"""Screen renderers. Read game state, call game.state functions on interaction, never mutate state directly."""

import streamlit as st

from game import state as gstate
from game.levels import (
    get_level, TOTAL_LEVELS, MODE_CATEGORIES, MODE_LABELS, LANGUAGES,
)
from game.player import get_rank
from ui.components import (
    render_status_bar, render_quest_trail, render_level_dots,
    render_tags, render_timer_bar, render_xp_bar,
)


# ---------------------------------------------------------------- MENU
def render_menu():
    state = gstate.gs()

    st.markdown(
        """
        <div class="kq-hero">
            <div class="kq-compass">🧭</div>
            <div class="kq-hero-title kq-display">Knowledge Quest</div>
            <p class="kq-hero-sub">The Ultimate Brain Challenge</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_quest_trail(current_level=1)

    st.markdown('<div class="kq-card">', unsafe_allow_html=True)
    st.markdown(
        "5 levels. Two challenge modes. One trail of questions that gets "
        "harder the further you go."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.8rem;color:var(--kq-text-dim);margin-bottom:0.3rem;">LANGUAGE</p>',
                unsafe_allow_html=True)
    lang_cols = st.columns(2)
    for i, (code, label) in enumerate(LANGUAGES.items()):
        with lang_cols[i]:
            is_selected = state["language"] == code
            btn_label = f"✓ {label}" if is_selected else label
            if st.button(btn_label, key=f"lang_{code}",
                         type="primary" if is_selected else "secondary"):
                gstate.set_language(code)
                st.rerun()

    st.markdown('<p style="font-size:0.8rem;color:var(--kq-text-dim);margin:0.7rem 0 0.3rem 0;">MODE</p>',
                unsafe_allow_html=True)
    mode_cols = st.columns(2)
    mode_icons = {"knowledge": "🧠", "logic": "🧩"}
    for i, (mode_key, label) in enumerate(MODE_LABELS.items()):
        with mode_cols[i]:
            is_selected = state["mode"] == mode_key
            btn_label = f"✓ {mode_icons[mode_key]} {label}" if is_selected else f"{mode_icons[mode_key]} {label}"
            if st.button(btn_label, key=f"mode_{mode_key}",
                         type="primary" if is_selected else "secondary"):
                gstate.set_mode(mode_key)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Quest", type="primary", key="menu_start"):
        gstate.go_to_setup()
        st.rerun()

    with st.expander("How to play"):
        st.markdown(
            "- Answer 5 questions per level to advance.\n"
            "- You have **3 lives** for the whole run — a wrong answer costs one.\n"
            "- You get **3 hints** — each removes one wrong option, at half points for that question.\n"
            "- From Level 2 onward, questions are timed. Answer fast for a speed bonus.\n"
            "- Build a streak of 3+ correct answers in a row for bonus points.\n"
            "- **Knowledge Challenge** tests general knowledge across 6 categories.\n"
            "- **Logic Lab** tests sequences, patterns, deduction and math reasoning."
        )


# ---------------------------------------------------------------- SETUP
def render_setup():
    state = gstate.gs()
    mode_categories = MODE_CATEGORIES[state["mode"]]

    st.markdown(
        f'<p style="font-size:0.8rem;color:var(--kq-text-dim);margin-bottom:0.1rem;">'
        f'{MODE_LABELS[state["mode"]].upper()} · {LANGUAGES[state["language"]].upper()}</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<h2 class="kq-display">Choose your category</h2>', unsafe_allow_html=True)
    st.caption("Mixed draws from every category. Pick a specialty to focus your run.")

    if "setup_category" not in st.session_state or st.session_state.setup_category not in mode_categories:
        st.session_state.setup_category = "Mixed"

    cols = st.columns(2)
    for i, cat in enumerate(mode_categories):
        col = cols[i % 2]
        with col:
            is_selected = st.session_state.setup_category == cat
            label = f"✓ {cat}" if is_selected else cat
            if st.button(label, key=f"cat_{cat}",
                         type="primary" if is_selected else "secondary"):
                st.session_state.setup_category = cat
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    level1 = get_level(1)
    st.markdown(
        f'<div class="kq-card">'
        f'<b>Level 1 — {level1["name"]}</b><br>'
        f'<span style="color:var(--kq-text-dim);font-size:0.88rem;">'
        f'{level1["questions_per_level"]} questions · {level1["difficulty"].title()} difficulty · no timer</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.button("🧭 Begin Level 1", type="primary", key="setup_begin"):
        gstate.start_game(st.session_state.setup_category)
        st.rerun()

    if st.button("← Back", key="setup_back"):
        gstate.go_to_menu()
        st.rerun()


# ---------------------------------------------------------------- PLAYING
def render_playing():
    state = gstate.gs()

    if state["current_question"] is None:
        st.error("No question loaded. Returning to menu.")
        gstate.reset_game()
        st.rerun()
        return

    # Auto-resolve timeout so the player doesn't have to click through a dead timer.
    if not state["answered"] and gstate.is_time_up():
        gstate.submit_answer(-1)

    render_status_bar(state)
    render_quest_trail(current_level=state["level_number"])

    level_cfg = get_level(state["level_number"])
    st.markdown(
        f'<div style="text-align:center;color:var(--kq-text-dim);font-size:0.85rem;margin-bottom:0.3rem;">'
        f'LEVEL {state["level_number"]} · {level_cfg["name"].upper()}</div>',
        unsafe_allow_html=True,
    )
    render_level_dots(len(state["level_questions"]), state["q_index"])

    q = state["current_question"]

    st.markdown('<div class="kq-card">', unsafe_allow_html=True)
    render_tags(q["category"], q["difficulty"])

    ratio = gstate.time_left_ratio()
    render_timer_bar(ratio)

    st.markdown(f'<p style="font-size:1.12rem;font-weight:600;margin-top:0.5rem;">{q["question"]}</p>',
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not state["answered"]:
        _render_unanswered(state, q)
    else:
        _render_feedback(state, q)


def _render_unanswered(state, q):
    can_hint = state["hints_remaining"] > 0 and not state["hint_used_this_q"]
    hint_col, _ = st.columns([1, 2])
    with hint_col:
        if st.button(f"💡 Hint ({state['hints_remaining']})", key="use_hint", disabled=not can_hint):
            gstate.use_hint()
            st.rerun()

    for i, option in enumerate(q["options"]):
        if i in state["hidden_options"]:
            continue
        if st.button(option, key=f"opt_{state['q_index']}_{i}"):
            gstate.submit_answer(i)
            st.rerun()


def _render_feedback(state, q):
    correct_idx = q["correct"]
    for i, option in enumerate(q["options"]):
        if i in state["hidden_options"] and i != state["selected_option"]:
            continue
        if i == correct_idx:
            st.markdown(f"✅ **{option}**")
        elif i == state["selected_option"]:
            st.markdown(f"❌ ~~{option}~~")
        else:
            st.markdown(f"&nbsp;&nbsp;&nbsp;{option}", unsafe_allow_html=True)

    if state.get("last_timed_out"):
        st.markdown(
            f'<div class="kq-feedback wrong">⏰ Time\'s up!'
            f'<div class="kq-explain">{q["explanation"]}</div></div>',
            unsafe_allow_html=True,
        )
    elif state["last_correct"]:
        st.markdown(
            f'<div class="kq-feedback correct">✓ Correct! +{state["last_points"]} points'
            f'<div class="kq-explain">{q["explanation"]}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="kq-feedback wrong">✗ Not quite.'
            f'<div class="kq-explain">{q["explanation"]}</div></div>',
            unsafe_allow_html=True,
        )

    if state["game_over"]:
        label = "See Results"
    elif state["q_index"] + 1 >= len(state["level_questions"]):
        label = "Finish Level"
    else:
        label = "Next Question →"

    if st.button(label, type="primary", key="advance_btn"):
        gstate.advance()
        st.rerun()


# ---------------------------------------------------------------- LEVEL COMPLETE
def render_level_complete():
    state = gstate.gs()
    level_cfg = get_level(state["level_number"])
    score_gained = state["score"] - state["level_score_start"]
    xp_gained = state["xp"] - state["level_xp_start"]

    st.markdown(
        f"""
        <div class="kq-hero">
            <div class="kq-compass">🏆</div>
            <div class="kq-hero-title kq-display">Level {state['level_number']} Complete!</div>
            <p class="kq-hero-sub">{level_cfg['name']} cleared — {state['level_correct_count']}/{len(state['level_questions'])} correct</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_quest_trail(current_level=state["level_number"] + 1)

    st.markdown(
        f"""
        <div class="kq-card" style="text-align:center;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;color:var(--kq-accent-soft);">
                +{score_gained} points · +{xp_gained} XP
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_xp_bar(get_rank(state["xp"]))

    next_level_num = state["level_number"] + 1
    if next_level_num <= TOTAL_LEVELS:
        next_cfg = get_level(next_level_num)
        if st.button(f"Continue to Level {next_level_num} — {next_cfg['name']} →", type="primary", key="next_level"):
            gstate.continue_to_next_level()
            st.rerun()

    if st.button("Quit to Menu", key="quit_menu_from_level_complete"):
        gstate.reset_game()
        st.rerun()


# ---------------------------------------------------------------- RESULTS
def render_results():
    state = gstate.gs()
    won = not state["game_over"]

    if won:
        title, sub, emoji = "Quest Complete!", "You cleared all 5 levels.", "👑"
    else:
        title, sub, emoji = "Quest Ended", state["game_over_reason"] or "Better luck next time.", "🗺️"

    st.markdown(
        f"""
        <div class="kq-hero">
            <div class="kq-compass">{emoji}</div>
            <div class="kq-hero-title kq-display">{title}</div>
            <p class="kq-hero-sub">{sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="kq-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Final Score", state["score"])
        st.metric("Accuracy", f"{gstate.accuracy_percent()}%")
    with c2:
        st.metric("Best Streak", state["max_streak"])
        st.metric("Questions Answered", state["total_answered"])
    st.markdown("</div>", unsafe_allow_html=True)

    render_xp_bar(get_rank(state["xp"]))

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔁 Play Again", type="primary", key="results_replay"):
        gstate.reset_game()
        gstate.go_to_setup()
        st.rerun()

    if st.button("🏠 Main Menu", key="results_menu"):
        gstate.reset_game()
        st.rerun()
