import json

from fastapi import APIRouter, HTTPException

from app.db.session import get_thread_messages, save_message
from app.models.schemas import (
    InboxThread,
    InboxThreadsResponse,
    Message,
    MessageSend,
    ThreadMessagesResponse,
)

router = APIRouter()


@router.get("/inbox/{user_id}/threads", response_model=InboxThreadsResponse)
def list_threads(user_id: str) -> InboxThreadsResponse:
    """FR-13/16: List conversation threads with voice-first metadata."""
    return InboxThreadsResponse(
        user_id=user_id,
        threads=[
            InboxThread(
                thread_id="thr-1001",
                peer_id="user-456",
                peer_name="Avery",
                last_message_type="voice",
                latest_voice_preview_url="https://cdn.example.com/voice/avery-latest.m4a",
                latest_transcript="I liked how calmly you described your weekend.",
                emotion_keywords=["Reflective", "Curious"],
                resonance_meter=0.67,
                latest_call_summary="22 min call — Shared values: travel, emotional honesty.",
            ),
            InboxThread(
                thread_id="thr-1002",
                peer_id="user-789",
                peer_name="Jordan",
                last_message_type="text",
                latest_transcript="Hey, loved your vibe!",
                emotion_keywords=["Excited"],
                resonance_meter=0.42,
            ),
        ],
    )


@router.post("/inbox/messages", response_model=Message)
def send_message(payload: MessageSend) -> Message:
    """FR-17: Send a text or voice message in a thread."""
    message_id = save_message(
        thread_id=payload.thread_id,
        sender_id=payload.sender_id,
        message_type=payload.message_type,
        content=payload.content,
        voice_url=payload.voice_url,
    )
    return Message(
        message_id=message_id,
        thread_id=payload.thread_id,
        sender_id=payload.sender_id,
        message_type=payload.message_type,
        content=payload.content,
        voice_url=payload.voice_url,
    )


@router.get("/inbox/{thread_id}/messages", response_model=ThreadMessagesResponse)
def get_messages(thread_id: str) -> ThreadMessagesResponse:
    """FR-13: Get all messages in a thread."""
    rows = get_thread_messages(thread_id)
    messages = []
    for r in rows:
        keywords = []
        if r.get("emotion_keywords"):
            keywords = json.loads(r["emotion_keywords"])
        messages.append(
            Message(
                message_id=r["message_id"],
                thread_id=r["thread_id"],
                sender_id=r["sender_id"],
                message_type=r["message_type"],
                content=r.get("content"),
                voice_url=r.get("voice_url"),
                transcript=r.get("transcript"),
                emotion_keywords=keywords,
            )
        )
    return ThreadMessagesResponse(thread_id=thread_id, messages=messages)
