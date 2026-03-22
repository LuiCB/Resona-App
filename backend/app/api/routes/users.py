from fastapi import APIRouter, HTTPException

from app.db.session import get_profile, upsert_profile
from app.models.schemas import UserProfile

router = APIRouter()


@router.post("/users/profile", response_model=UserProfile)
def upsert_profile_handler(profile: UserProfile) -> UserProfile:
    return upsert_profile(profile)


@router.get("/users/{user_id}/profile", response_model=UserProfile)
def get_profile_handler(user_id: str) -> UserProfile:
    profile = get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
