"""Small reusable rendering helpers shared across screens."""

import streamlit as st
from game.levels import LEVELS, TOTAL_LEVELS


def render_status_bar(state):
    lives_str = "❤️" * state["lives"] + "🤍" * (3 - state["lives"]) if state["lives"] <= 3 else "❤️" * state["lives"]
    streak_str = f"🔥{state['streak']}" if state["streak"] > 0 else "—"
    html = f"""
    <div class="kq-statbar">
        <div class="kq-stat"><span class="kq-stat-value">{state['score']}</span><span class="kq-stat-label">Score</span></div>
        <div class="kq-stat"><span class="kq-stat-value">{lives_str}</span><span class="kq-stat-label">Lives</span></div>
        <div class="kq-stat"><span class="kq-stat-value kq-streak">{streak_str}</span><span class="kq-stat-label">Streak</span></div>
        <div class="kq-stat"><span class="kq-stat-value">💡{state['hints_remaining']}</span><span class="kq-stat-label">Hints</span></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_quest_trail(current_level: int):
    """The signature waypoint trail: one node per level, connecting lines show progress."""
    nodes_html = []
    for lvl in LEVELS:
        n = lvl["number"]
        if n < current_level:
            cls = "done"
            content = "✓"
        elif n == current_level:
            cls = "current"
            content = str(n)
        else:
            cls = ""
            content = str(n)
        nodes_html.append(f'<div class="kq-trail-node {cls}" title="{lvl["name"]}">{content}</div>')
        if n < TOTAL_LEVELS:
            line_cls = "done" if n < current_level else ""
            nodes_html.append(f'<div class="kq-trail-line {line_cls}"></div>')

    st.markdown(f'<div class="kq-trail">{"".join(nodes_html)}</div>', unsafe_allow_html=True)


def render_level_dots(total: int, current_index: int):
    """Dot progress within the current level's question set."""
    dots = []
    for i in range(total):
        if i < current_index:
            cls = "done"
        elif i == current_index:
            cls = "current"
        else:
            cls = ""
        dots.append(f'<div class="kq-dot {cls}"></div>')
    st.markdown(f'<div class="kq-dots">{"".join(dots)}</div>', unsafe_allow_html=True)


def render_tags(category: str, difficulty: str):
    st.markdown(
        f'<span class="kq-tag kq-tag-cat">{category}</span>'
        f'<span class="kq-tag kq-tag-diff">{difficulty}</span>',
        unsafe_allow_html=True,
    )


def render_timer_bar(ratio):
    """ratio: float 0-1 remaining, or None if untimed. Updates on each rerun."""
    if ratio is None:
        return
    pct = max(0, min(100, int(ratio * 100)))
    warn_cls = "warn" if ratio < 0.35 else ""
    seconds_label = "Time running low!" if ratio < 0.35 else "Time remaining"
    st.markdown(
        f'<div class="kq-timer-track"><div class="kq-timer-fill {warn_cls}" style="width:{pct}%;"></div></div>'
        f'<div style="font-size:0.75rem;color:var(--kq-text-dim);margin-top:-0.6rem;margin-bottom:0.6rem;">{seconds_label}</div>',
        unsafe_allow_html=True,
    )


def render_xp_bar(rank_info):
    pct = int(rank_info["progress"] * 100)
    next_label = rank_info["next_rank"] or "Max Rank"
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:var(--kq-text-dim);margin-bottom:0.3rem;">
            <span><b style="color:var(--kq-accent-soft)">{rank_info['rank']}</b></span>
            <span>{rank_info['xp']} XP → {next_label}</span>
        </div>
        <div class="kq-xp-track"><div class="kq-xp-fill" style="width:{pct}%;"></div></div>
        """,
        unsafe_allow_html=True,
    )
