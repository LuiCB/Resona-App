import SwiftUI

@main
struct ResonaApp: App {
    var body: some Scene {
        WindowGroup {
            OnboardingGateView()
                .preferredColorScheme(.light)
        }
    }
}
