# Backend Integration Contract

## 1) Submit voice analysis result

`POST /api/v1/voice/analysis`

```json
{
  "user_id": "user-123",
  "sentiment_label": "reflective",
  "cadence_wpm": 122.4,
  "hesitation_rate": 0.11,
  "content_summary": "Values emotional safety and thoughtful communication",
  "analyzed_at": "2026-03-19T09:42:00Z"
}
```

## 2) Submit a voice recording for processing

The iOS app uploads an audio file. The backend stores metadata and forwards the
recording to this service for feature extraction.

`POST /internal/voice/process`

Request (multipart or JSON reference):
```json
{
  "user_id": "user-123",
  "prompt_id": 2,
  "audio_s3_key": "recordings/user-123/prompt-2.m4a",
  "sample_rate_hz": 44100,
  "duration_seconds": 18.4
}
```

Response — the extracted feature set (see `examples/feature_schema.json`):
```json
{
  "user_id": "user-123",
  "recording_id": "rec-991",
  "acoustic_features": { "...": "..." },
  "semantic_features": { "...": "..." },
  "quality": { "...": "..." }
}
```

## 3) Transcribe a voice message (FR-14)

Used by the backend when a voice note is sent in Inbox. Returns text transcript
plus emotion keywords for display.

`POST /internal/voice/transcribe`

```json
{
  "audio_url": "https://cdn.example.com/voice/msg-abc.m4a",
  "language": "en"
}
```

```json
{
  "transcript": "I liked how calmly you described your weekend.",
  "emotion_keywords": ["Reflective", "Curious"],
  "confidence": 0.92
}
```

## 4) Generate voice preview clip (FR-07)

Create a 5-second vibe snippet from a user's Voice-Yourself recordings for use
in Call mode preview.

`POST /internal/voice/preview-clip`

```json
{
  "user_id": "user-789",
  "max_duration_seconds": 5.0
}
```

```json
{
  "clip_url": "https://cdn.example.com/previews/user-789/clip-5s.mp3",
  "duration_seconds": 5.0,
  "source_prompt_ids": [0, 3]
}
```

## 5) Match candidates for discovery deck

Backend calls recommender service (internal endpoint):

`POST /internal/recommend/match`

```json
{
  "user_id": "user-123",
  "limit": 15,
  "constraints": {
    "distance_km": 30,
    "intent": "long-term"
  }
}
```

```json
{
  "candidates": [
    {
      "candidate_id": "user-456",
      "resonance_score": 0.83,
      "reason_tags": ["calm-cadence", "high-empathy"]
    }
  ]
}
```

## 6) Live call candidate

`POST /internal/recommend/call`

```json
{
  "user_id": "user-123",
  "active_now_only": true
}
```

```json
{
  "candidate_id": "user-789",
  "resonance_score": 0.75,
  "preview_clip_s3_key": "previews/user-789/clip-5s.mp3"
}
```

## 7) Vibe report insight hints (FR-20)

`POST /internal/insights/vibe-check`

```json
{
  "user_id": "user-123",
  "window": "weekly"
}
```

```json
{
  "summary": "You resonate most with people who speak slowly and use abstract metaphors.",
  "feature_highlights": ["slow-cadence", "metaphorical-language"]
}
```
