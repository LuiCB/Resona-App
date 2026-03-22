import SwiftUI

struct OnboardingGateView: View {
    @State private var completedVoicePrompts = 0
    @State private var isLoggedIn = true
    private let userID = "demo-user-1"

    var body: some View {
        if isLoggedIn {
            NavigationStack {
                ZStack {
                    ResonaTheme.backgroundGradient.ignoresSafeArea()

                    VStack(spacing: 24) {
                        Spacer()

                        Image(systemName: "waveform.circle.fill")
                            .font(.system(size: 72))
                            .foregroundStyle(ResonaTheme.ember)

                        Text("Resona")
                            .font(ResonaTheme.titleFont)
                            .foregroundStyle(ResonaTheme.dusk)

                        Text("Find someone who sounds like home.")
                            .font(ResonaTheme.bodyFont)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.85))
                            .multilineTextAlignment(.center)

                        // Voice prompt progress
                        VStack(spacing: 8) {
                            Text("Voice prompts completed")
                                .font(.subheadline)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                            ProgressView(value: Double(completedVoicePrompts), total: 6.0)
                                .tint(ResonaTheme.ember)
                                .frame(width: 200)
                            Text("\(completedVoicePrompts) / 6")
                                .font(.headline)
                                .foregroundStyle(ResonaTheme.ember)
                        }

                        NavigationLink {
                            VoiceYourselfHubView(completedPrompts: $completedVoicePrompts, userID: userID)
                        } label: {
                            Label("Record Voice-Yourself", systemImage: "mic.fill")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(ResonaTheme.ember)
                        .padding(.horizontal, 40)

                        NavigationLink {
                            MainTabView(
                                completedPrompts: $completedVoicePrompts,
                                isLoggedIn: $isLoggedIn,
                                userID: userID
                            )
                            .navigationBarBackButtonHidden()
                        } label: {
                            Label("Enter Main App", systemImage: "arrow.right.circle.fill")
                                .frame(maxWidth: .infinity)
                        }
                        .disabled(completedVoicePrompts < 2)
                        .buttonStyle(.bordered)
                        .padding(.horizontal, 40)

                        if completedVoicePrompts < 2 {
                            Text("Complete at least 2 voice prompts to unlock")
                                .font(.caption)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                        }

                        Spacer()
                    }
                    .padding(24)
                }
            }
        } else {
            // Logged out: show a simple login placeholder
            ZStack {
                ResonaTheme.backgroundGradient.ignoresSafeArea()
                VStack(spacing: 20) {
                    Text("Resona")
                        .font(ResonaTheme.titleFont)
                        .foregroundStyle(ResonaTheme.dusk)
                    Text("You have been logged out.")
                        .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                    Button("Log In") {
                        isLoggedIn = true
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(ResonaTheme.ember)
                }
            }
        }
    }
}
