import SwiftUI

// FR-19: Voice call view for a connection
struct ConnectionCallView: View {
    let connection: ConnectionItem
    @State private var callActive = false
    @State private var elapsed = 0
    @State private var timer: Timer?
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            ResonaTheme.dusk.ignoresSafeArea()

            VStack(spacing: 30) {
                Spacer()

                // Avatar
                Circle()
                    .fill(ResonaTheme.sage.opacity(0.3))
                    .frame(width: 100, height: 100)
                    .overlay(
                        Text(String(connection.displayName.prefix(1)))
                            .font(.largeTitle)
                            .foregroundStyle(.white)
                    )

                Text(connection.displayName)
                    .font(.title.bold())
                    .foregroundStyle(.white)

                if callActive {
                    Text(formatTime(elapsed))
                        .font(.title3.monospacedDigit())
                        .foregroundStyle(.white.opacity(0.8))
                } else {
                    Text("Connecting...")
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.6))
                }

                Spacer()

                // FR-19: Hang-up button
                Button {
                    timer?.invalidate()
                    dismiss()
                } label: {
                    Image(systemName: "phone.down.fill")
                        .font(.title)
                        .foregroundStyle(.white)
                        .frame(width: 70, height: 70)
                        .background(.red, in: Circle())
                }
                .padding(.bottom, 50)
            }
        }
        .onAppear {
            callActive = true
            timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
                elapsed += 1
            }
        }
        .onDisappear {
            timer?.invalidate()
        }
        .navigationBarBackButtonHidden()
    }

    private func formatTime(_ seconds: Int) -> String {
        String(format: "%02d:%02d", seconds / 60, seconds % 60)
    }
}

// MARK: - Connections List
struct ConnectionsView: View {
    let api: ResonaAPI
    let userID: String

    @State private var connections: [ConnectionItem] = []
    @State private var message = ""
    @State private var callTarget: ConnectionItem?
    @State private var messageTarget: ConnectionItem?

    var body: some View {
        NavigationStack {
            ZStack {
                ResonaTheme.backgroundGradient.ignoresSafeArea()
                VStack(alignment: .leading, spacing: 14) {
                    Text("Connections")
                        .font(ResonaTheme.titleFont)
                        .foregroundStyle(ResonaTheme.dusk)
                        .padding(.top, 28)

                    Text("Your mutual matches")
                        .font(.caption)
                        .foregroundStyle(ResonaTheme.dusk.opacity(0.6))

                    if !message.isEmpty {
                        Text(message)
                            .font(.subheadline)
                            .foregroundStyle(ResonaTheme.ember)
                    }

                    ScrollView {
                        VStack(spacing: 12) {
                            ForEach(connections) { connection in
                                VStack(alignment: .leading, spacing: 10) {
                                    HStack {
                                        // Avatar
                                        Circle()
                                            .fill(ResonaTheme.sage.opacity(0.3))
                                            .frame(width: 44, height: 44)
                                            .overlay(
                                                Text(String(connection.displayName.prefix(1)))
                                                    .font(.headline)
                                                    .foregroundStyle(ResonaTheme.dusk)
                                            )

                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(connection.displayName)
                                                .font(.headline)
                                                .foregroundStyle(ResonaTheme.dusk)
                                            Text(connection.status.capitalized)
                                                .font(.caption)
                                                .foregroundStyle(ResonaTheme.sage)
                                        }
                                        Spacer()

                                        // Voice notes badge
                                        HStack(spacing: 3) {
                                            Image(systemName: "waveform")
                                                .font(.caption2)
                                            Text("\(connection.voiceNoteCount)")
                                                .font(.caption2.bold())
                                        }
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(ResonaTheme.ember.opacity(0.1), in: Capsule())
                                        .foregroundStyle(ResonaTheme.ember)
                                    }

                                    // FR-19: Communication buttons
                                    HStack(spacing: 12) {
                                        // Direct phone call
                                        Button {
                                            callTarget = connection
                                        } label: {
                                            Label("Call", systemImage: "phone.fill")
                                                .frame(maxWidth: .infinity)
                                        }
                                        .buttonStyle(.borderedProminent)
                                        .tint(ResonaTheme.sage)
                                        .disabled(!connection.canDirectCall)

                                        // Voice messaging -> navigates to inbox/chat
                                        Button {
                                            messageTarget = connection
                                        } label: {
                                            Label("Message", systemImage: "mic.fill")
                                                .frame(maxWidth: .infinity)
                                        }
                                        .buttonStyle(.bordered)
                                    }
                                }
                                .padding()
                                .background(.white.opacity(0.9), in: RoundedRectangle(cornerRadius: 14))
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationDestination(item: $callTarget) { connection in
                ConnectionCallView(connection: connection)
            }
            .sheet(item: $messageTarget) { connection in
                NavigationStack {
                    // FR-19: Create a placeholder chat thread for messaging
                    ChatDetailView(thread: InboxThread(
                        threadID: connection.connectionID,
                        peerID: connection.connectionID,
                        peerName: connection.displayName,
                        lastMessageType: "text",
                        latestVoicePreviewURL: nil,
                        latestTranscript: nil,
                        emotionKeywords: [],
                        resonanceMeter: 0.0,
                        latestCallSummary: nil
                    ))
                    .toolbar {
                        ToolbarItem(placement: .cancellationAction) {
                            Button("Back") { messageTarget = nil }
                        }
                    }
                }
            }
        }
        .task { await loadConnections() }
    }

    private func loadConnections() async {
        do {
            connections = try await api.getConnections(userID: userID)
            message = connections.isEmpty ? "No mutual matches yet." : ""
        } catch {
            message = (error as? LocalizedError)?.errorDescription ?? "Unable to load connections."
        }
    }
}
