from fastapi import APIRouter, HTTPException

from app.db.session import get_profile, save_swipe
from app.models.schemas import MatchCandidate, SwipeAction, SwipeResult

router = APIRouter()

# FR-03: Demo candidates (15 profiles). In production, ask audio_intelligence.
_DEMO_CANDIDATES = [
    MatchCandidate(candidate_id="demo-1", display_name="Avery", age=27, gender="female", location="San Francisco", intent="long-term", bio="Music lover, sunset chaser", resonance_score=0.82),
    MatchCandidate(candidate_id="demo-2", display_name="Jordan", age=25, gender="non-binary", location="Oakland", intent="long-term", bio="Bookworm with a warm laugh", resonance_score=0.78),
    MatchCandidate(candidate_id="demo-3", display_name="Morgan", age=29, gender="female", location="San Jose", intent="short-term", bio="Trail runner, tea enthusiast", resonance_score=0.75),
    MatchCandidate(candidate_id="demo-4", display_name="Riley", age=24, gender="male", location="Berkeley", intent="friends", bio="Guitar player, deep thinker", resonance_score=0.71),
    MatchCandidate(candidate_id="demo-5", display_name="Casey", age=26, gender="female", location="Palo Alto", intent="long-term", bio="Quiet mornings, loud laughter", resonance_score=0.69),
    MatchCandidate(candidate_id="demo-6", display_name="Taylor", age=28, gender="non-binary", location="Mountain View", intent="long-term", bio="Podcast addict, dog parent", resonance_score=0.67),
    MatchCandidate(candidate_id="demo-7", display_name="Quinn", age=23, gender="female", location="Sunnyvale", intent="short-term", bio="Art student, night owl", resonance_score=0.65),
    MatchCandidate(candidate_id="demo-8", display_name="Drew", age=30, gender="male", location="San Mateo", intent="long-term", bio="Slow cook, fast reader", resonance_score=0.63),
    MatchCandidate(candidate_id="demo-9", display_name="Sage", age=27, gender="female", location="Daly City", intent="friends", bio="Yoga lover, journal keeper", resonance_score=0.61),
    MatchCandidate(candidate_id="demo-10", display_name="Elliot", age=26, gender="male", location="Redwood City", intent="long-term", bio="Stargazer, thoughtful texter", resonance_score=0.59),
    MatchCandidate(candidate_id="demo-11", display_name="Reese", age=25, gender="female", location="Fremont", intent="short-term", bio="Dance class regular, plant mom", resonance_score=0.57),
    MatchCandidate(candidate_id="demo-12", display_name="Finley", age=31, gender="male", location="Walnut Creek", intent="long-term", bio="History buff, morning person", resonance_score=0.55),
    MatchCandidate(candidate_id="demo-13", display_name="Rowan", age=22, gender="non-binary", location="Santa Clara", intent="friends", bio="Songwriter, hopeless romantic", resonance_score=0.53),
    MatchCandidate(candidate_id="demo-14", display_name="Blair", age=28, gender="female", location="Hayward", intent="long-term", bio="Film nerd, comfort food chef", resonance_score=0.51),
    MatchCandidate(candidate_id="demo-15", display_name="Skyler", age=24, gender="male", location="Cupertino", intent="short-term", bio="Skateboarder, sunset watcher", resonance_score=0.49),
]


@router.get("/match/{user_id}/candidates", response_model=list[MatchCandidate])
def get_match_candidates(user_id: str) -> list[MatchCandidate]:
    """FR-03: Return up to 15 candidates. Requires 2+ voice prompts (FR gate)."""
    profile = get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.voice_prompt_completed < 2:
        raise HTTPException(
            status_code=403,
            detail="Complete at least 2 Voice-Yourself prompts before matching",
        )
    return sorted(_DEMO_CANDIDATES, key=lambda c: c.resonance_score, reverse=True)


@router.post("/match/swipe", response_model=SwipeResult)
def swipe(action: SwipeAction) -> SwipeResult:
    """FR-04: Record a like/dislike swipe and detect mutual matches."""
    profile = get_profile(action.user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    mutual = save_swipe(action.user_id, action.target_id, action.action)
    return SwipeResult(
        user_id=action.user_id,
        target_id=action.target_id,
        action=action.action,
        mutual_match=mutual,
    )
