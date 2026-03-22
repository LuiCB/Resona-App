import uuid

from fastapi import APIRouter, HTTPException

from app.db.session import get_profile
from app.models.schemas import CallAction, CallCandidate, CallSession

router = APIRouter()


@router.get("/call/{user_id}/candidate", response_model=CallCandidate)
def get_live_call_candidate(user_id: str) -> CallCandidate:
    """FR-06/07: Find a live call candidate with voice preview."""
    profile = get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.voice_prompt_completed < 2:
        raise HTTPException(
            status_code=403,
            detail="Complete at least 2 Voice-Yourself prompts before call mode",
        )
    return CallCandidate(
        candidate_id="live-1",
        preview_url="https://cdn.example.com/previews/live-1.mp3",
        resonance_score=0.74,
    )


@router.post("/call/action", response_model=CallSession)
def call_action(action: CallAction) -> CallSession:
    """FR-08: Accept or decline a call based on voice preview."""
    profile = get_profile(action.user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    session_id = f"call-{uuid.uuid4().hex[:8]}"
    status = "connected" if action.action == "accept" else "declined"
    return CallSession(
        session_id=session_id,
        user_id=action.user_id,
        candidate_id=action.candidate_id,
        status=status,
        preview_url="https://cdn.example.com/previews/live-1.mp3" if status == "connected" else None,
    )
