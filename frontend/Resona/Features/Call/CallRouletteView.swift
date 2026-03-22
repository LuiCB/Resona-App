import SwiftUI

struct CallRouletteView: View {
    let api: ResonaAPI
    let userID: String
    let completedPrompts: Int

    @State private var candidate: CallCandidate?
    @State private var statusMessage = ""
    @State private var isLoading = false
    @State private var isInCall = false
    @State private var callSeconds = 0
    @State private var callTimer: Timer?

    var body: some View {
        ZStack {
            (isInCall ? ResonaTheme.dusk : Color.clear).ignoresSafeArea()
            if !isInCall { ResonaTheme.backgroundGradient.ignoresSafeArea() }

            if isInCall {
                // Active call UI
                VStack(spacing: 30) {
                    Spacer()
                    Circle()
                        .fill(ResonaTheme.sage.opacity(0.3))
                        .frame(width: 100, height: 100)
                        .overlay(
                            Image(systemName: "waveform")
                                .font(.largeTitle)
                                .foregroundStyle(.white)
                        )
                    Text("Connected")
                        .font(.title2.bold())
                        .foregroundStyle(.white)
                    Text(formatTime(callSeconds))
                        .font(.title.monospacedDigit())
                        .foregroundStyle(.white.opacity(0.8))
                    Spacer()
                    Button {
                        endCall()
                    } label: {
                        Image(systemName: "phone.down.fill")
                            .font(.title)
                            .foregroundStyle(.white)
                            .frame(width: 70, height: 70)
                            .background(.red, in: Circle())
                    }
                    .padding(.bottom, 50)
                }
            } else {
                // Discovery UI
                VStack(spacing: 20) {
                    VStack(spacing: 4) {
                        Text("Call")
                            .font(ResonaTheme.titleFont)
                            .foregroundStyle(ResonaTheme.dusk)
                        Text("Real-time voice roulette")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                    }
                    .padding(.top, 40)

                    if isLoading {
                        Spacer()
                        VStack(spacing: 14) {
                            ProgressView()
                                .scaleEffect(1.3)
                            Text("Finding someone in live mode...")
                                .font(.subheadline)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                        }
                        Spacer()
                    } else if let candidate {
                        Spacer()

                        // FR-07: Voice Preview card
                        VStack(spacing: 16) {
                            Circle()
                                .fill(ResonaTheme.sage.opacity(0.2))
                                .frame(width: 80, height: 80)
                                .overlay(
                                    Image(systemName: "person.fill")
                                        .font(.title)
                                        .foregroundStyle(ResonaTheme.dusk.opacity(0.4))
                                )

                            VStack(spacing: 4) {
                                Text("Resonance")
                                    .font(.caption)
                                    .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                                Text("\(Int(candidate.resonanceScore * 100))%")
                                    .font(.title.bold())
                                    .foregroundStyle(ResonaTheme.ember)
                            }

                            // 5-second vibe preview
                            VStack(spacing: 8) {
                                HStack(spacing: 10) {
                                    Button {} label: {
                                        Image(systemName: "play.circle.fill")
                                            .font(.system(size: 36))
                                            .foregroundStyle(ResonaTheme.ember)
                                    }
                                    Image(systemName: "waveform")
                                        .font(.title2)
                                        .foregroundStyle(ResonaTheme.ember.opacity(0.5))
                                }
                                Text("5-second vibe snippet")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .padding(24)
                        .background(.white.opacity(0.95), in: RoundedRectangle(cornerRadius: 20))
                        .shadow(color: .black.opacity(0.05), radius: 10)
                        .padding(.horizontal)

                        Spacer()

                        // FR-08: Connect or Decline
                        HStack(spacing: 30) {
                            Button {
                                Task { await findCandidate() }
                            } label: {
                                Image(systemName: "xmark")
                                    .font(.title2)
                                    .foregroundStyle(.red)
                                    .frame(width: 60, height: 60)
                                    .background(.white, in: Circle())
                                    .shadow(radius: 4)
                            }

                            Button {
                                startCall()
                            } label: {
                                Image(systemName: "phone.fill")
                                    .font(.title2)
                                    .foregroundStyle(.green)
                                    .frame(width: 60, height: 60)
                                    .background(.white, in: Circle())
                                    .shadow(radius: 4)
                            }
                        }
                        .padding(.bottom, 20)
                    } else {
                        Spacer()
                        VStack(spacing: 14) {
                            Image(systemName: "phone.badge.waveform.fill")
                                .font(.system(size: 40))
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.3))
                            Text(statusMessage.isEmpty ? "Tap to find someone" : statusMessage)
                                .font(.subheadline)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                                .multilineTextAlignment(.center)
                            Button("Go Live") {
                                Task { await findCandidate() }
                            }
                            .buttonStyle(.borderedProminent)
                            .tint(ResonaTheme.ember)
                        }
                        Spacer()
                    }
                }
            }
        }
        .task { await findCandidate() }
    }

    private func findCandidate() async {
        isLoading = true
        statusMessage = ""

        do {
            let profile = UserProfile(
                userID: userID,
                name: "Demo User",
                age: 26,
                gender: "non-binary",
                preferenceGender: "all",
                preferenceAgeMin: 23,
                preferenceAgeMax: 35,
                intent: "long-term",
                location: "San Francisco",
                photoCount: 2,
                voicePromptCompleted: completedPrompts,
                interests: []
            )
            _ = try await api.upsertProfile(profile)
            candidate = try await api.getCallCandidate(userID: userID)
        } catch {
            candidate = nil
            statusMessage = (error as? LocalizedError)?.errorDescription ?? "No one available right now."
        }

        isLoading = false
    }

    private func startCall() {
        isInCall = true
        callSeconds = 0
        callTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            callSeconds += 1
        }
    }

    private func endCall() {
        isInCall = false
        callTimer?.invalidate()
        callTimer = nil
        candidate = nil
        Task { await findCandidate() }
    }

    private func formatTime(_ seconds: Int) -> String {
        String(format: "%02d:%02d", seconds / 60, seconds % 60)
    }
}
