# PRD: Resona — Voice-First Connection App

**Version:** 1.0  
**Status:** Draft / Experimental  
**Platform:** iOS

## 1. Product Vision
Move beyond the superficiality of swiping by using audio intelligence to analyze user characteristics, sentiment, and subconscious patterns. Resona seeks to match users based on vocal resonance and way of thinking rather than visual aesthetics alone.

## 2. Target Audience
- **Deep Seekers:** Users tired of ghosting and low-effort text interactions
- **Auditory Learners:** People who find tone and cadence more attractive than a static bio
- **Gen Z / Millennials:** Users looking for authentic, vibe-based digital experiences

## 3. User Lifecycle and Feature Requirements

### 3.1 Onboarding and Basic Profile
**FR-01 — Basic Profile**  
Users must complete a profile containing:
- Identity: name, age, gender, gender and age preference
- Visuals: minimum of 2 verified photos
- Logistics: current location with geofencing
- Intent: goal selection such as long-term, short-term, or friends

**FR-02 — Navigation**  
A top-left profile icon opens a sidebar containing:
- Edit Profile: form-based fields with a Save and Exit button
- Log Out: returns the user to the authentication screen



### 3.2 The 5-Pillar Main Interface
To emphasize voice as the core product value, the app utilizes a 5-Element Bottom Tab Bar with a central high-visibility action.
- Tab 1 (Left): Match (Discovery Deck)
- Tab 2 (Mid-Left): Call (Real-time Voice Roulette)
- Tab 3 (Center - Primary): Voice-Yourself (Recording/Analysis Hub)
- Tab 4 (Mid-Right): Inbox (Text/Voice Message history)
- Tab 5 (Right): Connections (Mutual Matches/Soulmates)


#### A. Match
**FR-03 — Smart Batching**  
Generate 15 profile cards based on a recommendation engine using audio and text data.

**FR-04 — Swiping Mechanic**  
Swipe left to dislike and right to like.

**FR-05 — Deep Dive**  
Tap a card to view the full profile and listen to Voice-Yourself snippets.

USER CANNOT start matching without completing at least 2 Voice-Yourself questions.

#### B. Call
**FR-6 — Real-Time Matching**  
Match users currently in Active Call Mode.

**FR-7 — Voice Preview**  
Before connecting, let the user hear a 5-second vibe snippet of the other person.

**FR-8 — Connect or Decline**  
Allow the user to enter the call or decline based on the preview.

USER CANNOT start calling without completing at least 2 Voice-Yourself questions.

### C Voice-Yourself Analysis
**FR-09 — Recording Interface**  
Provide a dedicated screen with a central red Record button.

**FR-10 — Guided Prompts**  
Users answer 5 to 6 randomized psychological or philosophical questions.  
Example: “What does home feel like to you?”

**FR-10 — Save and Resume**  
Users can save progress and return later to complete the recording suite.

**FR-12 — Audio Intelligence Backend**  
Recordings are processed for:
- Sentiment: emotional baseline such as optimism and stability
- Cadence: speed and rhythm of thought
- Subconsciousness: vocabulary usage and hesitation patterns
- Content analysis: speech-to-text conversion with LLM for content analysis

### D. Inbox
In the inbox, user can check the historical message (Text/Voice Message history)

**FR-13 — Voice-First Threading**  
In the conversation list, display a mini-waveform instead of “Last message: [Text]” when the most recent message is a voice note.  
Users can tap a Play icon directly from the Inbox list to hear the latest voice note without opening the full thread.

**FR-14 — Dynamic Transcription**  
All voice messages are automatically transcribed into text and shown in a smaller, subtle font beneath the audio bubble.  
The AI highlights core emotion keywords, such as Excited, Hesitant, and Reflective, to help users understand the sender’s current sentiment.

**FR-15 — Vibe Progress Bar**  
Each chat thread includes a small Resonance Meter at the top that increases as the two users exchange more voice minutes.  
Higher resonance levels unlock Audio Themes or shared voice filters for Call mode.

**FR-16 — Integrated Call History**  
The Inbox also serves as a log for Call mode. If a call was successful and led to Friend status, the call duration and an AI-generated Call Summary appear in the thread.

**FR-17 — Quick-Record UI**  
Within the chat, a Hold-to-Talk button serves as the primary input.  
A Slide to Lock gesture supports longer, more thoughtful voice responses aligned with the way-of-thinking experience.

### E. Connections

**FR-18 — Mutual Match**  
Only users who mutually liked each other appear here.

**FR-19 — Communication**  
Support two primary modes:
- Direct phone call
- Voice messaging as asynchronous audio notes, which will direct to the message history page. 

The user can hang up the call by clicking the hang-up button. The user can exit the message page by clicking the back button on the top-left. 

### 3.3 Weekly Report: 
**FR-20: The "Vibe Check" Report**: A monthly or weekly AI summary sent to the user: "You seem to resonate most with people who speak slowly and use abstract metaphors." This gamifies the "subconscious" aspect of the app.


### 3.4 Voice Profile Visualization:
Based on the answer to the question, and the computed voice profile, we need to visualize the profile for the user. 
**FR-21: Voice Profile**
Add a new tab on the main page for voice profile, where we visualize the voice feature, it could be a diagram overview, detailed bullet points and evidence. 


## 4. Success Metrics
| KPI | Description |
|---|---|
| Voice-Yourself Completion Rate | Percentage of users who finish all 6 recordings |
| Call Duration | Average length of Call Mode conversations |
| Resonance Score | Match accuracy measured by how many Friends exchange more than 5 voice notes |

