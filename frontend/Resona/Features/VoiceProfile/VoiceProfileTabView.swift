import SwiftUI

struct VoiceProfileTabView: View {
    let api: ResonaAPI
    let userID: String
    let completedPrompts: Int

    @State private var profile: VoiceProfileResponse?
    @State private var isLoading = true
    @State private var expandedDimension: String?
    @State private var animateChart = false

    var body: some View {
        NavigationStack {
            Group {
                if isLoading {
                    loadingView
                } else if let profile, profile.completedCount > 0 {
                    profileContent(profile)
                } else {
                    emptyState
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background { ResonaTheme.backgroundGradient.ignoresSafeArea() }
            .navigationTitle("VoicePrint")
            .navigationBarTitleDisplayMode(.inline)
        }
        .task { await loadProfile() }
    }

    // MARK: - Loading

    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.2)
                .tint(ResonaTheme.ember)
            Text("Analyzing your voice identity...")
                .font(.subheadline)
                .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
        }
    }

    // MARK: - Empty State

    private var emptyState: some View {
        VStack(spacing: 20) {
            Spacer()
            Image(systemName: "waveform.badge.magnifyingglass")
                .font(.system(size: 56))
                .foregroundStyle(ResonaTheme.ember.opacity(0.4))
            Text("Your Voice Profile")
                .font(ResonaTheme.titleFont)
                .foregroundStyle(ResonaTheme.dusk)
            Text("Complete voice prompts in the Voice tab to unlock your psychological voice profile — powered by AI analysis of what you say and how you say it.")
                .font(ResonaTheme.bodyFont)
                .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            Spacer()
        }
    }

    // MARK: - Profile Content

    private func profileContent(_ p: VoiceProfileResponse) -> some View {
        ScrollView {
            VStack(spacing: 24) {
                // --- Hero / Identity Header ---
                identityHeader(p)

                // --- Radar Chart ---
                radarSection(p)

                // --- Top Themes ---
                if !p.topThemes.isEmpty {
                    themesSection(p.topThemes)
                }

                // --- Personality Narrative ---
                if !p.personalityNarrative.isEmpty {
                    narrativeSection(p.personalityNarrative)
                }

                // --- Linguistic Insights ---
                if !p.linguisticInsights.isEmpty {
                    linguisticSection(p.linguisticInsights)
                }

                // --- Vocal Behavior ---
                if !p.vocalBehavior.isEmpty {
                    vocalSection(p.vocalBehavior)
                }

                // --- Dimension Breakdown ---
                dimensionSection(p.dimensions)

                Color.clear.frame(height: 100)
            }
            .padding(.horizontal)
            .padding(.top, 8)
        }
    }

    // MARK: - Identity Header

    private func identityHeader(_ p: VoiceProfileResponse) -> some View {
        VStack(spacing: 12) {
            // Voice identity icon
            ZStack {
                Circle()
                    .fill(ResonaTheme.ember.opacity(0.12))
                    .frame(width: 80, height: 80)
                Image(systemName: "waveform.circle.fill")
                    .font(.system(size: 44))
                    .foregroundStyle(ResonaTheme.ember)
            }
            .padding(.top, 8)

            if !p.voiceIdentityLabel.isEmpty {
                Text(p.voiceIdentityLabel)
                    .font(.title2.bold())
                    .foregroundStyle(ResonaTheme.dusk)
            }

            Text(p.summary)
                .font(.subheadline)
                .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 8)

            // Completion badge
            HStack(spacing: 6) {
                Image(systemName: "checkmark.seal.fill")
                    .foregroundStyle(ResonaTheme.sage)
                Text("\(p.completedCount) voice response\(p.completedCount == 1 ? "" : "s") analyzed")
                    .font(.caption)
                    .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
            }
        }
        .padding(.vertical, 16)
        .frame(maxWidth: .infinity)
        .background(.white.opacity(0.5), in: RoundedRectangle(cornerRadius: 20))
    }

    // MARK: - Radar Section

    private func radarSection(_ p: VoiceProfileResponse) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionHeader("Dimension Overview", icon: "hexagon", subtitle: "Your 6-dimension psychological fingerprint")

            RadarChartView(dimensions: p.dimensions)
                .frame(height: 240)
                .padding(.horizontal, 8)
                .opacity(animateChart ? 1 : 0)
                .scaleEffect(animateChart ? 1 : 0.8)
                .animation(.spring(duration: 0.6, bounce: 0.3), value: animateChart)
                .onAppear { animateChart = true }
        }
        .sectionCard()
    }

    // MARK: - Top Themes

    private func themesSection(_ themes: [String]) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader("Key Themes", icon: "tag.fill", subtitle: "Recurring ideas across your responses")

            FlowLayout(spacing: 8) {
                ForEach(themes, id: \.self) { theme in
                    Text(theme)
                        .font(.caption)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(ResonaTheme.sage.opacity(0.15), in: Capsule())
                        .foregroundStyle(ResonaTheme.dusk.opacity(0.8))
                }
            }
        }
        .sectionCard()
    }

    // MARK: - Narrative

    private func narrativeSection(_ narrative: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader("AI Personality Insight", icon: "brain.head.profile", subtitle: "What your voice reveals about you")

            Text(narrative)
                .font(.subheadline)
                .foregroundStyle(ResonaTheme.dusk.opacity(0.8))
                .lineSpacing(4)
        }
        .sectionCard()
    }

    // MARK: - Linguistic Insights

    private func linguisticSection(_ insights: [LinguisticInsight]) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader("How You Speak", icon: "text.quote", subtitle: "Linguistic patterns detected in your words")

            ForEach(insights) { insight in
                HStack(spacing: 12) {
                    Image(systemName: insight.icon.isEmpty ? "textformat" : insight.icon)
                        .font(.title3)
                        .foregroundStyle(ResonaTheme.ember)
                        .frame(width: 32)

                    VStack(alignment: .leading, spacing: 2) {
                        HStack {
                            Text(insight.label)
                                .font(.subheadline.bold())
                                .foregroundStyle(ResonaTheme.dusk)
                            Spacer()
                            Text(insight.value.capitalized)
                                .font(.subheadline.bold())
                                .foregroundStyle(ResonaTheme.ember)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 3)
                                .background(ResonaTheme.ember.opacity(0.1), in: Capsule())
                        }
                        if !insight.detail.isEmpty {
                            Text(insight.detail)
                                .font(.caption)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                                .lineLimit(2)
                        }
                    }
                }
                .padding(.vertical, 4)
                if insight.id != insights.last?.id {
                    Divider().opacity(0.3)
                }
            }
        }
        .sectionCard()
    }

    // MARK: - Vocal Behavior

    private func vocalSection(_ behaviors: [VocalBehaviorInsight]) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader("How You Sound", icon: "speaker.wave.3.fill", subtitle: "Vocal patterns from audio analysis")

            ForEach(behaviors) { b in
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: b.icon.isEmpty ? "waveform" : b.icon)
                        .font(.title3)
                        .foregroundStyle(ResonaTheme.sage)
                        .frame(width: 32)

                    VStack(alignment: .leading, spacing: 2) {
                        Text(b.label)
                            .font(.caption.bold())
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                        Text(b.value)
                            .font(.subheadline)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.85))
                            .lineLimit(3)
                    }
                }
                .padding(.vertical, 4)
                if b.id != behaviors.last?.id {
                    Divider().opacity(0.3)
                }
            }
        }
        .sectionCard()
    }

    // MARK: - Dimension Breakdown

    private func dimensionSection(_ dims: [VoiceDimensionDetail]) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader("Dimension Breakdown", icon: "slider.horizontal.3", subtitle: "Tap any dimension to see the evidence")

            ForEach(dims) { dim in
                DimensionCard(
                    dimension: dim,
                    isExpanded: expandedDimension == dim.dimension
                ) {
                    withAnimation(.spring(duration: 0.3)) {
                        expandedDimension = expandedDimension == dim.dimension ? nil : dim.dimension
                    }
                }
            }
        }
    }

    // MARK: - Helpers

    private func sectionHeader(_ title: String, icon: String, subtitle: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Label(title, systemImage: icon)
                .font(.headline)
                .foregroundStyle(ResonaTheme.dusk)
            Text(subtitle)
                .font(.caption)
                .foregroundStyle(ResonaTheme.dusk.opacity(0.4))
        }
    }

    @MainActor
    private func loadProfile() async {
        defer { isLoading = false }
        do {
            profile = try await api.getVoiceProfile(userID: userID)
        } catch {
            // Will show empty state
        }
    }
}

// MARK: - Section Card Modifier

private struct SectionCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.white.opacity(0.6), in: RoundedRectangle(cornerRadius: 16))
    }
}

extension View {
    func sectionCard() -> some View {
        modifier(SectionCardModifier())
    }
}

// MARK: - Flow Layout (for theme tags)

struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = arrange(proposal: proposal, subviews: subviews)
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = arrange(proposal: proposal, subviews: subviews)
        for (index, position) in result.positions.enumerated() {
            subviews[index].place(at: CGPoint(x: bounds.minX + position.x, y: bounds.minY + position.y), proposal: .unspecified)
        }
    }

    private func arrange(proposal: ProposedViewSize, subviews: Subviews) -> (size: CGSize, positions: [CGPoint]) {
        let maxWidth = proposal.width ?? .infinity
        var positions: [CGPoint] = []
        var x: CGFloat = 0
        var y: CGFloat = 0
        var rowHeight: CGFloat = 0
        var maxX: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > maxWidth, x > 0 {
                x = 0
                y += rowHeight + spacing
                rowHeight = 0
            }
            positions.append(CGPoint(x: x, y: y))
            rowHeight = max(rowHeight, size.height)
            x += size.width + spacing
            maxX = max(maxX, x)
        }

        return (CGSize(width: maxX, height: y + rowHeight), positions)
    }
}
