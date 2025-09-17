🗺️ Roadmap for The Faulkner Machine (working title: As I Lay Coding)


Phase 0: Project Scaffolding (Day 1–2)
- Set up GitHub repo (so the devlog has receipts).
- Decide: Python + Streamlit (quick UI) OR Flask (more customizable).
- Prep a small corpus of Faulkner + your own test strings.


Phase 1: Recursive Text Loops
- Build a single loop that:
- Takes input → mutates it with repetition, word shuffling, sentence elongation.
- Option to “nest” → one loop inside another (simulating Rosa/Quentin/father voices).
- Deliverable: a prototype that can generate sentences longer than 500 words.


Phase 2: The Four Voices (Columns of Sutpen’s House)
- Implement 4 independent loops:
-- Rosa: vitriol, rage, “corrupting” syntax with sharp cuts.
-- Father: shaky, second-hand, reacting to Rosa’s strings.
-- Quentin: delirious, random insertions, syntax collapse.
-- Shreve: drops questions like bricks (“But why? How could he?”).
-Output → each voice in a column of text.
-Deliverable: UI mockup with static text in columns.


Phase 3: Cross-Contamination (The Incest Mechanism)
- Each loop pulls random substrings from one of the other loops.
- Text starts to blur → lines repeat, mutate, echo.
- Deliverable: a prototype where the four voices bleed into one another.


Phase 4: Hallucination Mode (1288-Word Switch)
- Add Sentence Length Dial (0–1288).
- At max, text generation runs recursive loops until it reaches ~1288 words in a single block.
- Add “Never Stop” switch → text output keeps unfurling endlessly until killed.
- Deliverable: the first truly hostile version.


Phase 5: The Inheritance Breaker (UI Polish)
- Columns warp/distort as text grows (CSS glitch filters or animated fonts).
- Add audio element → your recorded screams/whispers woven in when output exceeds certain thresholds.
- Visuals: columns could “crack” when inheritance burden becomes too great.
- Deliverable: an immersive horror-art installation, not just code.


Phase 6: Documentation & Performance
- Write devlog entries for each phase (blog + Mastodon snippets).
- Record screencaps → cut into YouTube devlog, interspersed with your commentary.
- Capstone performance → read or run the machine at Faulkner’s grave.
