import SwiftUI

struct ProfileMenuView: View {
    let api: ResonaAPI
    let userID: String
    @Binding var completedPrompts: Int
    @Binding var isLoggedIn: Bool

    // FR-01: Editable profile fields
    @State private var name = "Demo User"
    @State private var age = 26
    @State private var gender = "non-binary"
    @State private var preferenceGender = "all"
    @State private var preferenceAgeMin = 23
    @State private var preferenceAgeMax = 35
    @State private var intent = "long-term"
    @State private var location = "San Francisco"

    @State private var report: VibeReport?
    @State private var voiceProfile: VoiceProfileResponse?
    @State private var saveMessage = ""

    @Environment(\.dismiss) private var dismiss

    private let genderOptions = ["male", "female", "non-binary", "other"]
    private let prefGenderOptions = ["male", "female", "non-binary", "all"]
    private let intentOptions = ["long-term", "short-term", "friends"]

    var body: some View {
        NavigationStack {
            ZStack {
                ResonaTheme.backgroundGradient.ignoresSafeArea()
                Form {
                    // FR-01: Identity
                    Section("Identity") {
                        TextField("Name", text: $name)
                        Stepper("Age: \(age)", value: $age, in: 18...99)
                        Picker("Gender", selection: $gender) {
                            ForEach(genderOptions, id: \.self) { Text($0.capitalized) }
                        }
                    }

                    // FR-01: Preferences
                    Section("Preferences") {
                        Picker("Looking for", selection: $preferenceGender) {
                            ForEach(prefGenderOptions, id: \.self) { Text($0.capitalized) }
                        }
                        Stepper("Min age: \(preferenceAgeMin)", value: $preferenceAgeMin, in: 18...98)
                        Stepper("Max age: \(preferenceAgeMax)", value: $preferenceAgeMax, in: (preferenceAgeMin+1)...99)
                    }

                    // FR-01: Intent & Location
                    Section("Details") {
                        Picker("Intent", selection: $intent) {
                            ForEach(intentOptions, id: \.self) { Text($0.capitalized) }
                        }
                        TextField("Location", text: $location)
                    }

                    // Voice progress
                    Section("Voice-Yourself") {
                        HStack {
                            Text("Prompts completed")
                            Spacer()
                            Text("\(completedPrompts) / 6")
                                .foregroundStyle(ResonaTheme.ember)
                                .bold()
                        }
                        ProgressView(value: Double(completedPrompts), total: 6.0)
                            .tint(ResonaTheme.ember)
                    }

                    // Voice Feature Profile — radar chart + dimension details
                    Section("Voice Feature Profile") {
                        if let vp = voiceProfile {
                            VoiceProfileSection(profile: vp)
                        } else if completedPrompts > 0 {
                            HStack {
                                ProgressView()
                                Text("Loading voice analysis...")
                                    .font(.caption)
                            }
                        } else {
                            Text("Complete voice prompts to see your profile.")
                                .font(.caption)
                                .foregroundStyle(ResonaTheme.dusk.opacity(0.5))
                        }
                    }

                    // Save
                    Section {
                        Button {
                            Task { await saveProfile() }
                        } label: {
                            HStack {
                                Spacer()
                                Label("Save & Exit", systemImage: "checkmark.circle.fill")
                                    .bold()
                                Spacer()
                            }
                        }
                        .tint(ResonaTheme.ember)

                        if !saveMessage.isEmpty {
                            Text(saveMessage)
                                .font(.caption)
                                .foregroundStyle(ResonaTheme.ember)
                        }
                    }

                    // FR-20: Vibe Check Report
                    Section("Vibe Check Report") {
                        if let report {
                            Text(report.summary)
                                .font(.subheadline)
                            HStack(spacing: 6) {
                                ForEach(report.featureHighlights, id: \.self) { tag in
                                    Text(tag)
                                        .font(.caption2)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 3)
                                        .background(ResonaTheme.sage.opacity(0.2), in: Capsule())
                                        .foregroundStyle(ResonaTheme.dusk)
                                }
                            }
                        } else {
                            HStack {
                                ProgressView()
                                Text("Loading report...")
                                    .font(.caption)
                            }
                        }
                    }

                    // FR-02: Log Out
                    Section {
                        Button("Log Out", role: .destructive) {
                            isLoggedIn = false
                            dismiss()
                        }
                    }
                }
                .scrollContentBackground(.hidden)
            }
            .navigationTitle("Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { dismiss() }
                }
            }
            .task { await loadReport() }
            .task { await loadVoiceProfile() }
        }
    }

    private func saveProfile() async {
        let profile = UserProfile(
            userID: userID,
            name: name,
            age: age,
            gender: gender,
            preferenceGender: preferenceGender,
            preferenceAgeMin: preferenceAgeMin,
            preferenceAgeMax: preferenceAgeMax,
            intent: intent,
            location: location,
            photoCount: 2,
            voicePromptCompleted: completedPrompts,
            interests: []
        )

        do {
            _ = try await api.upsertProfile(profile)
            saveMessage = "Saved!"
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) { dismiss() }
        } catch {
            saveMessage = (error as? LocalizedError)?.errorDescription ?? "Save failed"
        }
    }

    private func loadReport() async {
        do {
            report = try await api.getVibeReport(userID: userID)
        } catch {
            // Report may not exist yet for new users
        }
    }

    private func loadVoiceProfile() async {
        do {
            voiceProfile = try await api.getVoiceProfile(userID: userID)
        } catch {
            // Profile may not exist yet
        }
    }
}
