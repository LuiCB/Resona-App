"""Service layer: runs the audio intelligence pipeline and persists results."""
from __future__ import annotations

import json
import os
import sys

# Locate audio_intelligence relative to this file (backend/app/services/ → repo root)
_REPO_ROOT = os.path.dirname(  # voice_dating/
    os.path.dirname(  # backend/
        os.path.dirname(  # app/
            os.path.dirname(os.path.abspath(__file__))  # services/
        )
    )
)
_AI_LIB = os.path.join(_REPO_ROOT, "audio_intelligence", "lib")
_AI_ROOT = os.path.join(_REPO_ROOT, "audio_intelligence")

for _p in (_AI_LIB, _AI_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pipeline import run_session_question  # noqa: E402
from interfaces.base import (  # noqa: E402
    ContentAnalysis,
    DimensionScore,
    DimensionVector,
    FusedAnalysisResult,
    QuestionAnalysis,
    VoiceBehavioralAnalysis,
)

from app.db.session import (
    get_voice_analyses,
    save_voice_analysis,
    upsert_user_dimensions,
)

# Maps pipeline dimension names to flat DB column prefixes
_DIM_MAP = {
    "D1_emotional_openness": ("d1_score", "d1_confidence"),
    "D2_relational_security": ("d2_score", "d2_confidence"),
    "D3_conflict_style":      ("d3_score", "d3_confidence"),
    "D4_energy_orientation":  ("d4_score", "d4_confidence"),
    "D5_value_gravity":       ("d5_score", "d5_confidence"),
    "D6_self_awareness":      ("d6_score", "d6_confidence"),
}


def _reconstruct_session_history(rows: list[dict]) -> list[QuestionAnalysis]:
    """Rebuild minimal QuestionAnalysis objects from stored DB rows."""
    history: list[QuestionAnalysis] = []
    for row in rows:
        output1_data = json.loads(row.get("output1_json") or "{}")
        output2_data = json.loads(row.get("output2_json") or "{}")
        dim_data = json.loads(row.get("dimension_snapshot_json") or "{}")

        output1 = ContentAnalysis(
            transcript=row.get("transcript", ""),
            dimension_signals=[
                DimensionScore(
                    dimension=d["dimension"],
                    score=d.get("score", 0.5),
                    confidence=d.get("confidence", 0.3),
                    reasoning=d.get("reasoning", ""),
                )
                for d in output1_data.get("dimension_signals", [])
            ],
            key_themes=output1_data.get("key_themes", []),
            linguistic_observations=output1_data.get("linguistic_observations", {}),
        )

        output2 = VoiceBehavioralAnalysis(
            emotional_tone=output2_data.get("emotional_tone", ""),
            speaking_energy=output2_data.get("speaking_energy", ""),
            fluency_patterns=output2_data.get("fluency_patterns", ""),
            voice_quality=output2_data.get("voice_quality", ""),
            engagement_level=output2_data.get("engagement_level", ""),
            notable_shifts=output2_data.get("notable_shifts", ""),
            raw_text=output2_data.get("raw_text", ""),
        )

        dim_scores = [
            DimensionScore(
                dimension=d["dimension"],
                score=d.get("score", 0.5),
                confidence=d.get("confidence", 0.0),
                reasoning=d.get("reasoning", ""),
            )
            for d in dim_data.get("scores", [])
        ]
        dimension_snapshot = DimensionVector(scores=dim_scores)

        fused = FusedAnalysisResult(
            updated_dimensions=dimension_snapshot,
            next_question=row.get("next_question"),
            session_complete=bool(row.get("session_complete", False)),
            reasoning_trace=row.get("reasoning_trace", ""),
        )

        history.append(QuestionAnalysis(
            user_id=row["user_id"],
            prompt_id=row["prompt_id"],
            question_text=row["question_text"],
            audio_url=row["audio_url"],
            transcript=row["transcript"],
            output1=output1,
            output2=output2,
            fused=fused,
            dimension_snapshot=dimension_snapshot,
        ))
    return history


def analyze_recording(
    user_id: str,
    prompt_id: int,
    question: str,
    audio_path: str,
) -> dict:
    """Run the full three-stage pipeline on one recording and persist results.

    Returns a dict with: transcript, next_question, session_complete,
    dimension_snapshot (list of dicts).
    """
    prior_rows = get_voice_analyses(user_id)
    session_history = _reconstruct_session_history(prior_rows)

    result = run_session_question(
        audio_path=audio_path,
        question=question,
        session_history=session_history,
        user_id=user_id,
    )

    # Serialize for storage
    output1_dict = {
        "dimension_signals": [
            {"dimension": s.dimension, "score": s.score,
             "confidence": s.confidence, "reasoning": s.reasoning}
            for s in result.output1.dimension_signals
        ],
        "key_themes": result.output1.key_themes,
        "linguistic_observations": result.output1.linguistic_observations,
    }

    output2_dict = {
        "emotional_tone":  result.output2.emotional_tone,
        "speaking_energy": result.output2.speaking_energy,
        "fluency_patterns": result.output2.fluency_patterns,
        "voice_quality":   result.output2.voice_quality,
        "engagement_level": result.output2.engagement_level,
        "notable_shifts":  result.output2.notable_shifts,
        "raw_text":        result.output2.raw_text,
    }

    dim_snapshot_dict = {
        "scores": [
            {"dimension": s.dimension, "score": s.score,
             "confidence": s.confidence, "reasoning": s.reasoning}
            for s in result.dimension_snapshot.scores
        ]
    }

    save_voice_analysis(
        user_id=user_id,
        prompt_id=prompt_id,
        question_text=question,
        audio_url=audio_path,
        transcript=result.transcript,
        output1_json=json.dumps(output1_dict),
        output2_json=json.dumps(output2_dict),
        reasoning_trace=result.fused.reasoning_trace,
        dimension_snapshot_json=json.dumps(dim_snapshot_dict),
        next_question=result.fused.next_question,
        session_complete=result.fused.session_complete,
    )

    # Update flat user_dimensions table
    dim_flat: dict[str, float] = {}
    for s in result.dimension_snapshot.scores:
        keys = _DIM_MAP.get(s.dimension)
        if keys:
            dim_flat[keys[0]] = s.score
            dim_flat[keys[1]] = s.confidence
    upsert_user_dimensions(user_id, dim_flat)

    return {
        "transcript": result.transcript,
        "next_question": result.fused.next_question,
        "session_complete": result.fused.session_complete,
        "dimension_snapshot": dim_snapshot_dict["scores"],
    }
