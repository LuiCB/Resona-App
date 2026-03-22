import SwiftUI

enum ResonaTheme {
    // Warm palette to create an emotionally safe, intimate atmosphere.
    static let ember = Color(red: 0.87, green: 0.43, blue: 0.30)
    static let dusk = Color(red: 0.16, green: 0.14, blue: 0.18)
    static let sand = Color(red: 0.96, green: 0.92, blue: 0.86)
    static let sage = Color(red: 0.52, green: 0.64, blue: 0.57)

    static let backgroundGradient = LinearGradient(
        colors: [sand, Color.white, Color(red: 0.97, green: 0.95, blue: 0.90)],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )

    static let titleFont = Font.system(size: 30, weight: .bold, design: .serif)
    static let bodyFont = Font.system(size: 16, weight: .regular, design: .rounded)
}
