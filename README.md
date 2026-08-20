# 🧭 Knowledge Quest — The Ultimate Brain Challenge

A mobile-first knowledge puzzle game built with Streamlit. Players progress
through 5 increasingly difficult levels, answering multiple-choice
questions across six categories, with lives, hints, streak bonuses, and a
speed-based scoring system.

This is the **MVP build**: Knowledge Challenge mode only. Logic Lab, Memory
Vault, Mystery Puzzle, Daily Challenge, achievements, and full statistics
are planned as follow-up milestones — the architecture below was built so
those can be added without rewriting the core engine.

---

## Features (MVP)

- Mobile-first, touch-friendly UI (large buttons, responsive layout, no
  horizontal scrolling)
- 5 levels with progressively increasing difficulty (Beginner → Master)
- 6 knowledge categories + a "Mixed" mode, 72-question starter bank
- Score system with difficulty weighting, speed bonus, and streak bonus
- 3 lives for the run, 3 hints (each removes one wrong option at half
  points for that question)
- Timer introduced gradually from Level 2 onward
- Immediate answer feedback with a short educational explanation
- XP + rank progress bar (foundation for the full rank/achievement system)
- Results screen with score, accuracy, best streak, and rank
- Anti-repetition question selection with safe fallbacks for small pools

---

## Project Structure

```
knowledge_quest/
├── app.py                    # Streamlit entry point / screen router
├── requirements.txt
├── README.md
├── .streamlit/config.toml    # theme
│
├── game/
│   ├── state.py               # session state machine (single source of truth)
│   ├── player.py               # XP -> rank mapping
│   ├── scoring.py               # pure scoring functions
│   ├── levels.py                # level/difficulty/category configuration
│   ├── challenge_base.py       # abstract interface future modes implement
│   ├── question_bank.py        # loads + selects questions, anti-repeat
│   └── modes/
│       └── knowledge.py         # Knowledge Challenge mode (MVP mode)
│
├── data/
│   └── questions.json          # 72 starter questions, easy to extend
│
├── ui/
│   ├── styles.py                # design tokens + injected CSS
│   ├── components.py            # status bar, quest trail, timer bar, etc.
│   └── screens.py               # menu / setup / playing / results renderers
│
└── tests/
    └── test_engine.py           # unit tests for scoring, ranks, levels, question bank
```

**Why this structure:** `game/` has zero UI knowledge — `state.py` is the
only place that mutates game state, and `ui/screens.py` only reads state
and calls `state.py` functions. Adding a new mode later means writing a
new file in `game/modes/` that implements `ChallengeMode`, adding it to the
`MODES` dict in `state.py`, and adding its questions to `data/` — the
screens, scoring, lives, streak, and level systems stay untouched.

---

## Installation (local)

Requires Python 3.9+.

```bash
cd knowledge_quest
pip install -r requirements.txt
```

## Running locally

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`). Open
it in a browser — including your phone's browser if it's on the same
Wi-Fi network, using the "Network URL" Streamlit also prints.

## Running tests

The core logic (scoring, ranks, levels, question selection) has no
Streamlit dependency and can be tested standalone:

```bash
python -m pytest tests/ -v
# or, without pytest:
python tests/test_engine.py
```

23 tests cover scoring rules, hint/speed/streak bonuses, rank thresholds,
difficulty progression, and question-bank edge cases (depleted pools,
category filtering, anti-repetition).

---

## Controls

Touch/click only — no keyboard required. Every interactive element is a
full-width button sized for comfortable tapping on a phone screen.

## Game Rules

- Answer 5 questions per level to advance. 5 levels total.
- You have 3 lives for the whole run; a wrong or timed-out answer costs one.
- You have 3 hints for the run; each removes one incorrect option and
  halves the points available for that question.
- From Level 2 onward, questions are timed (30s → 15s as levels increase).
  If time runs out, it's automatically scored as incorrect.
- A streak of 3+ correct answers in a row earns a bonus on top of the
  base score.
- **Timer implementation note:** Streamlit reruns the whole app on each
  interaction rather than running a live server loop, so there is no
  ticking JS clock. The countdown bar updates on every interaction (e.g.
  using a hint) and is enforced by checking elapsed time the moment you
  submit an answer — a deliberate, documented tradeoff rather than a
  faked feature.

---

## Deployment (public URL, no install required for players)

**Recommended platform: [Streamlit Community Cloud](https://streamlit.io/cloud)**
— free, built specifically for Streamlit apps, and gives you a public
`*.streamlit.app` URL.

1. Push this project to a public (or private, with Streamlit Cloud
   connected) GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with
   GitHub, and click "New app".
3. Select the repository, branch, and set the main file path to `app.py`.
4. Click "Deploy". Streamlit Cloud installs `requirements.txt`
   automatically.
5. You'll get a URL like `https://your-app-name.streamlit.app` — this is
   the link you can send to anyone. It opens directly in a mobile browser,
   no installation needed.

No environment variables or secrets are required for this MVP. Nothing in
this project depends on local file paths outside the repo, local-only
services, or hardware — it's deployment-ready as-is.

### Deployment checklist

- [x] No absolute local file paths (`question_bank.py` resolves paths
      relative to the project using `Path(__file__)`)
- [x] No local-only services or databases (all state lives in
      `st.session_state`, reset each session — no persistence needed for MVP)
- [x] `requirements.txt` present and minimal (Streamlit only)
- [x] `.streamlit/config.toml` sets the theme so it renders consistently
      on Streamlit Cloud

---

## Known MVP Limitations (by design, not oversight)

- Progress and stats reset when the browser tab/session ends — no
  account system or persistent save yet (planned: Section 15/16 of the
  spec, once a storage layer is added).
- Only Knowledge Challenge mode is implemented. Logic Lab, Memory Vault,
  Mystery Puzzle, and Daily Challenge are next.
- No sound effects yet (Streamlit audio is limited; will revisit with a
  lightweight approach if it doesn't hurt mobile load time).
- Achievements and the full 7-tier rank fanfare are not built yet — XP
  and rank progress are tracked and shown, which is the foundation for
  achievements to hook into.

## Future Improvements

- Add remaining game modes (Logic Lab, Memory Vault, Mystery Puzzle, Daily Challenge)
- Achievements system
- Full player statistics screen with per-category accuracy
- Difficulty adaptation based on performance
- Expand question bank well beyond 72 questions
- Optional sound effects with mute control
- Persistent save (e.g. lightweight JSON or database) for daily streaks
