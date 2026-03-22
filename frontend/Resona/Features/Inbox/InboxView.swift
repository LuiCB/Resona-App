import SwiftUI

// MARK: - FR-15 Resonance Meter
struct ResonanceMeterView: View {
    let value: Double // 0.0 to 1.0

    var body: some View {
        VStack(spacing: 2) {
            HStack(spacing: 4) {
                Image(systemName: "waveform.path")
                    .font(.caption2)
                Text("Resonance")
                    .font(.caption2)
                Spacer()
                Text("\(Int(value * 100))%")
                    .font(.caption2.bold())
            }
            .foregroundStyle(ResonaTheme.ember)

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(ResonaTheme.dusk.opacity(0.1))
                    Capsule()
                        .fill(
                            LinearGradient(
                                colors: [ResonaTheme.sage, ResonaTheme.ember],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: geo.size.width * value)
                }
            }
            .frame(height: 6)
        }
    }
}

// MARK: - FR-17 Chat Detail View
struct ChatDetailView: View {
    let thread: InboxThread
    @State private var isHolding = false

    // Simulated messages for demo
    private var messages: [(String, Bool, String?)] {
        var msgs: [(String, Bool, String?)] = []
        if let transcript = thread.latestTranscript {
            msgs.append((transcript, false, "voice"))
        }
        msgs.append(("Hey! I loved your voice note.", true, "text"))
        if thread.latestCallSummary != nil {
            msgs.append(("We had a great call!", false, "text"))
        }
        return msgs
    }

    var body: some View {
        ZStack {
            ResonaTheme.backgroundGradient.ignoresSafeArea()

            VStack(spacing: 0) {
                // FR-15: Resonance Meter at top
                ResonanceMeterView(value: thread.resonanceMeter)
                    .padding()
                    .background(.white.opacity(0.9))

                // FR-16: Call summary if exists
                if let callSummary = thread.latestCallSummary {
                    HStack(spacing: 8) {
                        Image(systemName: "phone.fill")
                            .foregroundStyle(ResonaTheme.sage)
                        Text(callSummary)
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity)
                    .background(ResonaTheme.sage.opacity(0.1))
                }

                // Messages
                ScrollView {
                    VStack(spacing: 12) {
                        ForEach(Array(messages.enumerated()), id: \.offset) { _, msg in
                            let (text, isMine, type) = msg
                            HStack {
                                if isMine { Spacer() }

                                VStack(alignment: isMine ? .trailing : .leading, spacing: 4) {
                                    if type == "voice" {
                                        // Voice message bubble with waveform
                                        HStack(spacing: 8) {
                                            Image(systemName: "play.circle.fill")
                                                .font(.title2)
                                                .foregroundStyle(isMine ? .white : ResonaTheme.ember)
                                            Image(systemName: "waveform")
                                                .font(.body)
                                                .foregroundStyle(isMine ? .white.opacity(0.8) : ResonaTheme.ember.opacity(0.6))
                                        }
                                        .padding(12)
                                        .background(
                                            isMine ? ResonaTheme.ember : Color.white,
                                            in: RoundedRectangle(cornerRadius: 16)
                                        )

                                        // FR-14: Transcript below voice bubble
                                        Text(text)
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                            .italic()
                                    } else {
                                        Text(text)
                                            .padding(12)
                                            .background(
                                                isMine ? ResonaTheme.ember : Color.white,
                                                in: RoundedRectangle(cornerRadius: 16)
                                            )
                                            .foregroundStyle(isMine ? .white : ResonaTheme.dusk)
                                    }

                                    // FR-14: Emotion keywords
                                    if !isMine && !thread.emotionKeywords.isEmpty && type == "voice" {
                                        HStack(spacing: 4) {
                                            ForEach(thread.emotionKeywords, id: \.self) { keyword in
                                                Text(keyword)
                                                    .font(.caption2)
                                                    .padding(.horizontal, 6)
                                                    .padding(.vertical, 2)
                                                    .background(ResonaTheme.ember.opacity(0.1), in: Capsule())
                                                    .foregroundStyle(ResonaTheme.ember)
                                            }
                                        }
                                    }
                                }

                                if !isMine { Spacer() }
                            }
                        }
                    }
                    .padding()
                }

                // FR-17: Hold-to-Talk input
                HStack(spacing: 12) {
                    // Text fallback
                    Button {} label: {
                        Image(systemName: "keyboard")
                            .font(.title3)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                    }

                    // Hold-to-Talk button
                    Button {} label: {
                        HStack(spacing: 8) {
                            Image(systemName: "mic.fill")
                            Text(isHolding ? "Recording..." : "Hold to Talk")
                                .font(.subheadline.bold())
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(isHolding ? ResonaTheme.ember : ResonaTheme.dusk, in: Capsule())
                        .foregroundStyle(.white)
                    }
                    .simultaneousGesture(
                        LongPressGesture(minimumDuration: 0.1)
                            .onChanged { _ in isHolding = true }
                    )
                }
                .padding()
                .background(.white)
            }
        }
        .navigationTitle(thread.peerName)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Inbox List
struct InboxView: View {
    let api: ResonaAPI
    let userID: String

    @State private var threads: [InboxThread] = []
    @State private var message = ""

    var body: some View {
        NavigationStack {
            ZStack {
                ResonaTheme.backgroundGradient.ignoresSafeArea()
                VStack(alignment: .leading, spacing: 0) {
                    Text("Inbox")
                        .font(ResonaTheme.titleFont)
                        .foregroundStyle(ResonaTheme.dusk)
                        .padding()
                        .padding(.top, 28)

                    if !message.isEmpty {
                        Text(message)
                            .font(.subheadline)
                            .foregroundStyle(ResonaTheme.ember)
                            .padding(.horizontal)
                    }

                    List(threads) { thread in
                        NavigationLink(destination: ChatDetailView(thread: thread)) {
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    // Avatar placeholder
                                    Circle()
                                        .fill(ResonaTheme.sage.opacity(0.3))
                                        .frame(width: 44, height: 44)
                                        .overlay(
                                            Text(String(thread.peerName.prefix(1)))
                                                .font(.headline)
                                                .foregroundStyle(ResonaTheme.dusk)
                                        )

                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(thread.peerName)
                                            .font(.headline)
                                            .foregroundStyle(ResonaTheme.dusk)

                                        // FR-13: Mini waveform for voice messages
                                        if thread.lastMessageType == "voice" {
                                            HStack(spacing: 6) {
                                                Button {
                                                    // Play voice preview
                                                } label: {
                                                    Image(systemName: "play.circle.fill")
                                                        .foregroundStyle(ResonaTheme.ember)
                                                }
                                                Image(systemName: "waveform")
                                                    .font(.caption)
                                                    .foregroundStyle(ResonaTheme.ember.opacity(0.6))
                                                Text("Voice note")
                                                    .font(.caption)
                                                    .foregroundStyle(.secondary)
                                            }
                                        } else if let transcript = thread.latestTranscript {
                                            Text(transcript)
                                                .font(.caption)
                                                .foregroundStyle(.secondary)
                                                .lineLimit(1)
                                        }
                                    }

                                    Spacer()
                                }

                                // Resonance meter mini
                                ResonanceMeterView(value: thread.resonanceMeter)

                                // Emotion keywords
                                if !thread.emotionKeywords.isEmpty {
                                    HStack(spacing: 4) {
                                        ForEach(thread.emotionKeywords, id: \.self) { keyword in
                                            Text(keyword)
                                                .font(.caption2)
                                                .padding(.horizontal, 6)
                                                .padding(.vertical, 2)
                                                .background(ResonaTheme.ember.opacity(0.1), in: Capsule())
                                                .foregroundStyle(ResonaTheme.ember)
                                        }
                                    }
                                }

                                // FR-16: Call summary
                                if let callSummary = thread.latestCallSummary {
                                    HStack(spacing: 4) {
                                        Image(systemName: "phone.fill")
                                            .font(.caption2)
                                            .foregroundStyle(ResonaTheme.sage)
                                        Text(callSummary)
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                            .lineLimit(1)
                                    }
                                }
                            }
                            .padding(.vertical, 6)
                        }
                        .listRowBackground(Color.white.opacity(0.75))
                    }
                    .scrollContentBackground(.hidden)
                }
            }
        }
        .task { await loadThreads() }
    }

    private func loadThreads() async {
        do {
            threads = try await api.getInboxThreads(userID: userID)
            message = threads.isEmpty ? "No conversations yet." : ""
        } catch {
            message = (error as? LocalizedError)?.errorDescription ?? "Unable to load inbox."
        }
    }
}
