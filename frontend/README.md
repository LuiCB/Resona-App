# Frontend (iOS / SwiftUI)

This folder contains the iOS client architecture for Resona.

## Product direction

Resona should feel warm, intimate, and reflective, not fast and gamified. UI language emphasizes voice snippets, emotional cues, and thoughtful pacing.

## Suggested stack

- SwiftUI for UI composition
- AVFoundation for voice recording/playback
- URLSession for backend API calls
- CoreData or SwiftData for local caching

## Feature map

- `Features/Onboarding`: profile + mandatory voice prompt completion gate
- `Features/VoiceYourself`: recording and progress/resume flow
- `Features/MainTabs`: 5-tab shell (Match, Call, Voice, Inbox, Connections)
- `Core/Theme`: color, typography, and spacing tokens
- `Core/Networking`: API client to backend

## Added starter code

- `Core/Models/ProfileModels.swift`: Codable payloads aligned with backend schemas
- `Core/Networking/ResonaAPI.swift`: async API wrapper for profile + match calls
- `Features/Match/MatchDeckView.swift`: fetches and renders discovery candidates
- `Features/Call/CallRouletteView.swift`: fetches live call candidate with preview metadata

## Local integration note

- API base URL is currently `http://127.0.0.1:8000` in `Features/MainTabs/MainTabView.swift`
- Start backend locally before using Match/Call tabs
