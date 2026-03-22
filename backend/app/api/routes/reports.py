from fastapi import APIRouter

from app.models.schemas import VibeReport

router = APIRouter()


@router.get("/reports/{user_id}/vibe-check", response_model=VibeReport)
def get_vibe_check(user_id: str, period: str = "weekly") -> VibeReport:
    return VibeReport(
        user_id=user_id,
        period=period,
        summary="You resonate most with calm speakers who use reflective language.",
        feature_highlights=["slow-cadence", "metaphor-friendly", "low-interruption"],
    )
