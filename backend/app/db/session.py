import json
import sqlite3
import uuid

from app.config import settings
from app.models.schemas import UserProfile


def _db_path() -> str:
    return settings.database_url.replace("sqlite:///", "", 1)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            preference_gender TEXT NOT NULL,
            preference_age_min INTEGER NOT NULL,
            preference_age_max INTEGER NOT NULL,
            intent TEXT NOT NULL,
            location TEXT NOT NULL,
            photo_count INTEGER NOT NULL,
            voice_prompt_completed INTEGER NOT NULL,
            interests TEXT NOT NULL DEFAULT '[]'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS voice_recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            prompt_id INTEGER NOT NULL,
            question_text TEXT NOT NULL DEFAULT '',
            audio_url TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, prompt_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS swipe_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, target_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            thread_id TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            message_type TEXT NOT NULL,
            content TEXT,
            voice_url TEXT,
            transcript TEXT,
            emotion_keywords TEXT DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    # Algorithm B.3/B.4: per-question voice analysis results
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS voice_analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            prompt_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            audio_url TEXT NOT NULL,
            transcript TEXT NOT NULL DEFAULT '',
            output1_json TEXT NOT NULL DEFAULT '{}',
            output2_json TEXT NOT NULL DEFAULT '{}',
            reasoning_trace TEXT NOT NULL DEFAULT '',
            dimension_snapshot_json TEXT NOT NULL DEFAULT '{}',
            next_question TEXT DEFAULT NULL,
            session_complete INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, prompt_id)
        )
        """
    )
    # Algorithm B.1: current user dimension scores (D1–D6 with uncertainties)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_dimensions (
            user_id TEXT PRIMARY KEY,
            d1_score REAL NOT NULL DEFAULT 0.5,
            d1_confidence REAL NOT NULL DEFAULT 0.0,
            d2_score REAL NOT NULL DEFAULT 0.5,
            d2_confidence REAL NOT NULL DEFAULT 0.0,
            d3_score REAL NOT NULL DEFAULT 0.5,
            d3_confidence REAL NOT NULL DEFAULT 0.0,
            d4_score REAL NOT NULL DEFAULT 0.5,
            d4_confidence REAL NOT NULL DEFAULT 0.0,
            d5_score REAL NOT NULL DEFAULT 0.5,
            d5_confidence REAL NOT NULL DEFAULT 0.0,
            d6_score REAL NOT NULL DEFAULT 0.5,
            d6_confidence REAL NOT NULL DEFAULT 0.0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    # Algorithm D.6: per-thread vibe progress state
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vibe_progress (
            thread_id TEXT PRIMARY KEY,
            user_a_id TEXT NOT NULL,
            user_b_id TEXT NOT NULL,
            resonance_score REAL NOT NULL DEFAULT 0.0,
            vibe_stage TEXT NOT NULL DEFAULT 'Spark',
            trend TEXT NOT NULL DEFAULT 'stable',
            insights_json TEXT NOT NULL DEFAULT '{}',
            call_summaries_json TEXT NOT NULL DEFAULT '[]',
            last_analysis_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()


def upsert_profile(profile: UserProfile) -> UserProfile:
    conn = _connect()
    interests_json = json.dumps(profile.interests) if profile.interests else "[]"
    conn.execute(
        """
        INSERT INTO user_profiles (
            user_id, name, age, gender, preference_gender,
            preference_age_min, preference_age_max, intent,
            location, photo_count, voice_prompt_completed, interests
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            age=excluded.age,
            gender=excluded.gender,
            preference_gender=excluded.preference_gender,
            preference_age_min=excluded.preference_age_min,
            preference_age_max=excluded.preference_age_max,
            intent=excluded.intent,
            location=excluded.location,
            photo_count=excluded.photo_count,
            voice_prompt_completed=excluded.voice_prompt_completed,
            interests=excluded.interests
        """,
        (
            profile.user_id,
            profile.name,
            profile.age,
            profile.gender,
            profile.preference_gender,
            profile.preference_age_min,
            profile.preference_age_max,
            profile.intent,
            profile.location,
            profile.photo_count,
            profile.voice_prompt_completed,
            interests_json,
        ),
    )
    conn.commit()
    conn.close()
    return profile


def get_profile(user_id: str) -> UserProfile | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM user_profiles WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    data = dict(row)
    if isinstance(data.get("interests"), str):
        data["interests"] = json.loads(data["interests"])
    return UserProfile(**data)


# --- Voice recordings ---

def get_completed_prompts(user_id: str) -> list[int]:
    conn = _connect()
    rows = conn.execute(
        "SELECT prompt_id FROM voice_recordings WHERE user_id = ? ORDER BY prompt_id",
        (user_id,),
    ).fetchall()
    conn.close()
    return [r["prompt_id"] for r in rows]


def save_voice_recording(user_id: str, prompt_id: int, question_text: str = "", audio_url: str = "") -> int:
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO voice_recordings (user_id, prompt_id, question_text, audio_url) VALUES (?, ?, ?, ?)",
        (user_id, prompt_id, question_text, audio_url),
    )
    # Also update the user profile's completed count
    count = conn.execute(
        "SELECT COUNT(*) as cnt FROM voice_recordings WHERE user_id = ?",
        (user_id,),
    ).fetchone()["cnt"]
    conn.execute(
        "UPDATE user_profiles SET voice_prompt_completed = ? WHERE user_id = ?",
        (count, user_id),
    )
    conn.commit()
    conn.close()
    return count


# --- Swipe actions ---

def save_swipe(user_id: str, target_id: str, action: str) -> bool:
    conn = _connect()
    conn.execute(
        """
        INSERT INTO swipe_actions (user_id, target_id, action)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, target_id) DO UPDATE SET action=excluded.action
        """,
        (user_id, target_id, action),
    )
    # Check for mutual match
    mutual = False
    if action == "like":
        row = conn.execute(
            "SELECT 1 FROM swipe_actions WHERE user_id = ? AND target_id = ? AND action = 'like'",
            (target_id, user_id),
        ).fetchone()
        mutual = row is not None
    conn.commit()
    conn.close()
    return mutual


# --- Messages ---

def save_message(
    thread_id: str,
    sender_id: str,
    message_type: str,
    content: str | None,
    voice_url: str | None,
) -> str:
    message_id = f"msg-{uuid.uuid4().hex[:8]}"
    conn = _connect()
    conn.execute(
        """
        INSERT INTO messages (message_id, thread_id, sender_id, message_type, content, voice_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (message_id, thread_id, sender_id, message_type, content, voice_url),
    )
    conn.commit()
    conn.close()
    return message_id


def get_thread_messages(thread_id: str) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
        (thread_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Voice analysis results (Algorithm B.3/B.4) ---

def save_voice_analysis(
    user_id: str,
    prompt_id: int,
    question_text: str,
    audio_url: str,
    transcript: str,
    output1_json: str,
    output2_json: str,
    reasoning_trace: str,
    dimension_snapshot_json: str,
    next_question: str | None = None,
    session_complete: bool = False,
) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT OR REPLACE INTO voice_analysis_results
            (user_id, prompt_id, question_text, audio_url, transcript,
             output1_json, output2_json, reasoning_trace, dimension_snapshot_json,
             next_question, session_complete)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, prompt_id, question_text, audio_url, transcript,
         output1_json, output2_json, reasoning_trace, dimension_snapshot_json,
         next_question, int(session_complete)),
    )
    conn.commit()
    conn.close()


def get_next_question_after_prompt(user_id: str, prompt_id: int) -> str | None:
    """Return the next_question produced after analyzing a given prompt."""
    conn = _connect()
    row = conn.execute(
        "SELECT next_question FROM voice_analysis_results WHERE user_id = ? AND prompt_id = ?",
        (user_id, prompt_id),
    ).fetchone()
    conn.close()
    return row["next_question"] if row else None


def get_voice_analyses(user_id: str) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM voice_analysis_results WHERE user_id = ? ORDER BY prompt_id",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- User dimensions (Algorithm B.1) ---

def upsert_user_dimensions(user_id: str, dimensions: dict[str, float]) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT INTO user_dimensions (user_id,
            d1_score, d1_confidence, d2_score, d2_confidence,
            d3_score, d3_confidence, d4_score, d4_confidence,
            d5_score, d5_confidence, d6_score, d6_confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            d1_score=excluded.d1_score, d1_confidence=excluded.d1_confidence,
            d2_score=excluded.d2_score, d2_confidence=excluded.d2_confidence,
            d3_score=excluded.d3_score, d3_confidence=excluded.d3_confidence,
            d4_score=excluded.d4_score, d4_confidence=excluded.d4_confidence,
            d5_score=excluded.d5_score, d5_confidence=excluded.d5_confidence,
            d6_score=excluded.d6_score, d6_confidence=excluded.d6_confidence,
            updated_at=datetime('now')
        """,
        (
            user_id,
            dimensions.get("d1_score", 0.5), dimensions.get("d1_confidence", 0.0),
            dimensions.get("d2_score", 0.5), dimensions.get("d2_confidence", 0.0),
            dimensions.get("d3_score", 0.5), dimensions.get("d3_confidence", 0.0),
            dimensions.get("d4_score", 0.5), dimensions.get("d4_confidence", 0.0),
            dimensions.get("d5_score", 0.5), dimensions.get("d5_confidence", 0.0),
            dimensions.get("d6_score", 0.5), dimensions.get("d6_confidence", 0.0),
        ),
    )
    conn.commit()
    conn.close()


def get_user_dimensions(user_id: str) -> dict | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM user_dimensions WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# --- Vibe progress (Algorithm D.6) ---

def upsert_vibe_progress(
    thread_id: str,
    user_a_id: str,
    user_b_id: str,
    resonance_score: float,
    vibe_stage: str,
    trend: str,
    insights_json: str,
    call_summaries_json: str,
) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT INTO vibe_progress
            (thread_id, user_a_id, user_b_id, resonance_score, vibe_stage,
             trend, insights_json, call_summaries_json, last_analysis_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(thread_id) DO UPDATE SET
            resonance_score=excluded.resonance_score,
            vibe_stage=excluded.vibe_stage,
            trend=excluded.trend,
            insights_json=excluded.insights_json,
            call_summaries_json=excluded.call_summaries_json,
            last_analysis_at=datetime('now')
        """,
        (thread_id, user_a_id, user_b_id, resonance_score,
         vibe_stage, trend, insights_json, call_summaries_json),
    )
    conn.commit()
    conn.close()


def get_vibe_progress(thread_id: str) -> dict | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM vibe_progress WHERE thread_id = ?",
        (thread_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
