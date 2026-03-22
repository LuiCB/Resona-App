# Core Algorithm

**Version:** 1.0  
**Status:** Draft / Experimental  
**Platform:** iOS

## Overview:
The core algorithm covers four parts:
- User profile building
- Voice-Yourself Question design and Answer Modeling
- Matching System
- Vibe Progress
The together form the intelligence of the app. 


## A. User profile building
User profile building algorithm extracts the user profile information and create a quantitative representation that serves as input to the matching system. 
In version 1.0, the user profile quantitative representation is a vector. 

### A.1 Types of Features
There are three types of features. 
- Categorical features: such as age, gender, preference on age, preference on gender, relationship intent, location, etc. 
- Interest: a keyword or a short phrase decribing a topic, hobby, activity or even event that expresses the dynamics of the user
- Voice-Yourself features: based on the user's answer, AI analyze the preference, characteristics and subconciousness of the user. This will be a standalone feature list, which could be a combination of dense and sparse feature, used by the matching system

### A.2 Feature Vector Generation:
**Categorical features**: create one-hot embedding, and concatenate them
**Interest**: use text encoder from LLM to generate embedding, and normalize it. 
**Voice-Yourself features**: will be the output vector from Voice-Yourself algorithrm. 


## B. Voice-Yourself Question design and Answer Modeling
We focus on strong Psychology assumption and create an framework of user analysis with Psychology-based ontology. Given the Psychology framework and Ontology, the goal is to understand user's preference/characteristics/subconciousness by designing proper verbally answerable questions. There will be 5~6 questions, which are not fixed. The first 2 questions will be a relatively easy one for warmup. After that, the remaining questions need to be adaptive based on the uncertain or unclear understanding based on the Psychology framework. The question design should not be aggressive, biased. 
Once user answers the question, the answer modeling algorithm do behaviral analysis including but not limited to tone analysis, pace study, speech pattern analysis, and conduct speech-to-text translation to study the content with LLM. 
All these studies should be supported by the Psychology framework and ontology we define. 


### B.1  Psychology Framework and Ontology

The framework rests on four well-validated psychological theories, combined into a unified ontology of **six latent dimensions** that can be inferred from short voice responses.

#### Theoretical foundations

| Theory | Source | Why it matters for matching |
|---|---|---|
| **Big Five personality** (OCEAN) | Costa & McCrae, 1992 | Most robust predictor of interpersonal style; decades of relationship-outcome research |
| **Attachment theory** | Bowlby 1969, Bartholomew & Horowitz 1991 | Directly models how people bond, seek closeness, and handle conflict in romantic contexts |
| **Schwartz Basic Values** | Schwartz, 1992 | Captures what a person prioritizes (security vs. stimulation, tradition vs. self-direction) — drives long-term compatibility |
| **Emotional Intelligence (EI)** | Salovey & Mayer, 1990 | Predicts relationship satisfaction; measurable through verbal self-reflection quality |

#### Ontology: Six latent dimensions

Each dimension is a continuous score ∈ [0, 1], inferred jointly from acoustic features and semantic content.

| # | Dimension | Definition | Primary theory source | Observable signals |
|---|---|---|---|---|
| D1 | **Emotional Openness** | Willingness to access and express inner emotional states | Big Five Openness + EI emotional perception | Vocabulary richness, metaphor usage, vocal warmth, pitch variability |
| D2 | **Relational Security** | Internal model of trust and comfort with intimacy | Attachment (secure ↔ anxious-avoidant spectrum) | Hesitation patterns around vulnerability topics, speech rate stability, self-referencing vs. other-referencing |
| D3 | **Conflict Style** | How the person navigates disagreement and tension | Attachment + Big Five Agreeableness | Hedging language, conditional phrasing, tone shifts when discussing friction |
| D4 | **Energy Orientation** | Degree of extraversion in social and romantic contexts | Big Five Extraversion | Speaking pace, response latency, volume dynamics, narrative length |
| D5 | **Value Gravity** | Core life priorities (security/tradition vs. novelty/achievement) | Schwartz Values circumplex | Topic selection, future-tense usage, abstract vs. concrete reasoning |
| D6 | **Self-Awareness** | Capacity to reflect on one's own patterns and motivations | EI emotional understanding + Big Five Conscientiousness | Causal reasoning depth, use of qualifiers, spontaneous self-correction |

#### Ontology representation

Each user's Voice-Yourself profile is stored as:

**v** = [d₁, d₂, d₃, d₄, d₅, d₆, σ₁, σ₂, ..., σ₆]

where dᵢ is the point estimate for dimension i and σᵢ is the **uncertainty** (confidence interval width) for that dimension. The uncertainty values are critical — they drive the adaptive question selection in B.2.


### B.2 Question Design

#### Structure

The session consists of **5–6 questions** delivered in two phases:

| Phase | Questions | Purpose | Selection method |
|---|---|---|---|
| **Warmup** | Q1, Q2 | Build comfort, reduce recording anxiety, establish acoustic baseline | Fixed pool, randomly sampled |
| **Adaptive** | Q3–Q6 | Reduce uncertainty on underspecified dimensions | Algorithmically selected |

#### Warmup question pool (Phase 1)

These are low-threat, open-ended prompts designed to be universally comfortable. They still provide signal (especially acoustic baseline and D1/D4), but the primary goal is naturalistic speech elicitation.

| Pool | Example prompts |
|---|---|
| Sensory/nostalgic | "Describe a place where you feel completely at ease." / "What does a perfect slow morning look like for you?" |
| Preference/taste | "What kind of music do you turn to when you need to reset?" / "What's a meal that feels like home?" |
| Narrative/anecdotal | "Tell me about something small that made you smile recently." / "What's a hobby or interest you'd love to share with someone?" |

Design constraints:
- No reference to relationships, conflict, or vulnerability in Phase 1
- Phrased as sensory or narrative invitations, not interrogations
- Each prompt should naturally elicit 20–60 seconds of speech

#### Adaptive question selection (Phase 2)

After Q1 and Q2 are answered and analyzed, the system holds an interim belief state: the accumulated analysis outputs (Output1 + Output2 from B.3) for each answered question, plus the current dimension estimates and uncertainties.

**Selection is delegated to the Reasoning LLM (Stage 3 in B.3).** Rather than a hand-coded scoring formula, the reasoning LLM receives:
- The psychology ontology (D1–D6 definitions)
- All prior question–answer pairs with their analysis outputs
- The current dimension estimates and confidence levels
- The candidate prompt bank
- The design guardrails (below)

The LLM is prompted to:
1. Identify which dimensions remain **most uncertain or underspecified** based on the evidence so far.
2. Select the next question from the prompt bank that best targets those dimensions.
3. Ensure the selected question is not semantically redundant with already-asked questions.
4. Respect the aggression/sensitivity constraints.
5. Return the selected question along with a brief rationale (which dimensions it targets and why).

This approach is more flexible than a formula — the LLM can reason about cross-dimension interactions, detect contradictory signals that need clarification, and adapt question framing based on the user's demonstrated comfort level.

**Adaptive prompt bank examples** (organized by target dimension):

| Target dimension(s) | Example prompt |
|---|---|
| D2 (Relational Security) | "What does emotional safety mean to you in a close relationship?" |
| D3 (Conflict Style) | "Think of a time you disagreed with someone you care about. How did you handle it?" |
| D2 + D6 (Security + Self-Awareness) | "What's a pattern in your past relationships you've noticed about yourself?" |
| D5 (Value Gravity) | "If you could change one thing about how the world works, what would it be?" |
| D1 + D4 (Openness + Energy) | "Describe the best conversation you've ever had — what made it so good?" |
| D5 + D6 (Values + Self-Awareness) | "What's something you used to believe about love that you've since changed your mind about?" |
| D3 + D2 (Conflict + Security) | "What does forgiveness look like to you?" |

The prompt bank is provided to the LLM as context. The LLM may also **generate novel questions** if no bank candidate adequately covers the uncertain dimensions, as long as it adheres to the guardrails.

**Termination condition:** The session ends when either (a) 6 questions have been answered, or (b) the reasoning LLM determines all dimensions have sufficient confidence (all σᵢ < τ, default τ = 0.15).

#### Design guardrails

- **No leading questions** — prompts must not embed assumptions ("Why do you struggle with...").
- **No binary framing** — avoid yes/no structures; always invite narrative.
- **Trauma-aware** — prompts tagged with aggression > 0.6 are only used if no lower-aggression alternative covers the same dimension.
- **Cultural neutrality** — prompts avoid culture-specific idioms; reviewed for bias across gender, orientation, and background.


### B.3 Answer Model and Analysis

Each voice response is processed through a **three-stage LLM pipeline**. All understanding — both content and vocal behavior — is performed by LLMs, producing text-based intermediate outputs that are fused by a final reasoning LLM.

#### Architecture overview

```
Audio recording
    │
    ├──► [Stage 1] Boson AI ASR ──► transcript ──► Qwen LLM ──► Output1 (content analysis)
    │
    ├──► [Stage 2] Boson AI Higgs Audio v3.5 ──► Output2 (voice behavioral analysis)
    │
    └──► [Stage 3] Reasoning LLM (Output1 + Output2) ──► dimension scores, question selection, features
```

#### Stage 1: Content analysis (Output1)

**Step 1a — Transcription:**
Use **Boson AI ASR** to convert the audio recording into a timestamped text transcript.

**Step 1b — Semantic analysis with Qwen:**
Pass the transcript + question context to a **Qwen model** with a structured prompt:

```
You are analyzing a voice dating app response for psychological profiling.

Psychology ontology — six dimensions:
- D1 Emotional Openness: willingness to access and express inner emotional states
- D2 Relational Security: internal model of trust and comfort with intimacy
- D3 Conflict Style: how the person navigates disagreement and tension
- D4 Energy Orientation: degree of extraversion in social/romantic contexts
- D5 Value Gravity: core life priorities (security/tradition vs. novelty/achievement)
- D6 Self-Awareness: capacity to reflect on one's own patterns and motivations

Question asked: "{question}"
Transcript: "{transcript}"

Analyze the content and produce:
1. For each dimension D1–D6:
   - relevance: whether this response provides signal for this dimension (high/medium/low/none)
   - score: 0.0–1.0 (only if relevance is medium or high)
   - confidence: 0.0–1.0
   - evidence: specific quotes or reasoning
2. Key themes: list of 3–5 themes or values expressed
3. Linguistic observations:
   - self-reference density (high/medium/low)
   - hedging frequency (high/medium/low)
   - emotional vocabulary richness (high/medium/low)
   - abstract vs. concrete reasoning tendency
   - temporal orientation (past/present/future leaning)
```

**Output1** is the full structured text response from Qwen.

#### Stage 2: Voice behavioral analysis (Output2)

Pass the same audio recording to **Boson AI Higgs Audio v3.5**, which analyzes the voice signal and produces a **text-based behavioral description**. The model is prompted to describe:

```
Analyze the vocal characteristics of this audio recording. Describe:
1. Emotional tone: what emotions are conveyed (e.g., warmth, anxiety, confidence, hesitation, enthusiasm)
2. Speaking energy: pace (fast/moderate/slow), volume dynamics, overall energy level
3. Fluency patterns: presence of pauses, filled pauses (um, uh), self-corrections, speech flow
4. Voice quality: perceived warmth vs. tension, steadiness vs. variability
5. Engagement level: does the speaker sound invested, detached, guarded, or open
6. Notable shifts: any changes in tone, pace, or energy during the response (e.g., slowed down when discussing a specific topic)
```

**Output2** is the full text description from Higgs Audio. This replaces all traditional acoustic feature extraction (Praat, librosa, openSMILE) — the audio-native LLM captures the same vocal behavioral signals in natural language form.

#### Stage 3: Reasoning LLM — Fusion, scoring, and question selection

A **reasoning LLM** receives Output1 + Output2 together with the full session context, and performs all downstream tasks in a single call:

**Input to reasoning LLM:**
```
You are the Voice-Yourself reasoning engine for a dating app.

## Psychology Ontology
[full D1–D6 definitions from B.1]

## Session State
- Questions asked so far: [list of Q/A pairs with their Output1 + Output2]
- Current dimension estimates: [dᵢ, σᵢ for each dimension, or "no estimate yet"]

## Current Question Analysis
- Question: "{current_question}"
- Output1 (content analysis): {output1}
- Output2 (voice behavioral analysis): {output2}

## Tasks
1. **Dimension scoring**: For each dimension D1–D6, produce:
   - updated_score: 0.0–1.0 (integrating both content and vocal evidence)
   - updated_confidence: 0.0–1.0
   - reasoning: how content evidence and vocal evidence were weighed

2. **Running profile update**: Given all questions answered so far, produce
   the current best estimate for each dimension with overall confidence.
   Higher confidence from either content or vocal channel should
   increase dimension confidence. Contradictions between channels
   should be noted and reduce confidence.

3. **Next question selection** (if session not complete):
   - Identify the 2 most uncertain dimensions
   - Select or generate the next question (from prompt bank or novel)
   - Ensure it is not redundant with prior questions
   - Ensure it respects design guardrails (no leading, no binary, trauma-aware)
   - Provide rationale

4. **Session termination check**: Should the session end?
   (all dimensions confident enough, or 6 questions reached)
```

**Output of Stage 3:**
- Updated **v** = [d₁, ..., d₆] and **σ** = [σ₁, ..., σ₆]
- Next question to present (or termination signal)
- Per-dimension reasoning trace (stored for Vibe Report in Section D)

#### Why this works

The three-stage pipeline has key advantages over traditional acoustic feature engineering:

| Aspect | Traditional pipeline | LLM pipeline |
|---|---|---|
| Acoustic analysis | Custom DSP (Praat, librosa, openSMILE) requiring signal processing expertise | Higgs Audio produces behavioral descriptions directly from audio |
| Feature engineering | Manual mapping of acoustic features to dimensions | LLM reasons about vocal behavior in natural language |
| Fusion | Fixed α-weighted formula | Reasoning LLM weighs evidence contextually — can handle contradictions, nuance, cross-dimension interactions |
| Question selection | Scoring formula with pre-rated weights | LLM reasons about what's missing and why, can generate novel questions |
| Iteration speed | Requires retraining or re-tuning pipelines | Prompt engineering — iterate in minutes |
| Explainability | Numeric scores only | Full reasoning traces for every decision |

#### Output

The final Voice-Yourself feature vector passed to the matching system (Section A.2) is:

**v_voice** = [d₁, d₂, d₃, d₄, d₅, d₆] ∈ ℝ⁶

with companion uncertainty vector **σ** ∈ ℝ⁶ used by the matching system to discount low-confidence dimensions during similarity computation.

The reasoning traces from Stage 3 are stored per-user for the Vibe Report (Section D).


### B.4 Implementation Guidelines

High-level guidelines for implementing the three-stage LLM pipeline.

#### API dependencies

| Component | Provider | Role | Input | Output |
|---|---|---|---|---|
| ASR | Boson AI | Speech-to-text | Audio file (WAV/M4A) | Timestamped transcript (text) |
| Content LLM | Qwen (via API) | Semantic analysis | Transcript + question + prompt template | Output1 (structured text) |
| Audio LLM | Boson AI Higgs Audio v3.5 | Voice behavioral analysis | Audio file | Output2 (behavioral description text) |
| Reasoning LLM | Qwen or equivalent (via API) | Fusion, scoring, question selection | Output1 + Output2 + session state + ontology | Dimension scores, next question, reasoning |

All models are accessed via API. Utility functions for Boson AI (ASR + Higgs Audio) will be provided at implementation stage.

#### Processing flow per question

```
1. User records answer → audio file uploaded to backend
2. Backend dispatches two parallel API calls:
   a. Boson AI ASR → transcript
   b. Boson AI Higgs Audio v3.5 → Output2
3. On ASR completion: call Qwen with transcript → Output1
4. Call Reasoning LLM with Output1 + Output2 + session state → updated scores + next question
5. Store results; return next question to frontend (or session-complete signal)
```

Steps 2a and 2b run in **parallel** (independent API calls). Step 3 depends on 2a. Step 4 depends on both 2b and 3.

#### Data flow and storage

Per user, per question, store:
- `audio_url`: reference to the stored audio file
- `transcript`: ASR output
- `output1`: full content analysis text from Qwen
- `output2`: full behavioral analysis text from Higgs Audio
- `reasoning`: Stage 3 reasoning trace
- `dimension_snapshot`: [d₁..d₆, σ₁..σ₆] after this question

The cumulative session state (all prior question outputs) is passed to the Reasoning LLM at each step, enabling it to refine estimates incrementally.

#### Prompt management

- All prompt templates (for Qwen content analysis, Higgs Audio behavioral prompt, and Reasoning LLM fusion prompt) should be stored as **versioned configuration**, not hardcoded.
- The psychology ontology (D1–D6 definitions) is injected into prompts from a single source of truth to ensure consistency.
- The prompt bank for adaptive questions is stored as a structured list (JSON/YAML) that the Reasoning LLM receives as context.

#### Latency budget

| Step | Expected latency | Notes |
|---|---|---|
| Audio upload | ~1–2s | Depends on file size (~60s audio ≈ 1MB M4A) |
| ASR (Boson AI) | ~3–5s | Parallel with Higgs Audio |
| Higgs Audio v3.5 | ~3–8s | Parallel with ASR |
| Qwen content analysis | ~2–4s | Sequential after ASR |
| Reasoning LLM | ~3–5s | Sequential after both outputs ready |
| **Total** | **~10–15s** | User sees a "analyzing your response..." state |

This is acceptable UX — the user has just finished speaking and expects processing time. The frontend should show an analysis animation during this window.

#### Error handling

- If ASR fails: retry once; if still fails, prompt user to re-record (audio may be corrupt or silent).
- If Higgs Audio fails: proceed with Output1 only — the Reasoning LLM can still score dimensions from content, with reduced confidence on acoustic-dependent dimensions (D4 especially).
- If Reasoning LLM fails: retry once; if still fails, use Output1 alone with a simplified scoring prompt as fallback.
- All API calls should have timeouts (30s) and circuit-breaker patterns for resilience.


## C. Matching System

The matching system retrieves the **top 15 most compatible candidates** for a given user by computing similarity over composite feature vectors. It applies hard filters first (categorical constraints), then ranks the remaining pool by vector similarity across interest and voice-yourself features.

### C.1 Composite Feature Vector

Each user's profile is represented as three sub-vectors (from Section A.2):

| Sub-vector | Source | Representation | Dimensionality |
|---|---|---|---|
| **v_cat** | Categorical features | One-hot encoding (age bucket, gender, intent, location region) | ~30–50 (varies by category cardinality) |
| **v_int** | Interests | LLM text encoder embedding, L2-normalized | 768 or 1024 (depends on encoder) |
| **v_voice** | Voice-Yourself dimensions | [d₁, d₂, d₃, d₄, d₅, d₆] from Section B | 6 |

The categorical sub-vector is **not used for similarity ranking** — it is used only for hard filtering (see C.2). The ranking similarity is computed over **v_int** and **v_voice** only.

### C.2 Hard Filters

Before similarity computation, candidates are filtered by categorical constraints. A candidate must pass **all** filters to enter the ranking pool:

| Filter | Logic |
|---|---|
| **Gender preference** | Candidate's gender ∈ user's preferred gender set AND user's gender ∈ candidate's preferred gender set (mutual) |
| **Age preference** | Candidate's age ∈ [user's min_age, user's max_age] AND user's age ∈ [candidate's min_age, candidate's max_age] (mutual) |
| **Location** | Candidate is within the user's geofence radius (configurable, default 50 km) |
| **Already seen** | Candidate has not been previously swiped on (left or right) by the user |
| **Voice-Yourself completion** | Candidate has completed at least 2 voice prompts (minimum for dimension estimates) |

### C.3 Similarity Computation

For each candidate passing the hard filters, compute a weighted similarity score:

**score(user, candidate)** = β · sim_interest(user, candidate) + (1 − β) · sim_voice(user, candidate)

where β controls the relative weight of interest similarity vs. voice similarity. Default β = 0.3 (voice-first philosophy — vocal/psychological compatibility is weighted higher).

#### Interest similarity

Cosine similarity between L2-normalized interest embeddings:

sim_interest(u, c) = v_int(u) · v_int(c)

Since both vectors are L2-normalized, this is equivalent to the dot product and produces a score ∈ [-1, 1], rescaled to [0, 1]:

sim_interest(u, c) = (v_int(u) · v_int(c) + 1) / 2

#### Voice similarity

Confidence-weighted Euclidean distance over the six psychological dimensions, converted to a similarity score:

For each dimension i, the effective weight accounts for uncertainty in **both** users:

wᵢ = (1 − σᵢ(u)) · (1 − σᵢ(c))

This down-weights dimensions where either user has low confidence. The weighted distance is:

dist_voice(u, c) = √(Σᵢ wᵢ · (dᵢ(u) − dᵢ(c))²) / √(Σᵢ wᵢ)

Converted to similarity:

sim_voice(u, c) = 1 − dist_voice(u, c)

Since each dᵢ ∈ [0, 1], the maximum possible distance is 1.0, so sim_voice ∈ [0, 1].

### C.4 Ranking and Retrieval

1. **Filter** the candidate pool using hard filters (C.2).
2. **Compute** score(user, candidate) for each remaining candidate (C.3).
3. **Sort** by score descending.
4. **Return top 15** candidates as the match deck batch.

#### Batch generation

A new batch of 15 is generated when:
- The user first opens the Match tab (initial load)
- The user exhausts the current deck (all 15 swiped)
- The user explicitly refreshes

Previously returned candidates that were **not swiped** may reappear in future batches. Swiped candidates (left or right) are permanently excluded via the hard filter.

### C.5 Version 1.0 Simplifications

For v1.0, the matching system is deliberately simple:

| Aspect | v1.0 approach | Future consideration |
|---|---|---|
| **Retrieval** | Brute-force scan over all candidates | ANN index (FAISS/ScaNN) when user base grows beyond ~10K |
| **Interest embedding** | Single embedding per user from concatenated interest keywords | Per-interest embeddings with aggregation strategies |
| **Voice similarity** | Euclidean distance on 6 dimensions | Learned similarity metric from match outcome data |
| **β weight** | Fixed at 0.3 | Personalized per user based on their engagement patterns |
| **Freshness** | No time decay | Boost recently active users, decay stale profiles |
| **Mutual compatibility** | score(u, c) only — one directional | Average of score(u,c) and score(c,u) for bidirectional ranking |
| **Diversity** | None — pure similarity ranking | MMR (Maximal Marginal Relevance) to ensure varied profiles in a batch |


## D. Vibe Progress

Vibe Progress tracks **how a connection between two matched users is evolving** over time by analyzing their ongoing message and call history. It powers three user-facing features:

1. **Resonance Meter** (FR-15) — a per-thread progress bar shown at the top of each chat
2. **Call Summary** (FR-16) — AI-generated summary after each call
3. **Vibe Check Report** (FR-20) — weekly/monthly personal insight report

The analysis pipeline mirrors Section B's three-stage LLM approach, applied to accumulated conversation data rather than a single prompt response.

### D.1 Input: Message and Call History

For each matched pair (user A, user B), the system collects:

| Source | Data |
|---|---|
| Voice messages | Audio files exchanged in the chat thread |
| Text messages | Any typed messages in the thread |
| Calls | Audio recordings or metadata (duration, who initiated, timestamps) of calls in Call mode |

Each interaction has a timestamp, sender, and type (voice_note, text, call).

### D.2 Analysis Pipeline

When a Vibe Progress update is triggered, the message history is processed through a two-stage pipeline, analogous to Section B:

```
Message/Call history
    │
    ├──► Voice messages & calls ──► [Stage 1] Boson AI ASR ──► transcripts
    │                                                              │
    │                                                              ├──► Qwen LLM ──► Output1 (content analysis)
    │
    ├──► Voice messages & calls ──► [Stage 2] Boson AI Higgs Audio v3.5 ──► Output2 (behavioral analysis)
    │
    ├──► Text messages ──► (direct input, no ASR needed)
    │
    └──► [Stage 3] Reasoning LLM (Output1 + Output2 + text messages) ──► Vibe scores, summaries, report
```

#### Stage 1: Content analysis (Output1)

**Step 1a — Transcription:**
Use **Boson AI ASR** to transcribe all voice messages and call recordings into text. Text messages are included directly without transcription.

**Step 1b — Conversation analysis with Qwen:**
Pass the assembled transcript (all messages in chronological order, labeled by sender) to **Qwen** with a structured prompt:

```
You are analyzing the conversation history between two matched users on a voice-first dating app.

## Conversation History
[chronological transcript with sender labels and timestamps]

Analyze the conversation and produce:
1. **Emotional trajectory**: how has the emotional tone evolved over the conversation?
   (e.g., guarded → warming up → open, or enthusiastic → stalling)
2. **Topic depth**: are topics staying surface-level or deepening?
   List key topics discussed and their depth (surface/moderate/deep).
3. **Reciprocity**: is the conversation balanced? Who initiates more?
   Who shares more personal content? Is vulnerability reciprocated?
4. **Connection signals**: identify specific moments of:
   - Humor or playfulness
   - Vulnerability or personal disclosure
   - Active listening (referencing what the other said)
   - Emotional mirroring
   - Tension, avoidance, or disengagement
5. **Communication style compatibility**: are their styles meshing?
   (e.g., one is verbose and one terse, or both match energy)
```

**Output1** is the structured text analysis from Qwen.

#### Stage 2: Voice behavioral analysis (Output2)

Pass voice messages and call recordings to **Boson AI Higgs Audio v3.5** for behavioral analysis. Unlike Section B (which analyzes one recording at a time), here the model is prompted to describe **relational vocal dynamics**:

```
Analyze the vocal characteristics across these audio messages between two speakers.

For each speaker, describe:
1. Emotional warmth: does their voice convey warmth, interest, or detachment?
2. Energy trend: is their energy increasing, stable, or declining over the exchanges?
3. Comfort level: do they sound more relaxed or more guarded over time?
4. Engagement markers: laughter, exclamations, trailing off, interrupting themselves

Between speakers, describe:
5. Energy matching: do they mirror each other's pace, volume, enthusiasm?
6. Vocal chemistry: do their voices complement each other (e.g., one calm + one animated)?
7. Notable moments: any voice messages where a speaker's tone noticeably shifted
```

**Output2** is the text behavioral description from Higgs Audio.

#### Stage 3: Reasoning LLM — Vibe scoring

A **reasoning LLM** receives Output1 + Output2 + the raw text messages and produces the Vibe Progress outputs:

```
You are the Vibe Progress engine for a dating app.

## Input
- Output1 (content analysis): {output1}
- Output2 (voice behavioral analysis): {output2}
- Text messages: {text_messages}
- Thread metadata: {message_count, voice_minutes, call_count, days_since_match}

## Tasks

1. **Resonance Score**: Compute a score from 0 to 100 representing the current
   connection strength. Consider:
   - Emotional depth progression
   - Reciprocity and balance
   - Vocal warmth and engagement trends
   - Frequency and consistency of communication
   Output: score (0–100), trend (rising/stable/cooling), reasoning

2. **Vibe Stage**: Classify the connection into a stage:
   - Spark (0–25): initial exchanges, surface-level, getting-to-know
   - Warming (25–50): some personal sharing, humor emerging, growing comfort
   - Resonating (50–75): genuine connection signals, vulnerability exchanged, deep topics
   - Soulmate Zone (75–100): strong emotional safety, natural flow, high compatibility evidence
   Output: stage label, evidence summary

3. **Connection insights**: 2–3 sentence summary of the connection for each user
   (personalized — what this connection seems to bring out in them).

4. **Call summary** (if new call data): summarize the call — key topics, emotional
   highlights, and any notable moments.
```

### D.3 Trigger and Frequency

Vibe Progress analysis is **not run on every message** — it is triggered at specific intervals to manage cost and latency:

| Trigger | What happens |
|---|---|
| **After every 5 voice messages** exchanged (combined from both users) | Full pipeline run → update Resonanfixce Score |
| **After every call** | Call-specific analysis → call summary + score update |
| **Daily batch** (for active threads) | Lightweight re-score for threads with any activity in the last 24h |
| **User requests Vibe Check Report** | Aggregate analysis across all active connections |

The Resonance Score is cached and displayed immediately in the UI. The full analysis only runs at trigger points.

### D.4 Vibe Check Report (FR-20)

A weekly or monthly personal report generated per user across **all their active connections**. The reasoning LLM receives:

- Vibe Progress data from all active threads
- The user's Voice-Yourself profile (D1–D6 dimensions from Section B)
- Historical resonance score trends

Prompt to reasoning LLM:

```
Generate a personal Vibe Check Report for this user.

## User's Voice-Yourself Profile
[D1–D6 scores and key traits from Section B]

## Active Connections
[For each connection: resonance score, stage, trend, key insights]

## Report Tasks
1. **Pattern recognition**: What kind of people does this user resonate with?
   (e.g., "You connect most with people who speak thoughtfully and value emotional safety.")
2. **Communication style insight**: What does the user's messaging behavior reveal?
   (e.g., "You tend to open up more in voice notes than text — your warmth comes through when you speak.")
3. **Growth observation**: How has the user's engagement evolved over time?
4. **Encouragement**: One actionable suggestion to deepen connections.
   (e.g., "Try asking a follow-up question about something your match mentioned — it shows you're listening.")

Keep the tone warm, non-judgmental, and conversational. This is a vibe report, not a clinical assessment.
```

### D.5 Resonance Meter Levels and Unlocks

The Resonance Score (0–100) maps to visual levels in the UI and unlocks features:

| Score range | Stage | Visual | Unlock |
|---|---|---|---|
| 0–25 | Spark | 1 bar, dim glow | Basic chat |
| 25–50 | Warming | 2 bars, amber glow | Audio Themes (fun voice filters for calls) |
| 50–75 | Resonating | 3 bars, warm pulse | Shared voice filters for Call mode |
| 75–100 | Soulmate Zone | 4 bars, full radiance | Full Vibe Report comparison between both users |

### D.6 Implementation Notes

- **ASR and Higgs Audio calls follow the same API pattern** as Section B.4 — same providers, same error handling, same timeout policies.
- **Message history is scoped** — only process messages since the last analysis run (incremental), not the entire thread each time. The reasoning LLM receives the previous Vibe Progress state plus new messages.
- **Storage per thread**: `resonance_score`, `vibe_stage`, `last_analysis_at`, `insights_json`, `call_summaries_json`.
- **Privacy**: Vibe Progress data is per-connection, not shared with other users. Each user only sees their own insights and the shared Resonance Score.
- **Cost control**: The daily batch job only processes threads with new activity. Inactive threads are skipped. The weekly Vibe Check Report is generated on-demand or on a schedule, not continuously.