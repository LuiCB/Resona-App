import Foundation

struct UserProfile: Codable {
    let userID: String
    var name: String
    var age: Int
    var gender: String
    var preferenceGender: String
    var preferenceAgeMin: Int
    var preferenceAgeMax: Int
    var intent: String
    var location: String
    var photoCount: Int
    var voicePromptCompleted: Int
    var interests: [String]

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case name
        case age
        case gender
        case preferenceGender = "preference_gender"
        case preferenceAgeMin = "preference_age_min"
        case preferenceAgeMax = "preference_age_max"
        case intent
        case location
        case photoCount = "photo_count"
        case voicePromptCompleted = "voice_prompt_completed"
        case interests
    }
}

struct MatchCandidate: Codable, Identifiable, Hashable {
    let candidateID: String
    let displayName: String
    let age: Int
    let gender: String
    let location: String
    let intent: String
    let bio: String
    let voicePreviewURL: String?
    let resonanceScore: Double

    var id: String { candidateID }

    enum CodingKeys: String, CodingKey {
        case candidateID = "candidate_id"
        case displayName = "display_name"
        case age
        case gender
        case location
        case intent
        case bio
        case voicePreviewURL = "voice_preview_url"
        case resonanceScore = "resonance_score"
    }
}

struct CallCandidate: Codable {
    let candidateID: String
    let previewURL: String
    let resonanceScore: Double

    enum CodingKeys: String, CodingKey {
        case candidateID = "candidate_id"
        case previewURL = "preview_url"
        case resonanceScore = "resonance_score"
    }
}

struct VibeReport: Codable {
    let userID: String
    let period: String
    let summary: String
    let featureHighlights: [String]

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case period
        case summary
        case featureHighlights = "feature_highlights"
    }
}

struct InboxThread: Codable, Identifiable {
    let threadID: String
    let peerID: String
    let peerName: String
    let lastMessageType: String
    let latestVoicePreviewURL: String?
    let latestTranscript: String?
    let emotionKeywords: [String]
    let resonanceMeter: Double
    let latestCallSummary: String?

    var id: String { threadID }

    enum CodingKeys: String, CodingKey {
        case threadID = "thread_id"
        case peerID = "peer_id"
        case peerName = "peer_name"
        case lastMessageType = "last_message_type"
        case latestVoicePreviewURL = "latest_voice_preview_url"
        case latestTranscript = "latest_transcript"
        case emotionKeywords = "emotion_keywords"
        case resonanceMeter = "resonance_meter"
        case latestCallSummary = "latest_call_summary"
    }
}

struct InboxThreadsResponse: Codable {
    let userID: String
    let threads: [InboxThread]

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case threads
    }
}

struct ConnectionItem: Codable, Identifiable, Hashable {
    let connectionID: String
    let displayName: String
    let status: String
    let voiceNoteCount: Int
    let canDirectCall: Bool

    var id: String { connectionID }

    enum CodingKeys: String, CodingKey {
        case connectionID = "connection_id"
        case displayName = "display_name"
        case status
        case voiceNoteCount = "voice_note_count"
        case canDirectCall = "can_direct_call"
    }
}

struct ConnectionsResponse: Codable {
    let userID: String
    let connections: [ConnectionItem]

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case connections
    }
}

// MARK: - Voice Prompts (Algorithm B.2)

struct VoicePrompt: Codable, Identifiable {
    let promptID: Int
    let text: String
    let completed: Bool

    var id: Int { promptID }

    enum CodingKeys: String, CodingKey {
        case promptID = "prompt_id"
        case text
        case completed
    }
}

struct VoicePromptsResponse: Codable {
    let userID: String
    let prompts: [VoicePrompt]
    let completedCount: Int

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case prompts
        case completedCount = "completed_count"
    }
}

struct VoiceRecordingSubmission: Codable {
    let userID: String
    let promptID: Int
    let questionText: String
    let audioURL: String

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case promptID = "prompt_id"
        case questionText = "question_text"
        case audioURL = "audio_url"
    }
}

struct VoiceRecordingResult: Codable {
    let userID: String
    let promptID: Int
    let status: String
    let completedCount: Int
    let nextQuestion: String?
    let sessionComplete: Bool

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case promptID = "prompt_id"
        case status
        case completedCount = "completed_count"
        case nextQuestion = "next_question"
        case sessionComplete = "session_complete"
    }
}

// --- Voice Profile: dimension visualization + evidence ---

struct VoiceEvidenceItem: Codable, Identifiable {
    let promptID: Int
    let question: String
    let transcript: String
    let keyThemes: [String]
    let emotionalTone: String
    let reasoning: String

    var id: Int { promptID }

    enum CodingKeys: String, CodingKey {
        case promptID = "prompt_id"
        case question
        case transcript
        case keyThemes = "key_themes"
        case emotionalTone = "emotional_tone"
        case reasoning
    }
}

struct VoiceDimensionDetail: Codable, Identifiable {
    let dimension: String
    let label: String
    let score: Double
    let confidence: Double
    let description: String
    let evidence: [VoiceEvidenceItem]

    var id: String { dimension }
}

struct LinguisticInsight: Codable, Identifiable {
    let label: String
    let value: String
    let icon: String
    let detail: String

    var id: String { label }
}

struct VocalBehaviorInsight: Codable, Identifiable {
    let label: String
    let value: String
    let icon: String

    var id: String { label }
}

struct VoiceProfileResponse: Codable {
    let userID: String
    let completedCount: Int
    let dimensions: [VoiceDimensionDetail]
    let summary: String
    let personalityNarrative: String
    let linguisticInsights: [LinguisticInsight]
    let vocalBehavior: [VocalBehaviorInsight]
    let topThemes: [String]
    let voiceIdentityLabel: String

    enum CodingKeys: String, CodingKey {
        case userID = "user_id"
        case completedCount = "completed_count"
        case dimensions
        case summary
        case personalityNarrative = "personality_narrative"
        case linguisticInsights = "linguistic_insights"
        case vocalBehavior = "vocal_behavior"
        case topThemes = "top_themes"
        case voiceIdentityLabel = "voice_identity_label"
    }
}
