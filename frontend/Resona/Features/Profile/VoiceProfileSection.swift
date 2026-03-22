import SwiftUI

/// Radar/hexagon chart + evidence cards for Voice-Yourself dimension scores.
struct VoiceProfileSection: View {
    let profile: VoiceProfileResponse

    @State private var expandedDimension: String? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Summary
            Text(profile.summary)
                .font(.subheadline)
                .foregroundStyle(ResonaTheme.dusk.opacity(0.8))

            // Radar chart
            if !profile.dimensions.isEmpty {
                RadarChartView(dimensions: profile.dimensions)
                    .frame(height: 220)
                    .padding(.horizontal)
            }

            // Dimension detail cards
            ForEach(profile.dimensions) { dim in
                DimensionCard(dimension: dim, isExpanded: expandedDimension == dim.dimension) {
                    withAnimation(.spring(duration: 0.3)) {
                        expandedDimension = expandedDimension == dim.dimension ? nil : dim.dimension
                    }
                }
            }
        }
    }
}

// MARK: - Radar Chart

struct RadarChartView: View {
    let dimensions: [VoiceDimensionDetail]

    var body: some View {
        GeometryReader { geo in
            let center = CGPoint(x: geo.size.width / 2, y: geo.size.height / 2)
            let radius = min(geo.size.width, geo.size.height) / 2 - 30

            ZStack {
                // Grid rings
                ForEach([0.25, 0.5, 0.75, 1.0], id: \.self) { level in
                    radarPath(count: dimensions.count, center: center, radius: radius * level)
                        .stroke(ResonaTheme.dusk.opacity(0.08), lineWidth: 1)
                }

                // Axis lines
                ForEach(0..<dimensions.count, id: \.self) { i in
                    Path { path in
                        path.move(to: center)
                        path.addLine(to: point(index: i, count: dimensions.count, center: center, radius: radius))
                    }
                    .stroke(ResonaTheme.dusk.opacity(0.1), lineWidth: 1)
                }

                // Score polygon fill
                radarDataPath(center: center, radius: radius)
                    .fill(ResonaTheme.ember.opacity(0.15))

                // Score polygon stroke
                radarDataPath(center: center, radius: radius)
                    .stroke(ResonaTheme.ember, lineWidth: 2)

                // Score dots + labels
                ForEach(0..<dimensions.count, id: \.self) { i in
                    let dim = dimensions[i]
                    let pt = point(index: i, count: dimensions.count, center: center, radius: radius * dim.score)
                    let labelPt = point(index: i, count: dimensions.count, center: center, radius: radius + 20)

                    Circle()
                        .fill(ResonaTheme.ember)
                        .frame(width: 6, height: 6)
                        .position(pt)

                    Text(dim.label.components(separatedBy: " ").first ?? dim.label)
                        .font(.system(size: 9, weight: .medium))
                        .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                        .position(labelPt)
                }
            }
        }
    }

    private func radarDataPath(center: CGPoint, radius: Double) -> Path {
        Path { path in
            for i in 0..<dimensions.count {
                let pt = point(index: i, count: dimensions.count, center: center, radius: radius * dimensions[i].score)
                if i == 0 { path.move(to: pt) } else { path.addLine(to: pt) }
            }
            path.closeSubpath()
        }
    }

    private func radarPath(count: Int, center: CGPoint, radius: Double) -> Path {
        Path { path in
            for i in 0..<count {
                let pt = point(index: i, count: count, center: center, radius: radius)
                if i == 0 { path.move(to: pt) } else { path.addLine(to: pt) }
            }
            path.closeSubpath()
        }
    }

    private func point(index: Int, count: Int, center: CGPoint, radius: Double) -> CGPoint {
        let angle = (Double(index) / Double(count)) * 2 * .pi - .pi / 2
        return CGPoint(x: center.x + radius * cos(angle), y: center.y + radius * sin(angle))
    }
}

// MARK: - Dimension Card

struct DimensionCard: View {
    let dimension: VoiceDimensionDetail
    let isExpanded: Bool
    let onTap: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header row
            Button(action: onTap) {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(dimension.label)
                            .font(.subheadline.bold())
                            .foregroundStyle(ResonaTheme.dusk)
                        Text(dimension.description)
                            .font(.caption2)
                            .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                    }
                    Spacer()
                    // Score badge
                    Text("\(Int(dimension.score * 100))%")
                        .font(.callout.bold().monospacedDigit())
                        .foregroundStyle(ResonaTheme.ember)
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundStyle(ResonaTheme.dusk.opacity(0.3))
                }
            }

            // Score bar
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 3)
                        .fill(ResonaTheme.dusk.opacity(0.08))
                    RoundedRectangle(cornerRadius: 3)
                        .fill(ResonaTheme.ember.opacity(0.7))
                        .frame(width: geo.size.width * dimension.score)
                }
            }
            .frame(height: 6)

            HStack {
                Text("Confidence: \(Int(dimension.confidence * 100))%")
                    .font(.caption2)
                    .foregroundStyle(ResonaTheme.dusk.opacity(0.4))
                Spacer()
                Text("\(dimension.evidence.count) signal(s)")
                    .font(.caption2)
                    .foregroundStyle(ResonaTheme.sage)
            }

            // Expanded evidence
            if isExpanded && !dimension.evidence.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(dimension.evidence) { ev in
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Q\(ev.promptID + 1): \(ev.question)")
                                .font(.caption.bold())
                                .foregroundStyle(ResonaTheme.dusk)
                            if !ev.transcript.isEmpty {
                                Text("\"\(ev.transcript)\"")
                                    .font(.caption2)
                                    .foregroundStyle(ResonaTheme.dusk.opacity(0.6))
                                    .italic()
                                    .lineLimit(3)
                            }
                            if !ev.keyThemes.isEmpty {
                                HStack(spacing: 4) {
                                    ForEach(ev.keyThemes, id: \.self) { theme in
                                        Text(theme)
                                            .font(.system(size: 9))
                                            .padding(.horizontal, 6)
                                            .padding(.vertical, 2)
                                            .background(ResonaTheme.sage.opacity(0.15), in: Capsule())
                                            .foregroundStyle(ResonaTheme.dusk.opacity(0.7))
                                    }
                                }
                            }
                            if !ev.emotionalTone.isEmpty {
                                Label(ev.emotionalTone, systemImage: "waveform")
                                    .font(.caption2)
                                    .foregroundStyle(ResonaTheme.ember.opacity(0.7))
                                    .lineLimit(2)
                            }
                        }
                        .padding(8)
                        .background(ResonaTheme.dusk.opacity(0.03), in: RoundedRectangle(cornerRadius: 8))
                    }
                }
            }
        }
        .padding(12)
        .background(.white.opacity(0.7), in: RoundedRectangle(cornerRadius: 12))
    }
}
