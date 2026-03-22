#!/bin/bash
# Restart the Resona backend server
source .env && export EIGENAI_API_KEY BOSON_AI_API_KEY
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1
cd ./backend
source .venv/bin/activate
PYTHONPATH=/Users/lui/Work/voice_dating/backend exec uvicorn app.main:app --host 0.0.0.0 --port 8000
