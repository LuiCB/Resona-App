"""Abstract interfaces for the audio intelligence service.

These define the contracts that align with Algorithm B.3 (three-stage LLM
pipeline) and Algorithm D (Vibe Progress).  The backend calls these
interfaces; concrete implementations live in this module.

Pipeline overview (Algorithm B.3):
    Audio ──► [Stage 1] Boson AI ASR → transcript → Qwen → Output1
    Audio ──► [Stage 2] Boson AI Higgs Audio v3.5 → Output2
           ──► [Stage 3] Reasoning LLM (Output1 + Output2) → dimension scores
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes — aligned with Algorithm B.1 / B.3 / B.4
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    """Score + uncertainty for one of the six latent dimensions (D1–D6)."""
    dimension: str          # e.g. "D1_emotional_openness"
    score: float            # 0.0–1.0
    confidence: float       # 0.0–1.0
    reasoning: str = ""     # per-dimension reasoning trace


@dataclass
class DimensionVector:
    """Full six-dimension profile vector  v = [d1..d6, σ1..σ6]."""
    scores: list[DimensionScore] = field(default_factory=list)  # len == 6

    @property
    def values(self) -> list[float]:
        return [d.score for d in self.scores]

    @property
    def uncertainties(self) -> list[float]:
        return [1.0 - d.confidence for d in self.scores]


@dataclass
class ContentAnalysis:
    """Output1 — result of Stage 1 (ASR + Qwen content analysis)."""
    transcript: str
    dimension_signals: list[DimensionScore]
    key_themes: list[str] = field(default_factory=list)
    linguistic_observations: dict[str, str] = field(default_factory=dict)


@dataclass
class VoiceBehavioralAnalysis:
    """Output2 — result of Stage 2 (Higgs Audio behavioral analysis)."""
    emotional_tone: str
    speaking_energy: str
    fluency_patterns: str
    voice_quality: str
    engagement_level: str
    notable_shifts: str
    raw_text: str = ""


@dataclass
class FusedAnalysisResult:
    """Output of Stage 3 — Reasoning LLM fusion."""
    updated_dimensions: DimensionVector
    next_question: str | None = None   # None when session complete
    next_question_rationale: str = ""
    session_complete: bool = False
    reasoning_trace: str = ""


@dataclass
class QuestionAnalysis:
    """Full per-question analysis bundle (Algorithm B.4 storage)."""
    user_id: str
    prompt_id: int
    question_text: str
    audio_url: str
    transcript: str
    output1: ContentAnalysis
    output2: VoiceBehavioralAnalysis
    fused: FusedAnalysisResult
    dimension_snapshot: DimensionVector


# ---------------------------------------------------------------------------
# Data classes — Algorithm D (Vibe Progress)
# ---------------------------------------------------------------------------

@dataclass
class VibeProgressResult:
    """Output of Vibe Progress analysis (Algorithm D.2 Stage 3)."""
    resonance_score: float          # 0.0–1.0
    vibe_stage: str                 # Spark / Warming / Resonating / Soulmate Zone
    trend: str                      # rising / stable / cooling
    connection_insights: str        # personalized summary
    call_summary: str | None = None
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Shared data classes for matching / preview
# ---------------------------------------------------------------------------

@dataclass
class PreviewClip:
    clip_url: str
    duration_seconds: float
    source_prompt_ids: list[int]


@dataclass
class MatchRecommendation:
    candidate_id: str
    resonance_score: float
    reason_tags: list[str] = field(default_factory=list)


@dataclass
class TranscriptionResult:
    transcript: str
    emotion_keywords: list[str]
    confidence: float


# ---------------------------------------------------------------------------
# Stage 1: ASR + Content analysis  (Algorithm B.3 Stage 1)
# ---------------------------------------------------------------------------

class ASRProvider(ABC):
    """Speech-to-text via Boson AI ASR."""

    @abstractmethod
    def transcribe(self, audio_url: str, language: str = "en") -> str:
        """Return timestamped transcript text."""
        ...


class ContentAnalyzer(ABC):
    """Qwen-based semantic analysis of a transcript (Algorithm B.3 Stage 1b)."""

    @abstractmethod
    def analyze(
        self,
        question: str,
        transcript: str,
    ) -> ContentAnalysis:
        ...


# ---------------------------------------------------------------------------
# Stage 2: Voice behavioral analysis  (Algorithm B.3 Stage 2)
# ---------------------------------------------------------------------------

class VoiceBehavioralAnalyzer(ABC):
    """Boson AI Higgs Audio v3.5 — voice behavioral analysis."""

    @abstractmethod
    def analyze(self, audio_url: str) -> VoiceBehavioralAnalysis:
        ...


# ---------------------------------------------------------------------------
# Stage 3: Reasoning LLM — Fusion, scoring, question selection
# ---------------------------------------------------------------------------

class ReasoningEngine(ABC):
    """Reasoning LLM that fuses Output1 + Output2 (Algorithm B.3 Stage 3)."""

    @abstractmethod
    def fuse_and_score(
        self,
        question: str,
        output1: ContentAnalysis,
        output2: VoiceBehavioralAnalysis,
        session_history: list[QuestionAnalysis],
        current_dimensions: DimensionVector | None,
    ) -> FusedAnalysisResult:
        ...


# ---------------------------------------------------------------------------
# FR-07: Voice preview clip generation
# ---------------------------------------------------------------------------

class PreviewGenerator(ABC):
    """Generate a short vibe snippet from a user's recordings."""

    @abstractmethod
    def generate_clip(
        self,
        user_id: str,
        max_duration_seconds: float = 5.0,
    ) -> PreviewClip:
        ...


# ---------------------------------------------------------------------------
# FR-03/06: Recommendation engine  (Algorithm C)
# ---------------------------------------------------------------------------

class Recommender(ABC):
    """Produce ranked candidate lists for Match and Call modes."""

    @abstractmethod
    def match_candidates(
        self,
        user_id: str,
        limit: int = 15,
        distance_km: int | None = None,
        intent: str | None = None,
    ) -> list[MatchRecommendation]:
        ...

    @abstractmethod
    def call_candidate(
        self,
        user_id: str,
        active_now_only: bool = True,
    ) -> MatchRecommendation | None:
        ...


# ---------------------------------------------------------------------------
# Algorithm D: Vibe Progress analysis
# ---------------------------------------------------------------------------

class VibeProgressAnalyzer(ABC):
    """Analyze message/call history for a matched pair (Algorithm D.2)."""

    @abstractmethod
    def analyze_thread(
        self,
        thread_id: str,
        since_last_analysis: bool = True,
    ) -> VibeProgressResult:
        ...

    @abstractmethod
    def generate_vibe_report(
        self,
        user_id: str,
        window: str = "weekly",
    ) -> str:
        """Generate a Vibe Check Report across all active connections (D.4)."""
        ...
