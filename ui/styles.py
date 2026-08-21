"""
Design tokens and injected CSS for Knowledge Quest.

Theme concept: a night-sky "expedition" — the player charts a trail of
knowledge waypoints. Signature element is the horizontal quest trail
(see components.render_quest_trail) rather than a generic progress bar.

Tokens:
  Background   #12142B  (deep indigo night)
  Surface      #1C2044  (card background)
  Surface-alt  #242952  (raised / hover surface)
  Accent       #E8A33D  (brass / lantern glow - primary actions, highlights)
  Accent-soft  #F2C572  (lighter brass for text-on-dark accents)
  Spark        #4FD1C5  (teal - success / correct)
  Danger       #E85D5D  (wrong / lives lost)
  Text         #F5F3EC  (warm off-white)
  Text-dim     #A8ACC9  (secondary text)

  Display font: 'Space Grotesk' (headings, score numbers, buttons)
  Body font:    'Inter' (body copy)
  Mono font:    'JetBrains Mono' (stats, timer, score digits)
"""

import streamlit as st

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">

<style>
:root {
    --kq-bg: #12142B;
    --kq-surface: #1C2044;
    --kq-surface-alt: #242952;
    --kq-accent: #E8A33D;
    --kq-accent-soft: #F2C572;
    --kq-spark: #4FD1C5;
    --kq-danger: #E85D5D;
    --kq-text: #F5F3EC;
    --kq-text-dim: #A8ACC9;
    --kq-border: rgba(232,163,61,0.22);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(ellipse at top, #1a1e42 0%, #12142B 55%, #0d0f22 100%);
    color: var(--kq-text);
}

#MainMenu, header[data-testid="stHeader"], footer {visibility: hidden; height: 0;}
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 560px;
}

h1, h2, h3, .kq-display {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.01em;
}

/* ---------- Buttons (touch-friendly, min 48px tall) ---------- */
div[data-testid="stButton"] > button {
    width: 100%;
    min-height: 52px;
    border-radius: 14px;
    border: 1.5px solid var(--kq-border);
    background: var(--kq-surface);
    color: var(--kq-text);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.02rem;
    transition: transform 0.08s ease, border-color 0.15s ease, background 0.15s ease;
}
div[data-testid="stButton"] > button:hover {
    border-color: var(--kq-accent);
    background: var(--kq-surface-alt);
    color: var(--kq-accent-soft);
}
div[data-testid="stButton"] > button:active {
    transform: scale(0.98);
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, var(--kq-accent) 0%, #d6862a 100%);
    border: none;
    color: #1a1206;
    box-shadow: 0 4px 14px rgba(232,163,61,0.28);
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    filter: brightness(1.06);
    color: #1a1206;
}

/* ---------- Cards ---------- */
.kq-card {
    background: var(--kq-surface);
    border: 1px solid var(--kq-border);
    border-radius: 18px;
    padding: 1.3rem 1.2rem;
    margin-bottom: 1rem;
}
.kq-hero {
    text-align: center;
    padding: 1.6rem 1rem 1.2rem 1rem;
}
.kq-hero-title {
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(120deg, var(--kq-accent-soft), var(--kq-accent) 60%, var(--kq-spark));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin: 0.2rem 0 0.1rem 0;
}
.kq-hero-sub {
    color: var(--kq-text-dim);
    font-size: 0.92rem;
    margin-bottom: 0;
}
.kq-compass {
    font-size: 2.4rem;
    filter: drop-shadow(0 0 10px rgba(232,163,61,0.5));
}

/* ---------- Top status bar ---------- */
.kq-statbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--kq-surface);
    border: 1px solid var(--kq-border);
    border-radius: 14px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.9rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.92rem;
}
.kq-stat { display:flex; flex-direction:column; align-items:center; min-width: 44px;}
.kq-stat-label { font-size: 0.62rem; color: var(--kq-text-dim); font-family:'Inter',sans-serif; letter-spacing:0.04em; text-transform:uppercase;}
.kq-stat-value { font-weight: 700; color: var(--kq-text); }

/* ---------- Quest trail (signature element) ---------- */
.kq-trail {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    margin: 0.6rem 0 1.1rem 0;
    padding: 0 4px;
}
.kq-trail-node {
    width: 34px; height: 34px;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
    border: 1.5px solid var(--kq-border);
    color: var(--kq-text-dim);
    background: var(--kq-surface);
}
.kq-trail-node.done {
    background: var(--kq-spark);
    color: #0a2624;
    border-color: var(--kq-spark);
}
.kq-trail-node.current {
    background: var(--kq-accent);
    color: #1a1206;
    border-color: var(--kq-accent);
    box-shadow: 0 0 0 4px rgba(232,163,61,0.22);
}
.kq-trail-line {
    flex: 1;
    height: 2px;
    background: var(--kq-border);
    min-width: 8px;
}
.kq-trail-line.done { background: var(--kq-spark); opacity: 0.6; }

/* within-level dot progress */
.kq-dots { display:flex; gap:6px; justify-content:center; margin-bottom: 0.9rem; }
.kq-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--kq-border); }
.kq-dot.done { background: var(--kq-spark); }
.kq-dot.current { background: var(--kq-accent); width: 12px; height: 12px; }

/* ---------- Tags / badges ---------- */
.kq-tag {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin-right: 0.4rem;
}
.kq-tag-cat { background: rgba(79,209,197,0.14); color: var(--kq-spark); }
.kq-tag-diff { background: rgba(232,163,61,0.16); color: var(--kq-accent-soft); }

/* ---------- Timer ---------- */
.kq-timer-track {
    width: 100%; height: 8px; border-radius: 5px;
    background: var(--kq-surface-alt);
    overflow: hidden; margin: 0.5rem 0 0.9rem 0;
}
.kq-timer-fill {
    height: 100%; border-radius: 5px;
    background: linear-gradient(90deg, var(--kq-spark), var(--kq-accent));
    transition: width 0.3s ease;
}
.kq-timer-fill.warn { background: linear-gradient(90deg, var(--kq-accent), var(--kq-danger)); }

/* ---------- Feedback ---------- */
.kq-feedback {
    border-radius: 16px;
    padding: 1rem 1.1rem;
    margin: 0.8rem 0;
    font-weight: 600;
}
.kq-feedback.correct { background: rgba(79,209,197,0.14); border: 1px solid rgba(79,209,197,0.4); color: var(--kq-spark); }
.kq-feedback.wrong { background: rgba(232,93,93,0.14); border: 1px solid rgba(232,93,93,0.4); color: #ff9c9c; }
.kq-explain { color: var(--kq-text-dim); font-weight: 400; font-size: 0.9rem; margin-top: 0.4rem; }

/* ---------- Lives / streak ---------- */
.kq-lives { font-size: 1.05rem; letter-spacing: 2px; }
.kq-streak { color: var(--kq-accent-soft); font-weight: 700; }

/* progress bar (xp) */
.kq-xp-track {
    width: 100%; height: 10px; border-radius: 6px;
    background: var(--kq-surface-alt); overflow: hidden;
}
.kq-xp-fill {
    height: 100%; border-radius: 6px;
    background: linear-gradient(90deg, #6a5acd, var(--kq-spark));
}

hr { border-color: var(--kq-border) !important; }

/* Radio / selectbox touch targets */
div[role="radiogroup"] label { padding: 0.35rem 0; }

@media (max-width: 400px) {
    .kq-hero-title { font-size: 1.6rem; }
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
