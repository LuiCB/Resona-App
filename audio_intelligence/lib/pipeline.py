"""Algorithm B.3 — Three-stage Voice-Yourself analysis pipeline.

Implements the concrete audio intelligence pipeline using:
  - core_api.ars_audio()              → Stage 1a (ASR)
  - core_api.speech_behavioral_analysis() → Stage 2 (Higgs Audio behavioral)
  - core_api.qwen_chat_completion()   → Stage 1b (content analysis) + Stage 3 (reasoning)

Processing flow per question (Algorithm B.4):
  1. Parallel: ASR transcription + Higgs Audio behavioral analysis
  2. Sequential: Qwen content analysis (needs transcript from step 1)
  3. Sequential: Reasoning LLM fusion (needs Output1 + Output2)
"""

from __future__ import annotations

import json
import re
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add lib directory to path so core_api and predict can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core_api

# Also make interfaces importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from interfaces.base import (
    ASRProvider,
    ContentAnalysis,
    ContentAnalyzer,
    DimensionScore,
    DimensionVector,
    FusedAnalysisResult,
    QuestionAnalysis,
    ReasoningEngine,
    VoiceBehavioralAnalysis,
    VoiceBehavioralAnalyzer,
)

# ---------------------------------------------------------------------------
# Psychology ontology — single source of truth (Algorithm B.1)
# ---------------------------------------------------------------------------

DIMENSION_DEFINITIONS = {
    "D1_emotional_openness": "Willingness to access and express inner emotional states",
    "D2_relational_security": "Internal model of trust and comfort with intimacy",
    "D3_conflict_style": "How the person navigates disagreement and tension",
    "D4_energy_orientation": "Degree of extraversion in social and romantic contexts",
    "D5_value_gravity": "Core life priorities (security/tradition vs. novelty/achievement)",
    "D6_self_awareness": "Capacity to reflect on one's own patterns and motivations",
}

DIMENSION_NAMES = list(DIMENSION_DEFINITIONS.keys())

ONTOLOGY_TEXT = "\n".join(
    f"- {name.split('_', 1)[0].upper()} {name.split('_', 1)[1].replace('_', ' ').title()}: {desc}"
    for name, desc in DIMENSION_DEFINITIONS.items()
)

# ---------------------------------------------------------------------------
# Adaptive prompt bank (Algorithm B.2)
# ---------------------------------------------------------------------------

WARMUP_PROMPTS = [
    "Describe a place where you feel completely at ease.",
    "What does a perfect slow morning look like for you?",
    "What kind of music do you turn to when you need to reset?",
    "What's a meal that feels like home?",
    "Tell me about something small that made you smile recently.",
    "What's a hobby or interest you'd love to share with someone?",
]

ADAPTIVE_PROMPT_BANK = [
    {"targets": "D2", "prompt": "What does emotional safety mean to you in a close relationship?"},
    {"targets": "D3", "prompt": "Think of a time you disagreed with someone you care about. How did you handle it?"},
    {"targets": "D2,D6", "prompt": "What's a pattern in your past relationships you've noticed about yourself?"},
    {"targets": "D5", "prompt": "If you could change one thing about how the world works, what would it be?"},
    {"targets": "D1,D4", "prompt": "Describe the best conversation you've ever had — what made it so good?"},
    {"targets": "D5,D6", "prompt": "What's something you used to believe about love that you've since changed your mind about?"},
    {"targets": "D3,D2", "prompt": "What does forgiveness look like to you?"},
]

CONFIDENCE_THRESHOLD = 0.15  # τ — session terminates when all σᵢ < τ
MAX_QUESTIONS = 6


# ---------------------------------------------------------------------------
# Stage 1a: ASR — uses core_api.ars_audio
# ---------------------------------------------------------------------------

class ASRProvider(ASRProvider):
    """Speech-to-text via Higgs Audio ASR (through core_api)."""

    def transcribe(self, audio_path: str, language: str = "en") -> str:
        return core_api.ars_audio(audio_path)


# ---------------------------------------------------------------------------
# Stage 1b: Content analysis — uses core_api.qwen_chat_completion
# ---------------------------------------------------------------------------

CONTENT_ANALYSIS_PROMPT = """You are analyzing a voice dating app response for psychological profiling.

Psychology ontology — six dimensions:
{ontology}

Question asked: "{question}"
Transcript: "{transcript}"

Analyze the content and produce a JSON object with this exact structure:
{{
  "dimensions": [
    {{
      "dimension": "D1_emotional_openness",
      "relevance": "high|medium|low|none",
      "score": 0.0-1.0,
      "confidence": 0.0-1.0,
      "evidence": "specific quotes or reasoning"
    }},
    ... (for all D1-D6)
  ],
  "key_themes": ["theme1", "theme2", "theme3"],
  "linguistic_observations": {{
    "self_reference_density": "high|medium|low",
    "hedging_frequency": "high|medium|low",
    "emotional_vocabulary_richness": "high|medium|low",
    "reasoning_style": "abstract|concrete|mixed",
    "temporal_orientation": "past|present|future|mixed"
  }}
}}

Output ONLY valid JSON, no other text."""


class EigenContentAnalyzer(ContentAnalyzer):
    """Qwen-based semantic analysis (Algorithm B.3 Stage 1b)."""

    def analyze(self, question: str, transcript: str) -> ContentAnalysis:
        prompt = CONTENT_ANALYSIS_PROMPT.format(
            ontology=ONTOLOGY_TEXT,
            question=question,
            transcript=transcript,
        )
        messages = [
            {"role": "system", "content": "You are a psychological analysis engine. Output only valid JSON."},
            {"role": "user", "content": prompt},
        ]
        raw = core_api.qwen_chat_completion(messages)
        return _parse_content_analysis(raw, transcript)


def _parse_content_analysis(raw: str, transcript: str) -> ContentAnalysis:
    """Parse Qwen JSON response into ContentAnalysis dataclass."""
    try:
        # Strip markdown code fences if present
        cleaned = re.sub(r"```json\s*", "", raw)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        data = json.loads(cleaned.strip())
    except json.JSONDecodeError:
        # Fallback: return raw text as-is with empty structured fields
        return ContentAnalysis(
            transcript=transcript,
            dimension_signals=[],
            key_themes=[],
            linguistic_observations={"raw_response": raw},
        )

    dimension_signals = []
    for d in data.get("dimensions", []):
        if d.get("relevance") in ("high", "medium"):
            dimension_signals.append(DimensionScore(
                dimension=d.get("dimension", ""),
                score=float(d.get("score", 0.5)),
                confidence=float(d.get("confidence", 0.3)),
                reasoning=d.get("evidence", ""),
            ))

    return ContentAnalysis(
        transcript=transcript,
        dimension_signals=dimension_signals,
        key_themes=data.get("key_themes", []),
        linguistic_observations=data.get("linguistic_observations", {}),
    )


# ---------------------------------------------------------------------------
# Stage 2: Voice behavioral analysis — uses core_api.speech_behavioral_analysis
# ---------------------------------------------------------------------------

class EigenVoiceBehavioralAnalyzer(VoiceBehavioralAnalyzer):
    """Higgs Audio v3.5 behavioral analysis (Algorithm B.3 Stage 2)."""

    def analyze(self, audio_path: str) -> VoiceBehavioralAnalysis:
        raw = core_api.speech_behavioral_analysis(audio_path)
        return _parse_behavioral_analysis(raw)


def _parse_behavioral_analysis(raw: str) -> VoiceBehavioralAnalysis:
    """Parse Higgs Audio text output into structured fields."""
    # The behavioral analysis is free-form text. We extract sections
    # by looking for the numbered items, or use the full text as fallback.
    text = raw.strip()
    return VoiceBehavioralAnalysis(
        emotional_tone=_extract_section(text, "emotional tone", "1."),
        speaking_energy=_extract_section(text, "speaking energy", "2."),
        fluency_patterns=_extract_section(text, "fluency", "3."),
        voice_quality=_extract_section(text, "voice quality", "4."),
        engagement_level=_extract_section(text, "engagement", "5."),
        notable_shifts=_extract_section(text, "notable shift", "6."),
        raw_text=text,
    )


def _extract_section(text: str, keyword: str, num_prefix: str) -> str:
    """Best-effort extraction of a section from free-form text."""
    import re
    lower = text.lower()

    # Strategy 1: Find "N. Keyword:" pattern (e.g. "1. Emotional Tone:")
    pattern = re.escape(num_prefix) + r"\s*" + re.escape(keyword) + r"[^:]*:\s*(.*)"
    m = re.search(pattern, lower)
    if m:
        start = m.start()
        rest = text[start:]
        lines = rest.split("\n")
        section_lines = [lines[0]]
        for line in lines[1:]:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and "." in stripped[:3]:
                break
            section_lines.append(line)
        # Remove the "N. Label:" prefix from the result
        result = "\n".join(section_lines).strip()
        colon_idx = result.find(":")
        if colon_idx != -1:
            result = result[colon_idx + 1:].strip()
        return result

    # Strategy 2: Find keyword anywhere as a heading/label
    idx = lower.find(keyword)
    if idx != -1:
        rest = text[idx:]
        lines = rest.split("\n")
        section_lines = [lines[0]]
        for line in lines[1:]:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and "." in stripped[:3]:
                break
            section_lines.append(line)
        result = "\n".join(section_lines).strip()
        colon_idx = result.find(":")
        if colon_idx != -1 and colon_idx < 40:
            result = result[colon_idx + 1:].strip()
        return result

    # Strategy 3: Try numbered prefix alone
    idx = lower.find(num_prefix)
    if idx != -1:
        rest = text[idx:]
        lines = rest.split("\n")
        section_lines = [lines[0]]
        for line in lines[1:]:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and "." in stripped[:3]:
                break
            section_lines.append(line)
        result = "\n".join(section_lines).strip()
        colon_idx = result.find(":")
        if colon_idx != -1 and colon_idx < 40:
            result = result[colon_idx + 1:].strip()
        return result

    return ""


# ---------------------------------------------------------------------------
# Stage 3: Reasoning LLM — Fusion + scoring + question selection
# ---------------------------------------------------------------------------

REASONING_PROMPT = """You are the Voice-Yourself reasoning engine for a dating app.

## Psychology Ontology
{ontology}

## Session State
Questions asked so far:
{session_history}

Current dimension estimates:
{current_dimensions}

## Current Question Analysis
- Question: "{question}"
- Output1 (content analysis): {output1}
- Output2 (voice behavioral analysis): {output2}

## Adaptive Prompt Bank
{prompt_bank}

## Tasks
Produce a JSON object with this exact structure:
{{
  "dimensions": [
    {{
      "dimension": "D1_emotional_openness",
      "updated_score": 0.0-1.0,
      "updated_confidence": 0.0-1.0,
      "reasoning": "how content and vocal evidence were weighed"
    }},
    ... (for all D1-D6)
  ],
  "session_complete": true/false,
  "next_question": "the next question text or null if session complete",
  "next_question_rationale": "which dimensions it targets and why",
  "reasoning_trace": "overall reasoning summary"
}}

Rules for next question selection:
- Identify the 2 most uncertain dimensions (lowest confidence).
- Select from the REMAINING prompt bank options (already-used prompts have been removed) or generate a completely novel question targeting those dimensions.
- CRITICAL: The next_question MUST be substantially different from ALL questions listed in "Questions asked so far". Do NOT rephrase, paraphrase, or ask a thematically similar version of any prior question. If in doubt, generate a novel question instead.
- No leading questions, no yes/no questions, must be trauma-aware.
- Session ends if: 6 questions answered OR all dimension confidences > 0.85.

Output ONLY valid JSON."""


class EigenReasoningEngine(ReasoningEngine):
    """Reasoning LLM that fuses Output1 + Output2 (Algorithm B.3 Stage 3)."""

    def fuse_and_score(
        self,
        question: str,
        output1: ContentAnalysis,
        output2: VoiceBehavioralAnalysis,
        session_history: list[QuestionAnalysis],
        current_dimensions: DimensionVector | None,
    ) -> FusedAnalysisResult:
        # Format session history
        if session_history:
            history_text = "\n".join(
                f"  Q{i+1}: \"{h.question_text}\"\n"
                f"    Transcript: \"{h.transcript[:200]}...\"\n"
                f"    Content themes: {h.output1.key_themes}\n"
                f"    Vocal tone: {h.output2.emotional_tone[:100]}"
                for i, h in enumerate(session_history)
            )
        else:
            history_text = "  (no prior questions)"

        # Format current dimensions
        if current_dimensions and current_dimensions.scores:
            dims_text = "\n".join(
                f"  {s.dimension}: score={s.score:.2f}, confidence={s.confidence:.2f}"
                for s in current_dimensions.scores
            )
        else:
            dims_text = "  (no estimates yet — this is the first question)"

        # Format Output1
        output1_text = json.dumps({
            "transcript": output1.transcript,
            "dimension_signals": [
                {"dim": s.dimension, "score": s.score, "confidence": s.confidence, "evidence": s.reasoning}
                for s in output1.dimension_signals
            ],
            "key_themes": output1.key_themes,
            "linguistic_observations": output1.linguistic_observations,
        }, indent=2)

        # Format Output2
        output2_text = output2.raw_text if output2.raw_text else json.dumps({
            "emotional_tone": output2.emotional_tone,
            "speaking_energy": output2.speaking_energy,
            "fluency_patterns": output2.fluency_patterns,
            "voice_quality": output2.voice_quality,
            "engagement_level": output2.engagement_level,
            "notable_shifts": output2.notable_shifts,
        }, indent=2)

        # Format prompt bank — exclude questions already asked
        asked_questions = {q.lower().strip() for q in (
            [h.question_text for h in session_history] + [question]
        )}
        remaining_prompts = [
            p for p in ADAPTIVE_PROMPT_BANK
            if p["prompt"].lower().strip() not in asked_questions
        ]
        if remaining_prompts:
            bank_text = "\n".join(
                f"  [{p['targets']}] \"{p['prompt']}\""
                for p in remaining_prompts
            )
        else:
            bank_text = "  (all prompt bank items used — generate a novel question)"

        prompt = REASONING_PROMPT.format(
            ontology=ONTOLOGY_TEXT,
            session_history=history_text,
            current_dimensions=dims_text,
            question=question,
            output1=output1_text,
            output2=output2_text,
            prompt_bank=bank_text,
        )

        messages = [
            {"role": "system", "content": "You are a psychological reasoning engine. Output only valid JSON."},
            {"role": "user", "content": prompt},
        ]
        raw = core_api.qwen_chat_completion(messages)
        return _parse_reasoning_result(raw)


def _parse_reasoning_result(raw: str) -> FusedAnalysisResult:
    """Parse reasoning LLM JSON into FusedAnalysisResult."""
    try:
        cleaned = re.sub(r"```json\s*", "", raw)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        # Also strip any <think>...</think> blocks from Qwen thinking mode
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL)
        cleaned = cleaned.strip()
        # Extract the JSON object even if there's trailing text
        brace_start = cleaned.find("{")
        if brace_start >= 0:
            depth = 0
            in_string = False
            escape_next = False
            for i in range(brace_start, len(cleaned)):
                c = cleaned[i]
                if escape_next:
                    escape_next = False
                    continue
                if c == "\\":
                    escape_next = True
                    continue
                if c == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if not in_string:
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            cleaned = cleaned[brace_start:i+1]
                            break
        # Fix unescaped newlines inside JSON string values
        # (LLMs sometimes output literal newlines in string fields)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Escape literal newlines/tabs inside JSON string values
            fixed = []
            in_str = False
            esc = False
            for ch in cleaned:
                if esc:
                    fixed.append(ch)
                    esc = False
                    continue
                if ch == '\\':
                    fixed.append(ch)
                    esc = True
                    continue
                if ch == '"':
                    in_str = not in_str
                    fixed.append(ch)
                    continue
                if in_str and ch == '\n':
                    fixed.append('\\n')
                elif in_str and ch == '\r':
                    fixed.append('\\r')
                elif in_str and ch == '\t':
                    fixed.append('\\t')
                else:
                    fixed.append(ch)
            data = json.loads("".join(fixed))
    except json.JSONDecodeError as e:
        import logging
        logging.error("JSON parse failed: %s\nRaw (first 1000 chars): %s", e, raw[:1000])
        # Fallback with default scores
        return FusedAnalysisResult(
            updated_dimensions=_default_dimension_vector(),
            reasoning_trace=f"Failed to parse reasoning output: {raw[:500]}",
        )

    scores = []
    for d in data.get("dimensions", []):
        scores.append(DimensionScore(
            dimension=d.get("dimension", ""),
            score=float(d.get("updated_score", 0.5)),
            confidence=float(d.get("updated_confidence", 0.3)),
            reasoning=d.get("reasoning", ""),
        ))

    # Ensure all 6 dimensions are present
    found = {s.dimension for s in scores}
    for name in DIMENSION_NAMES:
        if name not in found:
            scores.append(DimensionScore(dimension=name, score=0.5, confidence=0.0, reasoning="No signal"))

    # Sort by dimension order
    dim_order = {name: i for i, name in enumerate(DIMENSION_NAMES)}
    scores.sort(key=lambda s: dim_order.get(s.dimension, 99))

    return FusedAnalysisResult(
        updated_dimensions=DimensionVector(scores=scores),
        next_question=data.get("next_question"),
        next_question_rationale=data.get("next_question_rationale", ""),
        session_complete=data.get("session_complete", False),
        reasoning_trace=data.get("reasoning_trace", ""),
    )


def _default_dimension_vector() -> DimensionVector:
    return DimensionVector(scores=[
        DimensionScore(dimension=name, score=0.5, confidence=0.0, reasoning="default")
        for name in DIMENSION_NAMES
    ])


# ---------------------------------------------------------------------------
# Full pipeline orchestrator (Algorithm B.4)
# ---------------------------------------------------------------------------

def analyze_voice_response(
    audio_path: str,
    question: str,
    session_history: list[QuestionAnalysis] | None = None,
    current_dimensions: DimensionVector | None = None,
    prompt_id: int = 0,
    user_id: str = "",
) -> QuestionAnalysis:
    """Run the full three-stage pipeline on one voice recording.

    Algorithm B.4 processing flow:
      1. Parallel: ASR (→ transcript) + Higgs Audio (→ Output2)
      2. Sequential: Qwen content analysis (transcript → Output1)
      3. Sequential: Reasoning LLM (Output1 + Output2 → fused result)

    Args:
        audio_path: Path to the audio file (WAV/M4A).
        question: The question the user was answering.
        session_history: Prior QuestionAnalysis objects for this session.
        current_dimensions: Current D1–D6 estimates (None for first question).
        prompt_id: Index of this prompt in the session.
        user_id: User identifier.

    Returns:
        QuestionAnalysis with all stage outputs and updated dimensions.
    """
    if session_history is None:
        session_history = []

    asr = ASRProvider()
    content_analyzer = EigenContentAnalyzer()
    behavioral_analyzer = EigenVoiceBehavioralAnalyzer()
    reasoning = EigenReasoningEngine()

    # ── Steps 1 & 2: Parallel ASR + behavioral analysis ──────────────
    transcript = None
    output2 = None

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_asr = executor.submit(asr.transcribe, audio_path)
        future_behavioral = executor.submit(behavioral_analyzer.analyze, audio_path)

        transcript = future_asr.result()
        output2 = future_behavioral.result()

    # For simplicity in this example, we'll run them sequentially
    # transcript = asr.transcribe(audio_path)
    # output2 = behavioral_analyzer.analyze(audio_path)

    # ── Step 3: Content analysis (depends on transcript) ─────────────
    output1 = content_analyzer.analyze(question, transcript)

    # ── Step 4: Reasoning LLM fusion ─────────────────────────────────
    fused = reasoning.fuse_and_score(
        question=question,
        output1=output1,
        output2=output2,
        session_history=session_history,
        current_dimensions=current_dimensions,
    )

    return QuestionAnalysis(
        user_id=user_id,
        prompt_id=prompt_id,
        question_text=question,
        audio_url=audio_path,
        transcript=transcript,
        output1=output1,
        output2=output2,
        fused=fused,
        dimension_snapshot=fused.updated_dimensions,
    )


def run_session_question(
    audio_path: str,
    question: str,
    session_history: list[QuestionAnalysis],
    user_id: str = "",
) -> QuestionAnalysis:
    """Convenience function: analyze one question with auto-derived state.

    Derives current_dimensions and prompt_id from session_history automatically.
    """
    current_dims = None
    if session_history:
        current_dims = session_history[-1].dimension_snapshot

    prompt_id = len(session_history)

    return analyze_voice_response(
        audio_path=audio_path,
        question=question,
        session_history=session_history,
        current_dimensions=current_dims,
        prompt_id=prompt_id,
        user_id=user_id,
    )


# ---------------------------------------------------------------------------
# CLI for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Voice-Yourself pipeline on an audio file")
    parser.add_argument("audio_file", help="Path to audio file (WAV/M4A)")
    parser.add_argument("--question", default=WARMUP_PROMPTS[0], help="Question that was asked")
    parser.add_argument("--user-id", default="test-user", help="User ID")
    args = parser.parse_args()

    print(f"=== Voice-Yourself Pipeline ===")
    print(f"Audio: {args.audio_file}")
    print(f"Question: {args.question}")
    print()

    result = analyze_voice_response(
        audio_path=args.audio_file,
        question=args.question,
        user_id=args.user_id,
    )

    print(f"\n=== Results ===")
    print(f"Transcript: {result.transcript}")
    print(f"\nContent themes: {result.output1.key_themes}")
    print(f"Vocal tone: {result.output2.emotional_tone}")
    print(f"\nDimension scores:")
    for d in result.fused.updated_dimensions.scores:
        print(f"  {d.dimension}: {d.score:.2f} (confidence: {d.confidence:.2f})")
        print(f"    {d.reasoning}")
    print(f"\nSession complete: {result.fused.session_complete}")
    print(f"Next question: {result.fused.next_question}")
    print(f"Rationale: {result.fused.next_question_rationale}")