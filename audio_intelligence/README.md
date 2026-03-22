# Audio Intelligence

This module owns voice feature extraction and recommendation logic.

## Responsibilities

- Process Voice-Yourself recordings and emit structured features (FR-12)
- Transcribe voice messages and extract emotion keywords (FR-14)
- Generate 5-second voice preview clips for Call mode (FR-07)
- Generate ranked match candidates for discovery deck (FR-03)
- Generate call-mode candidates for live voice roulette (FR-06)
- Provide explainability metadata for weekly/monthly vibe report (FR-20)

## Boundaries

- Do not own user auth, profile persistence, or messaging state
- Do not call iOS app directly; communicate through backend APIs

## Structure

```
contracts/
  backend_integration.md   # Full API contract between backend ↔ AI service
interfaces/
  base.py                  # Abstract interfaces (FeatureExtractor, Transcriber, etc.)
  stubs.py                 # Stub implementations for local testing
examples/
  feature_schema.json      # Example extracted feature set
```

## Interfaces

| Interface          | PRD Ref  | Purpose                                       |
|--------------------|----------|-----------------------------------------------|
| FeatureExtractor   | FR-12    | Extract acoustic + semantic features from audio |
| Transcriber        | FR-14    | Voice-to-text with emotion keyword detection   |
| PreviewGenerator   | FR-07    | Generate 5s vibe snippet for Call preview      |
| Recommender        | FR-03/06 | Rank match and call candidates by resonance    |
| InsightGenerator   | FR-20    | Produce weekly/monthly vibe-check summaries    |

## Local Usage

```python
from interfaces.stubs import StubTranscriber

transcriber = StubTranscriber()
result = transcriber.transcribe("https://cdn.example.com/voice/note.m4a")
print(result.transcript, result.emotion_keywords)
```
