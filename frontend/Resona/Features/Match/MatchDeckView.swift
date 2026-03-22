import SwiftUI

// MARK: - FR-05 Deep Dive Detail
struct MatchProfileDetailView: View {
    let candidate: MatchCandidate
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            ResonaTheme.backgroundGradient.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 20) {
                    // Profile photo placeholder
                    ZStack {
                        RoundedRectangle(cornerRadius: 20)
                            .fill(ResonaTheme.dusk.opacity(0.1))
                            .frame(height: 300)
                        VStack(spacing: 8) {
                            Image(systemName: "person.fill")
                                .font(.system(size: 60))
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.3))
                            Text("\(candidate.displayName), \(candidate.age)")
                                .font(.title.bold())
                                .foregroundStyle(ResonaTheme.dusk)
                            Text(candidate.location)
                                .font(.subheadline)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                        }
                    }

                    // Resonance score
                    VStack(spacing: 6) {
                        Text("Vocal Resonance")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                        ProgressView(value: candidate.resonanceScore)
                            .tint(ResonaTheme.ember)
                        Text("\(Int(candidate.resonanceScore * 100))%")
                            .font(.title2.bold())
                            .foregroundStyle(ResonaTheme.ember)
                    }
                    .padding()
                    .background(.white.opacity(0.9), in: RoundedRectangle(cornerRadius: 16))

                    // Voice-Yourself snippet placeholder
                    VStack(spacing: 10) {
                        Text("Voice-Yourself Snippet")
                            .font(.headline)
                            .foregroundStyle(ResonaTheme.dusk)
                        HStack(spacing: 12) {
                            Image(systemName: "waveform")
                                .font(.title)
                                .foregroundStyle(ResonaTheme.ember)
                            Button {
                                // Audio playback placeholder
                            } label: {
                                Image(systemName: "play.circle.fill")
                                    .font(.system(size: 44))
                                    .foregroundStyle(ResonaTheme.ember)
                            }
                            Image(systemName: "waveform")
                                .font(.title)
                                .foregroundStyle(ResonaTheme.ember)
                        }
                        Text("Tap to listen to their voice")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding()
                    .background(.white.opacity(0.9), in: RoundedRectangle(cornerRadius: 16))

                    Spacer(minLength: 40)
                }
                .padding()
            }
        }
        .navigationTitle(candidate.displayName)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - FR-04 Swipeable Card
struct MatchCardView: View {
    let candidate: MatchCandidate
    let onSwipe: (Bool) -> Void // true = like, false = dislike
    let onTap: () -> Void

    @State private var offset: CGSize = .zero
    @State private var rotation: Double = 0

    private var swipeDirection: String? {
        if offset.width > 80 { return "LIKE" }
        if offset.width < -80 { return "PASS" }
        return nil
    }

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 20)
                .fill(.white)
                .shadow(color: .black.opacity(0.1), radius: 8, y: 4)

            VStack(spacing: 0) {
                // Photo area
                ZStack {
                    Rectangle()
                        .fill(
                            LinearGradient(
                                colors: [ResonaTheme.sage.opacity(0.3), ResonaTheme.ember.opacity(0.15)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    VStack(spacing: 8) {
                        Image(systemName: "person.fill")
                            .font(.system(size: 50))
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.3))
                        Text("Tap to view profile")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                    }
                }
                .frame(height: 320)
                .clipped()

                // Info area
                VStack(alignment: .leading, spacing: 8) {
                    HStack(alignment: .firstTextBaseline) {
                        Text(candidate.displayName)
                            .font(.title2.bold())
                        Text("\(candidate.age)")
                            .font(.title3)
                            .foregroundStyle(.secondary)
                        Spacer()
                        HStack(spacing: 4) {
                            Image(systemName: "waveform.path")
                                .foregroundStyle(ResonaTheme.ember)
                            Text("\(Int(candidate.resonanceScore * 100))%")
                                .font(.subheadline.bold())
                                .foregroundStyle(ResonaTheme.ember)
                        }
                    }

                    HStack(spacing: 4) {
                        Image(systemName: "location.fill")
                            .font(.caption)
                        Text(candidate.location)
                    }
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                }
                .padding()
            }
            .clipShape(RoundedRectangle(cornerRadius: 20))

            // Swipe indicator overlay
            if let direction = swipeDirection {
                Text(direction)
                    .font(.system(size: 40, weight: .black))
                    .foregroundStyle(direction == "LIKE" ? .green : .red)
                    .rotationEffect(.degrees(direction == "LIKE" ? -20 : 20))
                    .padding()
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(direction == "LIKE" ? .green : .red, lineWidth: 4)
                    )
            }
        }
        .frame(height: 440)
        .offset(offset)
        .rotationEffect(.degrees(rotation))
        .gesture(
            DragGesture()
                .onChanged { value in
                    offset = value.translation
                    rotation = Double(value.translation.width / 20)
                }
                .onEnded { value in
                    if value.translation.width > 120 {
                        withAnimation(.easeOut(duration: 0.3)) {
                            offset = CGSize(width: 500, height: 0)
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            onSwipe(true)
                        }
                    } else if value.translation.width < -120 {
                        withAnimation(.easeOut(duration: 0.3)) {
                            offset = CGSize(width: -500, height: 0)
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            onSwipe(false)
                        }
                    } else {
                        withAnimation(.spring()) {
                            offset = .zero
                            rotation = 0
                        }
                    }
                }
        )
        .onTapGesture { onTap() }
    }
}

// MARK: - Match Deck
struct MatchDeckView: View {
    let api: ResonaAPI
    let userID: String
    let completedPrompts: Int

    @State private var candidates: [MatchCandidate] = []
    @State private var statusMessage = ""
    @State private var isLoading = false
    @State private var selectedCandidate: MatchCandidate?

    var body: some View {
        NavigationStack {
            ZStack {
                ResonaTheme.backgroundGradient.ignoresSafeArea()

                VStack(spacing: 16) {
                    // Header
                    VStack(spacing: 4) {
                        Text("Discover")
                            .font(ResonaTheme.titleFont)
                            .foregroundStyle(ResonaTheme.dusk)
                        Text("Swipe right to like, left to pass")
                            .font(.caption)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                    }
                    .padding(.top, 40)

                    if isLoading {
                        Spacer()
                        ProgressView("Finding your people...")
                            .foregroundStyle(ResonaTheme.dusk)
                        Spacer()
                    } else if candidates.isEmpty {
                        Spacer()
                        VStack(spacing: 12) {
                            Image(systemName: "person.3.fill")
                                .font(.system(size: 40))
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.3))
                            Text(statusMessage.isEmpty ? "No more profiles" : statusMessage)
                                .font(.subheadline)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                            Button("Refresh") {
                                Task { await loadCandidates() }
                            }
                            .buttonStyle(.borderedProminent)
                            .tint(ResonaTheme.ember)
                        }
                        Spacer()
                    } else {
                        // FR-03/04: Stacked swipeable cards (highest score on top)
                        ZStack {
                            ForEach(candidates.prefix(3).reversed()) { candidate in
                                MatchCardView(
                                    candidate: candidate,
                                    onSwipe: { liked in
                                        withAnimation { candidates.removeAll { $0.id == candidate.id } }
                                    },
                                    onTap: { selectedCandidate = candidate }
                                )
                            }
                        }
                        .padding(.horizontal)

                        // Action buttons
                        HStack(spacing: 40) {
                            Button {
                                if let top = candidates.first {
                                    withAnimation { candidates.removeAll { $0.id == top.id } }
                                }
                            } label: {
                                Image(systemName: "xmark")
                                    .font(.title)
                                    .foregroundStyle(.red)
                                    .frame(width: 56, height: 56)
                                    .background(.white, in: Circle())
                                    .shadow(radius: 4)
                            }

                            Button {
                                if let top = candidates.first {
                                    withAnimation { candidates.removeAll { $0.id == top.id } }
                                }
                            } label: {
                                Image(systemName: "heart.fill")
                                    .font(.title)
                                    .foregroundStyle(.green)
                                    .frame(width: 56, height: 56)
                                    .background(.white, in: Circle())
                                    .shadow(radius: 4)
                            }
                        }
                        .padding(.bottom, 8)
                    }
                }
            }
            .navigationDestination(item: $selectedCandidate) { candidate in
                MatchProfileDetailView(candidate: candidate)
            }
            .task { await loadCandidates() }
        }
    }

    private func loadCandidates() async {
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
            candidates = try await api.getMatchCandidates(userID: userID)
            if candidates.isEmpty {
                statusMessage = "No candidates right now. Try again soon."
            }
        } catch {
            statusMessage = (error as? LocalizedError)?.errorDescription ?? "Unable to load matches."
        }

        isLoading = false
    }
}
