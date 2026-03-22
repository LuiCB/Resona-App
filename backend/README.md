# Backend (FastAPI)

This service owns identity, profile, messaging metadata, call metadata, and API orchestration for matching and voice analysis.

## Storage

- Current default: SQLite (`backend/resona.db`)
- User profile endpoints are persisted via sqlite3 (no longer in-memory)
- Replace `database_url` in `app/config.py` for Postgres in production

## Run locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API scope

- `POST /api/v1/users/profile` upsert onboarding/profile data
- `POST /api/v1/voice/analysis` receives processed audio features
- `GET /api/v1/match/{user_id}/candidates` asks recommender for discovery deck
- `GET /api/v1/call/{user_id}/candidate` asks recommender for call roulette
- `GET /api/v1/reports/{user_id}/vibe-check` returns weekly/monthly vibe summary

## Product rule enforced

- Match and Call candidate endpoints return `403` until `voice_prompt_completed >= 2`

Current route logic is intentionally stubbed so you can connect real DB + audio intelligence services incrementally.
