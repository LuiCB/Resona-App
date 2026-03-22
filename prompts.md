# Pipeline Prompts Summary

This document summarizes the prompts used in the `pipeline.py` file for the Voice-Yourself analysis pipeline.

## Prompts

### 0. Voice Behavioral Analysis

The Voice-Yourself pipeline uses a six-dimension psychological ontology to analyze user responses. These dimensions are:

- **D1 Emotional Openness**: Willingness to access and express inner emotional states.
- **D2 Relational Security**: Internal model of trust and comfort with intimacy.
- **D3 Conflict Style**: How the person navigates disagreement and tension.
- **D4 Energy Orientation**: Degree of extraversion in social and romantic contexts.
- **D5 Value Gravity**: Core life priorities (security/tradition vs. novelty/achievement).
- **D6 Self-Awareness**: Capacity to reflect on one's own patterns and motivations.

This ontology serves as the foundation for analyzing voice responses and generating psychological profiles.

**Prompt:**
```python
user_text=(
    "Analyze the speaker's vocal behavior and output EXACTLY this numbered format:\n"
    "1. Emotional Tone: <describe the speaker's emotional state and tone>\n"
    "2. Speaking Energy: <describe pace, volume, and energy level>\n"
    "3. Fluency Patterns: <describe hesitations, filler words, flow>\n"
    "4. Voice Quality: <describe pitch, warmth, resonance>\n"
    "5. Engagement Level: <describe how engaged or invested the speaker sounds>\n"
    "6. Notable Shifts: <describe any changes in tone, pace, or energy during the recording>\n"
    "Output in English."
)
```


### 1. **Content Analysis Prompt**
**Purpose:** Analyze the transcript of a voice response to extract psychological dimensions, key themes, and linguistic observations.

**Prompt:**
```plaintext
You are analyzing a voice dating app response for psychological profiling.

Psychology ontology — six dimensions:
{ontology}

Question asked: "{question}"
Transcript: "{transcript}"

Analyze the content and produce a JSON object with this exact structure:
{
  "dimensions": [
    {
      "dimension": "D1_emotional_openness",
      "relevance": "high|medium|low|none",
      "score": 0.0-1.0,
      "confidence": 0.0-1.0,
      "evidence": "specific quotes or reasoning"
    },
    ... (for all D1-D6)
  ],
  "key_themes": ["theme1", "theme2", "theme3"],
  "linguistic_observations": {
    "self_reference_density": "high|medium|low",
    "hedging_frequency": "high|medium|low",
    "emotional_vocabulary_richness": "high|medium|low",
    "reasoning_style": "abstract|concrete|mixed",
    "temporal_orientation": "past|present|future|mixed"
  }
}

Output ONLY valid JSON, no other text.
```

### 2. **Reasoning Prompt**
**Purpose:** Fuse the outputs of content analysis and voice behavioral analysis to update psychological dimensions, determine session completion, and select the next question.

**Prompt:**
```plaintext
You are the Voice-Yourself reasoning engine for a dating app.

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
{
  "dimensions": [
    {
      "dimension": "D1_emotional_openness",
      "updated_score": 0.0-1.0,
      "updated_confidence": 0.0-1.0,
      "reasoning": "how content and vocal evidence were weighed"
    },
    ... (for all D1-D6)
  ],
  "session_complete": true/false,
  "next_question": "the next question text or null if session complete",
  "next_question_rationale": "which dimensions it targets and why",
  "reasoning_trace": "overall reasoning summary"
}

Rules for next question selection:
- Identify the 2 most uncertain dimensions (lowest confidence).
- Select from the REMAINING prompt bank options (already-used prompts have been removed) or generate a completely novel question targeting those dimensions.
- CRITICAL: The next_question MUST be substantially different from ALL questions listed in "Questions asked so far". Do NOT rephrase, paraphrase, or ask a thematically similar version of any prior question. If in doubt, generate a novel question instead.
- No leading questions, no yes/no questions, must be trauma-aware.
- Session ends if: 6 questions answered OR all dimension confidences > 0.85.

Output ONLY valid JSON.
```


## Model Used

The pipeline leverages the following AI models:

1. **Boson AI ARS**: For speech-to-text transcription and vocal behavior analysis.
2. **Eigen AI GPT-OSS 120B**: A reasoning and content analysis model used for semantic understanding and adaptive questioning.

These models work together to extract insights from both the content and delivery of user responses, enabling a comprehensive analysis of psychological dimensions.

