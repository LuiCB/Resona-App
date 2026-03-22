import Foundation

struct APIErrorPayload: Decodable {
    let detail: String
}

enum APIClientError: LocalizedError {
    case invalidResponse
    case server(statusCode: Int, message: String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server."
        case .server(_, let message):
            return message
        }
    }
}

struct ResonaAPI {
    private let client: APIClient
    private let decoder = JSONDecoder()
    private let encoder = JSONEncoder()

    init(baseURL: URL) {
        self.client = APIClient(baseURL: baseURL)
    }

    func getProfile(userID: String) async throws -> UserProfile {
        let request = client.makeRequest(path: "api/v1/users/\(userID)/profile")
        let data = try await execute(request)
        return try decoder.decode(UserProfile.self, from: data)
    }

    func upsertProfile(_ profile: UserProfile) async throws -> UserProfile {
        var request = client.makeRequest(path: "api/v1/users/profile", method: "POST")
        request.httpBody = try encoder.encode(profile)
        let data = try await execute(request)
        return try decoder.decode(UserProfile.self, from: data)
    }

    func getMatchCandidates(userID: String) async throws -> [MatchCandidate] {
        let request = client.makeRequest(path: "api/v1/match/\(userID)/candidates")
        let data = try await execute(request)
        return try decoder.decode([MatchCandidate].self, from: data)
    }

    func getCallCandidate(userID: String) async throws -> CallCandidate {
        let request = client.makeRequest(path: "api/v1/call/\(userID)/candidate")
        let data = try await execute(request)
        return try decoder.decode(CallCandidate.self, from: data)
    }

    func getInboxThreads(userID: String) async throws -> [InboxThread] {
        let request = client.makeRequest(path: "api/v1/inbox/\(userID)/threads")
        let data = try await execute(request)
        let response = try decoder.decode(InboxThreadsResponse.self, from: data)
        return response.threads
    }

    func getConnections(userID: String) async throws -> [ConnectionItem] {
        let request = client.makeRequest(path: "api/v1/connections/\(userID)")
        let data = try await execute(request)
        let response = try decoder.decode(ConnectionsResponse.self, from: data)
        return response.connections
    }

    func getVibeReport(userID: String, period: String = "weekly") async throws -> VibeReport {
        var components = URLComponents()
        components.queryItems = [URLQueryItem(name: "period", value: period)]
        let query = components.percentEncodedQuery.map { "?\($0)" } ?? ""
        let request = client.makeRequest(path: "api/v1/reports/\(userID)/vibe-check\(query)")
        let data = try await execute(request)
        return try decoder.decode(VibeReport.self, from: data)
    }

    // MARK: - Voice Prompts (Algorithm B.2)

    func getVoicePrompts(userID: String) async throws -> VoicePromptsResponse {
        let request = client.makeRequest(path: "api/v1/voice/\(userID)/prompts")
        let data = try await execute(request)
        return try decoder.decode(VoicePromptsResponse.self, from: data)
    }

    func getVoiceProfile(userID: String) async throws -> VoiceProfileResponse {
        let request = client.makeRequest(path: "api/v1/voice/\(userID)/profile")
        let data = try await execute(request)
        return try decoder.decode(VoiceProfileResponse.self, from: data)
    }

    func submitVoiceRecording(userID: String, promptID: Int, questionText: String, audioFileURL: URL) async throws -> VoiceRecordingResult {
        let boundary = "Boundary-\(UUID().uuidString)"
        var request = client.makeRequest(path: "api/v1/voice/recording", method: "POST")
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        func appendField(_ name: String, _ value: String) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(value)\r\n".data(using: .utf8)!)
        }
        appendField("user_id", userID)
        appendField("prompt_id", "\(promptID)")
        appendField("question_text", questionText)

        let audioData = try Data(contentsOf: audioFileURL)
        let filename = audioFileURL.lastPathComponent
        let ext = audioFileURL.pathExtension.lowercased()
        let mimeType = ext == "m4a" ? "audio/mp4" : ext == "mp3" ? "audio/mpeg" : "audio/wav"
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"audio_file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        body.append(audioData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        request.httpBody = body
        let data = try await execute(request)
        return try decoder.decode(VoiceRecordingResult.self, from: data)
    }

    private func execute(_ request: URLRequest) async throws -> Data {
        let (data, response) = try await URLSession.shared.data(for: request)

        guard let http = response as? HTTPURLResponse else {
            throw APIClientError.invalidResponse
        }
        guard (200...299).contains(http.statusCode) else {
            if let payload = try? decoder.decode(APIErrorPayload.self, from: data) {
                throw APIClientError.server(statusCode: http.statusCode, message: payload.detail)
            }
            throw APIClientError.server(statusCode: http.statusCode, message: "Server error (\(http.statusCode)).")
        }

        return data
    }
}
