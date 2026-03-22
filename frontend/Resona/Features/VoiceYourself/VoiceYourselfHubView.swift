import AVFoundation
import SwiftUI
import UniformTypeIdentifiers

struct VoiceYourselfHubView: View {
    @Binding var completedPrompts: Int
    let userID: String
    @State private var selectedPromptIndex: Int = 0
    @State private var completedSet: Set<Int> = []
    @State private var isRecording = false
    @State private var recordingSeconds: Double = 0
    @State private var timer: Timer?
    @State private var prompts: [VoicePrompt] = []
    @State private var isLoading = true
    @State private var isSubmitting = false
    @State private var submitError: String? = nil

    @State private var audioRecorder: AVAudioRecorder?
    @State private var currentRecordingURL: URL? = nil
    @State private var showFilePicker = false

    private let minRecordingSeconds: Double = 3.0
    private let maxRecordingSeconds: Double = 120.0
    private let api = ResonaAPI(baseURL: URL(string: "http://localhost:8000")!)

    // Fallback prompts shown while loading from backend
    private let fallbackPrompts = [
        "Describe a place where you feel completely at ease.",
        "What kind of music do you turn to when you need to reset?",
        "What does emotional safety mean to you in a close relationship?",
        "What values guide your decisions?",
        "What kind of love feels healthiest to you?",
        "Describe the best conversation you've ever had — what made it so good?"
    ]

    private var promptTexts: [String] {
        prompts.isEmpty ? fallbackPrompts : prompts.map(\.text)
    }
    private var promptCount: Int { promptTexts.count }
    private var canStop: Bool { recordingSeconds >= minRecordingSeconds }

    var body: some View {
        ZStack {
            ResonaTheme.backgroundGradient.ignoresSafeArea()

            VStack(spacing: 20) {
                // Title
                VStack(spacing: 4) {
                    Text("Voice-Yourself")
                        .font(ResonaTheme.titleFont)
                        .foregroundStyle(ResonaTheme.dusk)
                    Text("Share your voice, reveal your vibe")
                        .font(.caption)
                        .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                }

                // Progress dots — tappable for navigation & redo
                HStack(spacing: 8) {
                    ForEach(0..<promptCount, id: \.self) { i in
                        Circle()
                            .fill(completedSet.contains(i)
                                  ? (i == selectedPromptIndex ? ResonaTheme.ember : ResonaTheme.sage)
                                  : (i == selectedPromptIndex ? ResonaTheme.ember.opacity(0.5) : ResonaTheme.dusk.opacity(0.15)))
                            .frame(width: i == selectedPromptIndex ? 14 : 10,
                                   height: i == selectedPromptIndex ? 14 : 10)
                            .overlay(
                                completedSet.contains(i)
                                ? Image(systemName: "checkmark")
                                    .font(.system(size: 6, weight: .bold))
                                    .foregroundStyle(.white)
                                : nil
                            )
                            .onTapGesture {
                                guard !isRecording else { return }
                                selectedPromptIndex = i
                            }
                            .animation(.spring(duration: 0.25), value: selectedPromptIndex)
                    }
                }

                Text("\(completedSet.count) / \(promptCount) completed")
                    .font(.subheadline)
                    .foregroundStyle(ResonaTheme.dusk.opacity(0.7))

                Spacer()

                // Current prompt card
                VStack(spacing: 12) {
                    HStack {
                        Text("Prompt \(selectedPromptIndex + 1)")
                            .font(.caption.bold())
                            .foregroundStyle(ResonaTheme.ember)
                        Spacer()
                        if completedSet.contains(selectedPromptIndex) {
                            Label("Recorded — tap mic to redo", systemImage: "arrow.counterclockwise")
                                .font(.caption2)
                                .foregroundStyle(ResonaTheme.sage)
                        }
                    }
                    Text(promptTexts[selectedPromptIndex])
                        .font(.title3)
                        .foregroundStyle(ResonaTheme.dusk)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding()
                .background(.white.opacity(0.8), in: RoundedRectangle(cornerRadius: 16))
                .padding(.horizontal)

                // Recording timer display
                if isRecording {
                    Text(formatTime(recordingSeconds))
                        .font(.title2.monospacedDigit())
                        .foregroundStyle(ResonaTheme.ember)
                }

                // FR-09: Central red Record button
                ZStack {
                    // Outer pulsing ring
                    Circle()
                        .stroke(ResonaTheme.ember.opacity(isRecording ? 0.4 : 0.1), lineWidth: 4)
                        .frame(width: 140, height: 140)
                        .scaleEffect(isRecording ? 1.15 : 1.0)
                        .animation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true), value: isRecording)

                    // Elapsed ring (fills over maxRecordingSeconds)
                    if isRecording {
                        Circle()
                            .trim(from: 0, to: min(recordingSeconds / maxRecordingSeconds, 1.0))
                            .stroke(ResonaTheme.ember, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                            .frame(width: 140, height: 140)
                            .rotationEffect(.degrees(-90))
                    }

                    // Main button
                    Button {
                        if isRecording {
                            if canStop { stopAndSubmit() }
                        } else {
                            startRecording()
                        }
                    } label: {
                        Circle()
                            .fill(ResonaTheme.ember)
                            .frame(width: 110, height: 110)
                            .overlay(
                                Group {
                                    if isRecording {
                                        RoundedRectangle(cornerRadius: 6)
                                            .fill(.white.opacity(canStop ? 1.0 : 0.4))
                                            .frame(width: 30, height: 30)
                                    } else {
                                        Image(systemName: "mic.fill")
                                            .font(.system(size: 36))
                                            .foregroundStyle(.white)
                                    }
                                }
                            )
                            .shadow(color: ResonaTheme.ember.opacity(0.4), radius: 12)
                    }
                }

                // Status text
                if isRecording {
                    if canStop {
                        Text("Tap stop when you're done")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                    } else {
                        Text("Keep going... \(Int(ceil(minRecordingSeconds - recordingSeconds)))s minimum")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.ember.opacity(0.8))
                    }
                } else if isSubmitting {
                    ProgressView()
                        .tint(ResonaTheme.ember)
                } else {
                    if let err = submitError {
                        Text(err)
                            .font(.caption)
                            .foregroundStyle(.red)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    } else {
                        Text(completedSet.contains(selectedPromptIndex)
                             ? "Tap to re-record this prompt"
                             : "Tap to record your answer")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                    }
                }

                // Upload file option
                if !isRecording && !isSubmitting {
                    Button {
                        showFilePicker = true
                    } label: {
                        Label("Upload a recording", systemImage: "folder")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                    }
                    .padding(.top, 4)
                }

                // Prompt navigation
                if !isRecording {
                    HStack(spacing: 24) {
                        Button {
                            if selectedPromptIndex > 0 { selectedPromptIndex -= 1 }
                        } label: {
                            Image(systemName: "chevron.left")
                                .font(.title3)
                                .foregroundStyle(selectedPromptIndex > 0 ? ResonaTheme.dusk : ResonaTheme.dusk.opacity(0.2))
                        }
                        .disabled(selectedPromptIndex == 0)

                        Text("\(selectedPromptIndex + 1) of \(promptCount)")
                            .font(.subheadline)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.6))

                        Button {
                            if selectedPromptIndex < promptCount - 1 { selectedPromptIndex += 1 }
                        } label: {
                            Image(systemName: "chevron.right")
                                .font(.title3)
                                .foregroundStyle(selectedPromptIndex < promptCount - 1 ? ResonaTheme.dusk : ResonaTheme.dusk.opacity(0.2))
                        }
                        .disabled(selectedPromptIndex >= promptCount - 1)
                    }
                }

                Spacer()
            }
            .padding()
        }
        .fileImporter(
            isPresented: $showFilePicker,
            allowedContentTypes: [.audio, .wav, UTType(filenameExtension: "m4a") ?? .audio],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                guard let url = urls.first else { return }
                submitUploadedFile(url: url)
            case .failure(let error):
                submitError = error.localizedDescription
            }
        }
        .onAppear {
            Task { await loadPrompts() }
        }
    }

    private func startRecording() {
        AVAudioApplication.requestRecordPermission { granted in
            guard granted else { return }
            DispatchQueue.main.async {
                let session = AVAudioSession.sharedInstance()
                try? session.setCategory(.record, mode: .default)
                try? session.setActive(true)

                let filename = "prompt_\(selectedPromptIndex)_\(Int(Date().timeIntervalSince1970)).wav"
                let url = FileManager.default.temporaryDirectory.appendingPathComponent(filename)
                currentRecordingURL = url

                let settings: [String: Any] = [
                    AVFormatIDKey: Int(kAudioFormatLinearPCM),
                    AVSampleRateKey: 16000,
                    AVNumberOfChannelsKey: 1,
                    AVLinearPCMBitDepthKey: 16,
                    AVLinearPCMIsFloatKey: false,
                    AVLinearPCMIsBigEndianKey: false,
                ]
                audioRecorder = try? AVAudioRecorder(url: url, settings: settings)
                audioRecorder?.record()

                isRecording = true
                recordingSeconds = 0
                timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
                    recordingSeconds += 0.1
                    if recordingSeconds >= maxRecordingSeconds {
                        stopAndSubmit()
                    }
                }
            }
        }
    }

    private func stopAndSubmit() {
        isRecording = false
        timer?.invalidate()
        timer = nil
        audioRecorder?.stop()
        audioRecorder = nil
        try? AVAudioSession.sharedInstance().setActive(false)

        guard let fileURL = currentRecordingURL else {
            recordingSeconds = 0
            return
        }

        withAnimation { completedSet.insert(selectedPromptIndex) }
        completedPrompts = completedSet.count

        let promptIndex = selectedPromptIndex
        let question = promptTexts[promptIndex]
        isSubmitting = true
        submitError = nil

        Task {
            do {
                let result = try await api.submitVoiceRecording(
                    userID: userID,
                    promptID: promptIndex,
                    questionText: question,
                    audioFileURL: fileURL
                )
                await MainActor.run {
                    isSubmitting = false
                    // Refresh prompts so next adaptive question appears
                    Task { await loadPrompts() }
                    // Auto-advance to next incomplete prompt
                    if !result.sessionComplete,
                       let next = (0..<promptCount).first(where: { !completedSet.contains($0) }) {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                            withAnimation { selectedPromptIndex = next }
                        }
                    }
                }
            } catch {
                await MainActor.run {
                    isSubmitting = false
                    submitError = error.localizedDescription
                }
            }
            recordingSeconds = 0
        }
    }

    @MainActor
    private func loadPrompts() async {
        do {
            let response = try await api.getVoicePrompts(userID: userID)
            prompts = response.prompts
            completedSet = Set(response.prompts.filter(\.completed).map(\.promptID))
            completedPrompts = completedSet.count
        } catch {
            // Keep fallback prompts
        }
    }

    private func submitUploadedFile(url: URL) {
        guard url.startAccessingSecurityScopedResource() else {
            submitError = "Cannot access selected file"
            return
        }
        let promptIndex = selectedPromptIndex
        let question = promptTexts[promptIndex]
        isSubmitting = true
        submitError = nil

        Task {
            defer { url.stopAccessingSecurityScopedResource() }
            do {
                let result = try await api.submitVoiceRecording(
                    userID: userID,
                    promptID: promptIndex,
                    questionText: question,
                    audioFileURL: url
                )
                await MainActor.run {
                    withAnimation { completedSet.insert(promptIndex) }
                    completedPrompts = completedSet.count
                    isSubmitting = false
                    Task { await loadPrompts() }
                    if !result.sessionComplete,
                       let next = (0..<promptCount).first(where: { !completedSet.contains($0) }) {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                            withAnimation { selectedPromptIndex = next }
                        }
                    }
                }
            } catch {
                await MainActor.run {
                    isSubmitting = false
                    submitError = error.localizedDescription
                }
            }
        }
    }

    private func formatTime(_ seconds: Double) -> String {
        let mins = Int(seconds) / 60
        let secs = Int(seconds) % 60
        return String(format: "%d:%02d", mins, secs)
    }
}
