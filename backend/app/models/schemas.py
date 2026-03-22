from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "resona-backend"


class UserProfile(BaseModel):
    user_id: str
    name: str
    age: int = Field(ge=18, le=100)
    gender: str
    preference_gender: str
    preference_age_min: int = Field(ge=18, le=100)
    preference_age_max: int = Field(ge=18, le=100)
    intent: str
    location: str
    photo_count: int = Field(ge=0)
    voice_prompt_completed: int = Field(ge=0, le=6)
    interests: list[str] = Field(default_factory=list)


# --- Algorithm B.1: Dimension scores ---
class DimensionScoreItem(BaseModel):
    dimension: str
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    reasoning: str = ""


class UserDimensions(BaseModel):
    user_id: str
    dimensions: list[DimensionScoreItem] = Field(default_factory=list)  # len == 6
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --- Algorithm B.3: Voice analysis pipeline result ---
class VoiceAnalysisResult(BaseModel):
    user_id: str
    prompt_id: int
    question_text: str
    transcript: str = ""
    output1_json: str = "{}"   # Stage 1 content analysis (Qwen)
    output2_json: str = "{}"   # Stage 2 behavioral analysis (Higgs Audio)
    reasoning_trace: str = ""  # Stage 3 reasoning LLM trace
    dimension_snapshot: list[DimensionScoreItem] = Field(default_factory=list)
    next_question: str | None = None
    session_complete: bool = False
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class MatchCandidate(BaseModel):
    candidate_id: str
    display_name: str
    age: int
    gender: str = ""
    location: str
    intent: str = ""
    bio: str = ""
    voice_preview_url: str | None = None
    resonance_score: float = Field(ge=0, le=1)


class CallCandidate(BaseModel):
    candidate_id: str
    preview_url: str
    resonance_score: float = Field(ge=0, le=1)


class VibeReport(BaseModel):
    user_id: str
    period: str
    summary: str
    feature_highlights: list[str] = []
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InboxThread(BaseModel):
    thread_id: str
    peer_id: str
    peer_name: str
    last_message_type: str
    latest_voice_preview_url: str | None = None
    latest_transcript: str | None = None
    emotion_keywords: list[str] = []
    resonance_meter: float = Field(ge=0, le=1)
    latest_call_summary: str | None = None


class InboxThreadsResponse(BaseModel):
    user_id: str
    threads: list[InboxThread]


class ConnectionItem(BaseModel):
    connection_id: str
    display_name: str
    status: str
    voice_note_count: int = 0
    can_direct_call: bool = True


class ConnectionsResponse(BaseModel):
    user_id: str
    connections: list[ConnectionItem]


# --- FR-04: Swipe Actions ---
class SwipeAction(BaseModel):
    user_id: str
    target_id: str
    action: str = Field(pattern=r"^(like|dislike)$")


class SwipeResult(BaseModel):
    user_id: str
    target_id: str
    action: str
    mutual_match: bool = False


# --- FR-08: Call Actions ---
class CallAction(BaseModel):
    user_id: str
    candidate_id: str
    action: str = Field(pattern=r"^(accept|decline)$")


class CallSession(BaseModel):
    session_id: str
    user_id: str
    candidate_id: str
    status: str  # "connected" | "declined"
    preview_url: str | None = None


# --- FR-09/10: Voice Prompts ---
class VoicePrompt(BaseModel):
    prompt_id: int
    text: str
    completed: bool = False


class VoicePromptsResponse(BaseModel):
    user_id: str
    prompts: list[VoicePrompt]
    completed_count: int


class VoiceRecordingSubmission(BaseModel):
    user_id: str
    prompt_id: int
    question_text: str = ""
    audio_url: str = ""


class VoiceRecordingResult(BaseModel):
    user_id: str
    prompt_id: int
    status: str = "saved"
    completed_count: int
    next_question: str | None = None
    session_complete: bool = False


# --- Voice Profile: dimension visualization + evidence ---
class VoiceEvidenceItem(BaseModel):
    prompt_id: int
    question: str
    transcript: str = ""
    key_themes: list[str] = Field(default_factory=list)
    emotional_tone: str = ""
    reasoning: str = ""


class VoiceDimensionDetail(BaseModel):
    dimension: str         # e.g. "D1_emotional_openness"
    label: str             # e.g. "Emotional Openness"
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    description: str = ""
    evidence: list[VoiceEvidenceItem] = Field(default_factory=list)


class LinguisticInsight(BaseModel):
    label: str             # e.g. "Self-Reference Density"
    value: str             # e.g. "high"
    icon: str = ""         # SF Symbol name hint for iOS
    detail: str = ""       # Short explanation


class VocalBehaviorInsight(BaseModel):
    label: str             # e.g. "Emotional Tone"
    value: str             # e.g. "Calm, reflective"
    icon: str = ""


class VoiceProfileResponse(BaseModel):
    user_id: str
    completed_count: int
    dimensions: list[VoiceDimensionDetail] = Field(default_factory=list)
    summary: str = ""
    personality_narrative: str = ""          # LLM-generated prose about who they are
    linguistic_insights: list[LinguisticInsight] = Field(default_factory=list)
    vocal_behavior: list[VocalBehaviorInsight] = Field(default_factory=list)
    top_themes: list[str] = Field(default_factory=list)  # Aggregate key themes across all prompts
    voice_identity_label: str = ""          # Short archetype e.g. "The Reflective Explorer"


# --- FR-13/17: Messages ---
class MessageSend(BaseModel):
    sender_id: str
    thread_id: str
    message_type: str = Field(pattern=r"^(text|voice)$")
    content: str | None = None
    voice_url: str | None = None


class Message(BaseModel):
    message_id: str
    thread_id: str
    sender_id: str
    message_type: str
    content: str | None = None
    voice_url: str | None = None
    transcript: str | None = None
    emotion_keywords: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ThreadMessagesResponse(BaseModel):
    thread_id: str
    messages: list[Message]
