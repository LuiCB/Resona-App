import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.session import init_db
from app.api.routes import (
    health,
    users,
    voice,
    match,
    call,
    inbox,
    connections,
    reports,
)

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(users.router, prefix=settings.api_prefix, tags=["users"])
app.include_router(voice.router, prefix=settings.api_prefix, tags=["voice"])
app.include_router(match.router, prefix=settings.api_prefix, tags=["match"])
app.include_router(call.router, prefix=settings.api_prefix, tags=["call"])
app.include_router(inbox.router, prefix=settings.api_prefix, tags=["inbox"])
app.include_router(connections.router, prefix=settings.api_prefix, tags=["connections"])
app.include_router(reports.router, prefix=settings.api_prefix, tags=["reports"])
