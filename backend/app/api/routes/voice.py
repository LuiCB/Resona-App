import json
import logging
import os
import traceback

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.db.session import (
    get_completed_prompts,
    get_profile,
    get_user_dimensions,
    get_voice_analyses,
    save_voice_recording,
    upsert_profile,
)
from app.models.schemas import (
    LinguisticInsight,
    UserProfile,
    VocalBehaviorInsight,
    VoiceDimensionDetail,
    VoiceEvidenceItem,
    VoiceProfileResponse,
    VoicePrompt,
    VoicePromptsResponse,
    VoiceRecordingResult,
)
from app.services import voice_analysis

router = APIRouter()

# Fixed demo prompts — 6 curated questions for the hackathon demo.
DEMO_PROMPTS = [
    "Describe a place where you feel completely at ease.",
    "What kind of music do you turn to when you need to reset?",
    "What does emotional safety mean to you in a close relationship?",
    "What values guide your decisions?",
    "What kind of love feels healthiest to you?",
    "Describe the best conversation you've ever had — what made it so good?",
]

MAX_PROMPTS = 6

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")


def _build_prompt_list(user_id: str) -> list[str]:
    """Return the fixed 6 demo prompts."""
    return list(DEMO_PROMPTS)


@router.get("/voice/{user_id}/prompts", response_model=VoicePromptsResponse)
def list_prompts(user_id: str) -> VoicePromptsResponse:
    """FR-10 / Algorithm B.2: Get guided prompts with completion status.

    Q0–Q1 are fixed warmup prompts. Q2–Q5 are filled by the reasoning LLM's
    next_question output; placeholders are shown until then.
    """
    completed = set(get_completed_prompts(user_id))
    prompt_texts = _build_prompt_list(user_id)
    prompts = [
        VoicePrompt(prompt_id=i, text=text, completed=(i in completed))
        for i, text in enumerate(prompt_texts)
    ]
    return VoicePromptsResponse(
        user_id=user_id,
        prompts=prompts,
        completed_count=len(completed),
    )


@router.post("/voice/recording", response_model=VoiceRecordingResult)
async def save_recording(
    user_id: str = Form(...),
    prompt_id: int = Form(...),
    question_text: str = Form(""),
    audio_file: UploadFile = File(...),
) -> VoiceRecordingResult:
    """FR-09/10 / Algorithm B.4: Upload a voice recording and run the pipeline.

    Accepts multipart/form-data with fields:
      - user_id, prompt_id, question_text  (form fields)
      - audio_file                         (audio file, WAV or M4A)

    Runs the three-stage analysis pipeline synchronously and returns the
    next adaptive question (or session_complete=True).
    """
    profile = get_profile(user_id)
    if profile is None:
        # Auto-create a default profile so the demo flow works without
        # requiring the user to save their profile first.
        profile = upsert_profile(UserProfile(
            user_id=user_id, name="Demo User", age=25, gender="other",
            preference_gender="all", preference_age_min=18,
            preference_age_max=99, intent="long-term", location="",
            photo_count=0, voice_prompt_completed=0,
        ))
    if prompt_id < 0 or prompt_id >= MAX_PROMPTS:
        raise HTTPException(status_code=400, detail="Invalid prompt_id")

    # Resolve question text from pipeline-derived prompts if not provided
    if not question_text:
        question_text = _build_prompt_list(user_id)[prompt_id]

    # Save audio file to uploads/{user_id}/prompt_{prompt_id}.<ext>
    user_upload_dir = os.path.join(UPLOADS_DIR, user_id)
    os.makedirs(user_upload_dir, exist_ok=True)

    ext = os.path.splitext(audio_file.filename or "")[1] or ".m4a"
    audio_path = os.path.abspath(
        os.path.join(user_upload_dir, f"prompt_{prompt_id}{ext}")
    )
    contents = await audio_file.read()
    with open(audio_path, "wb") as f:
        f.write(contents)

    # Save recording metadata first (so completed count is updated)
    count = save_voice_recording(
        user_id, prompt_id, question_text=question_text, audio_url=audio_path
    )

    # Run pipeline
    try:
        analysis = voice_analysis.analyze_recording(
            user_id=user_id,
            prompt_id=prompt_id,
            question=question_text,
            audio_path=audio_path,
        )
    except Exception as exc:
        logging.error("Pipeline failed for user=%s prompt=%s: %s", user_id, prompt_id, traceback.format_exc())
        # Pipeline failure is non-fatal — recording is already saved
        return VoiceRecordingResult(
            user_id=user_id,
            prompt_id=prompt_id,
            status="saved_analysis_failed",
            completed_count=count,
            next_question=None,
            session_complete=False,
        )

    return VoiceRecordingResult(
        user_id=user_id,
        prompt_id=prompt_id,
        status="analyzed",
        completed_count=count,
        next_question=analysis["next_question"],
        session_complete=analysis["session_complete"],
    )


# --- Dimension label map ---
_DIM_LABELS = {
    "D1_emotional_openness":  ("Emotional Openness",  "Willingness to access and express inner emotional states"),
    "D2_relational_security": ("Relational Security", "Internal model of trust and comfort with intimacy"),
    "D3_conflict_style":      ("Conflict Style",      "How the person navigates disagreement and tension"),
    "D4_energy_orientation":  ("Energy Orientation",   "Degree of extraversion in social and romantic contexts"),
    "D5_value_gravity":       ("Value Gravity",        "Core life priorities — security/tradition vs. novelty/achievement"),
    "D6_self_awareness":      ("Self-Awareness",       "Capacity to reflect on one's own patterns and motivations"),
}

_DIM_ORDER = [
    "D1_emotional_openness", "D2_relational_security", "D3_conflict_style",
    "D4_energy_orientation", "D5_value_gravity", "D6_self_awareness",
]

_DIM_DB_PREFIX = {
    "D1_emotional_openness": "d1", "D2_relational_security": "d2",
    "D3_conflict_style": "d3", "D4_energy_orientation": "d4",
    "D5_value_gravity": "d5", "D6_self_awareness": "d6",
}


@router.get("/voice/{user_id}/profile", response_model=VoiceProfileResponse)
def get_voice_profile(user_id: str) -> VoiceProfileResponse:
    """Return the user's voice feature profile with dimension scores, evidence, and insights."""
    completed = get_completed_prompts(user_id)
    dims_row = get_user_dimensions(user_id)
    analyses = get_voice_analyses(user_id)

    # Aggregate data across all analyses
    evidence_per_dim: dict[str, list[VoiceEvidenceItem]] = {d: [] for d in _DIM_ORDER}
    all_themes: list[str] = []
    all_linguistic: list[dict] = []
    all_vocal_tones: list[str] = []
    all_vocal_energy: list[str] = []
    all_vocal_fluency: list[str] = []
    all_vocal_quality: list[str] = []
    all_vocal_engagement: list[str] = []
    all_reasoning_traces: list[str] = []

    for row in analyses:
        output1 = json.loads(row.get("output1_json") or "{}")
        output2 = json.loads(row.get("output2_json") or "{}")
        dim_snapshot = json.loads(row.get("dimension_snapshot_json") or "{}")

        item = VoiceEvidenceItem(
            prompt_id=row["prompt_id"],
            question=row["question_text"],
            transcript=row.get("transcript", "")[:300],
            key_themes=output1.get("key_themes", []),
            emotional_tone=output2.get("emotional_tone", "")[:200],
            reasoning=row.get("reasoning_trace", "")[:300],
        )

        # Collect themes
        all_themes.extend(output1.get("key_themes", []))

        # Collect linguistic observations
        ling = output1.get("linguistic_observations", {})
        if ling and not ling.get("raw_response"):
            all_linguistic.append(ling)

        # Collect vocal behavior data
        if output2.get("emotional_tone"):
            all_vocal_tones.append(output2["emotional_tone"][:150])
        if output2.get("speaking_energy"):
            all_vocal_energy.append(output2["speaking_energy"][:150])
        if output2.get("fluency_patterns"):
            all_vocal_fluency.append(output2["fluency_patterns"][:150])
        if output2.get("voice_quality"):
            all_vocal_quality.append(output2["voice_quality"][:150])
        if output2.get("engagement_level"):
            all_vocal_engagement.append(output2["engagement_level"][:150])

        # Collect reasoning
        if row.get("reasoning_trace"):
            all_reasoning_traces.append(row["reasoning_trace"][:500])

        # Map evidence to dimensions
        for ds in dim_snapshot.get("scores", []):
            dim_name = ds.get("dimension", "")
            if dim_name in evidence_per_dim and ds.get("confidence", 0) > 0:
                evidence_per_dim[dim_name].append(item)

    # Build dimension list
    dimensions = []
    for dim in _DIM_ORDER:
        label, description = _DIM_LABELS[dim]
        prefix = _DIM_DB_PREFIX[dim]
        score = 0.5
        confidence = 0.0
        if dims_row:
            score = dims_row.get(f"{prefix}_score", 0.5)
            confidence = dims_row.get(f"{prefix}_confidence", 0.0)
        dimensions.append(VoiceDimensionDetail(
            dimension=dim,
            label=label,
            score=score,
            confidence=confidence,
            description=description,
            evidence=evidence_per_dim[dim],
        ))

    # --- Aggregate linguistic insights ---
    linguistic_insights = []
    if all_linguistic:
        # Majority-vote across all analyses for each trait
        _LING_META = [
            ("self_reference_density", "Self-Reference", "person.fill", "How often you reference yourself — reveals self-focus vs. outward orientation"),
            ("hedging_frequency", "Hedging", "questionmark.circle", "Use of qualifiers like 'maybe', 'kind of' — indicates certainty vs. openness"),
            ("emotional_vocabulary_richness", "Emotional Vocabulary", "text.book.closed", "Range and depth of emotion words — signals emotional intelligence"),
            ("reasoning_style", "Reasoning Style", "brain.head.profile", "Whether you think in abstractions or concrete details"),
            ("temporal_orientation", "Temporal Focus", "clock.arrow.circlepath", "Whether your mind gravitates to past, present, or future"),
        ]
        for key, label, icon, detail in _LING_META:
            vals = [l.get(key, "") for l in all_linguistic if l.get(key)]
            if vals:
                from collections import Counter
                most_common = Counter(vals).most_common(1)[0][0]
                linguistic_insights.append(LinguisticInsight(
                    label=label, value=most_common, icon=icon, detail=detail,
                ))

    # --- Aggregate vocal behavior insights ---
    vocal_behavior = []
    if all_vocal_tones:
        vocal_behavior.append(VocalBehaviorInsight(
            label="Emotional Tone", value=all_vocal_tones[0], icon="waveform"))
    if all_vocal_energy:
        vocal_behavior.append(VocalBehaviorInsight(
            label="Speaking Energy", value=all_vocal_energy[0], icon="bolt.fill"))
    if all_vocal_fluency:
        vocal_behavior.append(VocalBehaviorInsight(
            label="Fluency Patterns", value=all_vocal_fluency[0], icon="water.waves"))
    if all_vocal_quality:
        vocal_behavior.append(VocalBehaviorInsight(
            label="Voice Quality", value=all_vocal_quality[0], icon="speaker.wave.3"))
    if all_vocal_engagement:
        vocal_behavior.append(VocalBehaviorInsight(
            label="Engagement Level", value=all_vocal_engagement[0], icon="chart.bar.fill"))

    # --- Deduplicate top themes ---
    seen = set()
    top_themes = []
    for t in all_themes:
        tl = t.lower().strip()
        if tl and tl not in seen:
            seen.add(tl)
            top_themes.append(t)
        if len(top_themes) >= 12:
            break

    # --- Generate personality narrative + voice identity label ---
    personality_narrative = ""
    voice_identity_label = ""
    if analyses:
        top = sorted(dimensions, key=lambda d: d.confidence, reverse=True)[:3]
        traits = ", ".join(f"{d.label} ({d.score:.0%})" for d in top)
        summary = f"Based on {len(analyses)} voice response(s), your strongest signals are: {traits}."

        # Build a personality narrative from the reasoning traces and dimension scores
        if all_reasoning_traces:
            narrative_parts = []
            for d in sorted(dimensions, key=lambda d: d.confidence, reverse=True):
                if d.confidence > 0:
                    level = "high" if d.score > 0.7 else "moderate" if d.score > 0.4 else "low"
                    narrative_parts.append(f"Your {d.label.lower()} registers as {level} ({d.score:.0%})")
            if narrative_parts:
                personality_narrative = ". ".join(narrative_parts[:4]) + "."
                # Append the first reasoning trace as deeper context
                personality_narrative += f"\n\n{all_reasoning_traces[0]}"

        # Generate voice identity archetype from top two dimensions
        _ARCHETYPES = {
            ("D1_emotional_openness", "D6_self_awareness"): "The Reflective Heart",
            ("D1_emotional_openness", "D4_energy_orientation"): "The Passionate Connector",
            ("D2_relational_security", "D6_self_awareness"): "The Grounded Thinker",
            ("D2_relational_security", "D1_emotional_openness"): "The Warm Harbor",
            ("D3_conflict_style", "D5_value_gravity"): "The Principled Negotiator",
            ("D4_energy_orientation", "D1_emotional_openness"): "The Vibrant Spirit",
            ("D5_value_gravity", "D6_self_awareness"): "The Deliberate Seeker",
            ("D6_self_awareness", "D1_emotional_openness"): "The Introspective Soul",
        }
        sorted_dims = sorted(dimensions, key=lambda d: d.score * d.confidence, reverse=True)
        if len(sorted_dims) >= 2:
            pair = (sorted_dims[0].dimension, sorted_dims[1].dimension)
            voice_identity_label = _ARCHETYPES.get(pair, "")
            if not voice_identity_label:
                # Fallback: try reverse pair
                voice_identity_label = _ARCHETYPES.get((pair[1], pair[0]), "")
            if not voice_identity_label:
                # Generic fallback based on top dimension
                _GENERIC = {
                    "D1_emotional_openness": "The Open Heart",
                    "D2_relational_security": "The Steady Anchor",
                    "D3_conflict_style": "The Balanced Navigator",
                    "D4_energy_orientation": "The Dynamic Presence",
                    "D5_value_gravity": "The Rooted Seeker",
                    "D6_self_awareness": "The Conscious Observer",
                }
                voice_identity_label = _GENERIC.get(sorted_dims[0].dimension, "Voice Explorer")
    else:
        summary = "No voice analysis data yet. Complete voice prompts to build your profile."

    return VoiceProfileResponse(
        user_id=user_id,
        completed_count=len(completed),
        dimensions=dimensions,
        summary=summary,
        personality_narrative=personality_narrative,
        linguistic_insights=linguistic_insights,
        vocal_behavior=vocal_behavior,
        top_themes=top_themes,
        voice_identity_label=voice_identity_label,
    )
