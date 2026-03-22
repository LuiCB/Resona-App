import SwiftUI

struct MainTabView: View {
    @Binding var completedPrompts: Int
    @Binding var isLoggedIn: Bool
    let userID: String

    @State private var showProfileMenu = false
    @State private var selectedTab = 2 // Default to Voice (center)
    private let api = ResonaAPI(baseURL: URL(string: "http://127.0.0.1:8000")!)

    var body: some View {
        TabView(selection: $selectedTab) {
            MatchDeckView(api: api, userID: userID, completedPrompts: completedPrompts)
                .tabItem { Label("Match", systemImage: "rectangle.stack.person.crop") }
                .tag(0)

            CallRouletteView(api: api, userID: userID, completedPrompts: completedPrompts)
                .tabItem { Label("Call", systemImage: "phone.fill") }
                .tag(1)

            VoiceYourselfHubView(completedPrompts: $completedPrompts, userID: userID)
                .tabItem { Label("Voice", systemImage: "mic.circle.fill") }
                .tag(2)

            VoiceProfileTabView(api: api, userID: userID, completedPrompts: completedPrompts)
                .tabItem { Label("VoicePrint", systemImage: "waveform.badge.magnifyingglass") }
                .tag(3)

            ConnectionsView(api: api, userID: userID)
                .tabItem { Label("Connections", systemImage: "person.2.fill") }
                .tag(4)

            InboxView(api: api, userID: userID)
                .tabItem { Label("Inbox", systemImage: "bubble.left.and.bubble.right.fill") }
                .tag(5)
        }
        .tint(ResonaTheme.ember)
        // FR-02: Top-left profile icon always accessible
        .overlay(alignment: .topLeading) {
            Button {
                showProfileMenu = true
            } label: {
                Image(systemName: "person.crop.circle.fill")
                    .font(.title2)
                    .foregroundStyle(ResonaTheme.dusk)
                    .padding(12)
                    .background(.ultraThinMaterial, in: Circle())
            }
            .padding(.leading, 16)
            .padding(.top, 8)
        }
        .sheet(isPresented: $showProfileMenu) {
            ProfileMenuView(
                api: api,
                userID: userID,
                completedPrompts: $completedPrompts,
                isLoggedIn: $isLoggedIn
            )
        }
    }
}
