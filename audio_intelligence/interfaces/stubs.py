"""Stub implementations that return demo data.

These can be used for local testing. Replace with real implementations
backed by Boson AI ASR, Qwen, Higgs Audio v3.5, and a reasoning LLM.
"""

from __future__ import annotations

from .base import (
    ASRProvider,
    ContentAnalysis,
    ContentAnalyzer,
    DimensionScore,
    DimensionVector,
    FusedAnalysisResult,
    MatchRecommendation,
    PreviewClip,
    PreviewGenerator,
    QuestionAnalysis,
    Recommender,
    TranscriptionResult,
    ReasoningEngine,
    VoiceBehavioralAnalysis,
    VoiceBehavioralAnalyzer,
    VibeProgressAnalyzer,
    VibeProgressResult,
)

_DIMENSION_NAMES = [
    "D1_emotional_openness",
    "D2_relational_security",
    "D3_conflict_style",
    "D4_energy_orientation",
    "D5_value_gravity",
    "D6_self_awareness",
]


def _stub_dimension_vector() -> DimensionVector:
    return DimensionVector(
        scores=[
            DimensionScore(dimension=name, score=0.5, confidence=0.3, reasoning="stub")
            for name in _DIMENSION_NAMES
        ]
    )


class StubASRProvider(ASRProvider):
    def transcribe(self, audio_url: str, language: str = "en") -> str:
        return "I think what makes a place feel like home is the people around you."


class StubContentAnalyzer(ContentAnalyzer):
    def analyze(self, question: str, transcript: str) -> ContentAnalysis:
        return ContentAnalysis(
            transcript=transcript,
            dimension_signals=[
                DimensionScore(dimension="D1_emotional_openness", score=0.72, confidence=0.6, reasoning="Rich emotional vocabulary"),
                DimensionScore(dimension="D2_relational_security", score=0.65, confidence=0.4, reasoning="References to people and belonging"),
            ],
            key_themes=["belonging", "warmth", "people-oriented"],
            linguistic_observations={
                "self_reference_density": "medium",
                "hedging_frequency": "low",
                "emotional_vocabulary_richness": "high",
                "reasoning_style": "concrete",
                "temporal_orientation": "present",
            },
        )


class StubVoiceBehavioralAnalyzer(VoiceBehavioralAnalyzer):
    def analyze(self, audio_url: str) -> VoiceBehavioralAnalysis:
        return VoiceBehavioralAnalysis(
            emotional_tone="warm, relaxed with subtle enthusiasm",
            speaking_energy="moderate pace, steady volume",
            fluency_patterns="minimal filled pauses, natural flow",
            voice_quality="warm timbre, steady pitch",
            engagement_level="invested and open",
            notable_shifts="slight warmth increase when discussing people",
            raw_text="The speaker sounds relaxed and genuinely warm.",
        )


class StubReasoningEngine(ReasoningEngine):
    def fuse_and_score(
        self,
        question: str,
        output1: ContentAnalysis,
        output2: VoiceBehavioralAnalysis,
        session_history: list[QuestionAnalysis],
        current_dimensions: DimensionVector | None,
    ) -> FusedAnalysisResult:
        return FusedAnalysisResult(
            updated_dimensions=_stub_dimension_vector(),
            next_question="Think of a time you disagreed with someone you care about. How did you handle it?",
            next_question_rationale="D3 (Conflict Style) remains the most uncertain dimension.",
            session_complete=len(session_history) >= 5,
            reasoning_trace="Stub reasoning — all dimensions set to 0.5 with low confidence.",
        )


class StubPreviewGenerator(PreviewGenerator):
    def generate_clip(self, user_id: str, max_duration_seconds: float = 5.0) -> PreviewClip:
        return PreviewClip(
            clip_url=f"https://cdn.example.com/previews/{user_id}/clip-5s.mp3",
            duration_seconds=min(max_duration_seconds, 5.0),
            source_prompt_ids=[0, 3],
        )


class StubRecommender(Recommender):
    def match_candidates(
        self,
        user_id: str,
        limit: int = 15,
        distance_km: int | None = None,
        intent: str | None = None,
    ) -> list[MatchRecommendation]:
        return [
            MatchRecommendation(
                candidate_id=f"user-{i+100}",
                resonance_score=round(0.85 - i * 0.02, 2),
                reason_tags=["calm-cadence", "high-empathy"],
            )
            for i in range(limit)
        ]

    def call_candidate(
        self,
        user_id: str,
        active_now_only: bool = True,
    ) -> MatchRecommendation | None:
        return MatchRecommendation(
            candidate_id="user-789",
            resonance_score=0.75,
            reason_tags=["warm-tone", "reflective"],
        )


class StubVibeProgressAnalyzer(VibeProgressAnalyzer):
    def analyze_thread(
        self,
        thread_id: str,
        since_last_analysis: bool = True,
    ) -> VibeProgressResult:
        return VibeProgressResult(
            resonance_score=0.67,
            vibe_stage="Warming",
            trend="rising",
            connection_insights="You two share a reflective communication style.",
            reasoning="Stub analysis — fixed demo values.",
        )

    def generate_vibe_report(self, user_id: str, window: str = "weekly") -> str:
        return "You resonate most with people who speak slowly and use abstract metaphors."
