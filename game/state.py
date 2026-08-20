"""
Core game state machine, stored in st.session_state under the "gs" key.

Design notes:
- This module is the single source of truth for game state. UI code in
  ui/screens.py only ever reads gs and calls these functions; it never
  mutates state directly. That boundary is what will let us add Logic Lab,
  Memory Vault etc. later without rewriting this file.
- Timer design: Streamlit reruns the whole script on each interaction, so
  there is no live server-side countdown. The timer is a CSS-animated
  visual countdown (see ui/components.py) for player feedback and pressure,
  and is enforced at answer-submission time by comparing elapsed wall-clock
  time against the level's timer_seconds. This is an intentional, documented
  tradeoff rather than a fake feature.
"""

import time
import streamlit as st

from game.levels import get_level, TOTAL_LEVELS
from game.player import STARTING_LIVES, STARTING_HINTS
from game.scoring import compute_score, xp_from_score
from game.modes.knowledge import KnowledgeChallengeMode

MODES = {
    "knowledge": KnowledgeChallengeMode(),
}


def _fresh_state() -> dict:
    return {
        "screen": "menu",           # menu | setup | playing | level_complete | results
        "mode": "knowledge",
        "category": "Mixed",
        "level_number": 1,

        "level_questions": [],
        "q_index": 0,
        "current_question": None,
        "answered": False,
        "selected_option": None,
        "last_correct": None,
        "hidden_options": [],
        "hint_used_this_q": False,

        "score": 0,
        "xp": 0,
        "lives": STARTING_LIVES,
        "hints_remaining": STARTING_HINTS,
        "streak": 0,
        "max_streak": 0,
        "correct_count": 0,
        "total_answered": 0,
        "used_question_ids": set(),

        "question_start_time": None,

        "level_correct_count": 0,
        "level_score_start": 0,
        "level_xp_start": 0,

        "game_over": False,
        "game_over_reason": "",
    }


def init_state():
    if "gs" not in st.session_state:
        st.session_state.gs = _fresh_state()


def gs() -> dict:
    return st.session_state.gs


def reset_game():
    st.session_state.gs = _fresh_state()


def go_to_setup():
    gs()["screen"] = "setup"


def go_to_menu():
    gs()["screen"] = "menu"


def start_game(category: str):
    state = gs()
    state["category"] = category
    state["level_number"] = 1
    start_level(1)


def start_level(level_number: int):
    state = gs()
    level_cfg = get_level(level_number)
    mode = MODES[state["mode"]]

    questions = mode.generate_level(level_number, state["category"], state["used_question_ids"])
    if not questions:
        # Safety net: should not happen given question_bank fallbacks, but
        # never let the game hang with an empty level.
        state["game_over"] = True
        state["game_over_reason"] = "No questions available for this selection."
        state["screen"] = "results"
        return

    state["level_number"] = level_number
    state["level_questions"] = questions
    state["q_index"] = 0
    state["level_correct_count"] = 0
    state["level_score_start"] = state["score"]
    state["level_xp_start"] = state["xp"]
    state["screen"] = "playing"
    _load_question(state["q_index"])


def _load_question(index: int):
    state = gs()
    state["current_question"] = state["level_questions"][index]
    state["answered"] = False
    state["selected_option"] = None
    state["last_correct"] = None
    state["hidden_options"] = []
    state["hint_used_this_q"] = False
    state["question_start_time"] = time.time()


def timer_seconds_for_current_level():
    return get_level(gs()["level_number"])["timer_seconds"]


def time_left_ratio() -> float:
    """Return fraction (0-1) of time remaining for the current question, or None if untimed."""
    limit = timer_seconds_for_current_level()
    if limit is None:
        return None
    state = gs()
    elapsed = time.time() - state["question_start_time"]
    remaining = max(0.0, limit - elapsed)
    return remaining / limit


def is_time_up() -> bool:
    ratio = time_left_ratio()
    return ratio is not None and ratio <= 0


def use_hint():
    state = gs()
    if state["hints_remaining"] <= 0 or state["answered"] or state["hint_used_this_q"]:
        return
    q = state["current_question"]
    correct_idx = q["correct"]
    remaining_wrong = [i for i in range(len(q["options"]))
                        if i != correct_idx and i not in state["hidden_options"]]
    if remaining_wrong:
        state["hidden_options"].append(remaining_wrong[0])
    state["hints_remaining"] -= 1
    state["hint_used_this_q"] = True


def submit_answer(selected_index: int):
    state = gs()
    if state["answered"]:
        return

    q = state["current_question"]
    timed_out = is_time_up()
    ratio = time_left_ratio()
    correct = (not timed_out) and (selected_index == q["correct"])

    state["answered"] = True
    state["selected_option"] = selected_index
    state["last_correct"] = correct
    state["last_timed_out"] = timed_out
    state["used_question_ids"].add(q["id"])
    state["total_answered"] += 1

    if correct:
        state["streak"] += 1
        state["max_streak"] = max(state["max_streak"], state["streak"])
        points = compute_score(
            difficulty=q["difficulty"],
            hint_used=state["hint_used_this_q"],
            time_left_ratio=ratio,
            streak_count=state["streak"],
        )
        state["score"] += points
        state["xp"] += xp_from_score(points)
        state["correct_count"] += 1
        state["level_correct_count"] += 1
        state["last_points"] = points
    else:
        state["streak"] = 0
        state["last_points"] = 0
        state["lives"] -= 1
        if state["lives"] <= 0:
            state["game_over"] = True
            state["game_over_reason"] = "Out of lives"


def advance():
    """Move to next question, next level, level-complete screen, or results."""
    state = gs()

    if state["game_over"]:
        state["screen"] = "results"
        return

    next_index = state["q_index"] + 1
    if next_index < len(state["level_questions"]):
        state["q_index"] = next_index
        _load_question(next_index)
        return

    # Level finished
    if state["level_number"] >= TOTAL_LEVELS:
        state["screen"] = "results"
    else:
        state["screen"] = "level_complete"


def continue_to_next_level():
    state = gs()
    start_level(state["level_number"] + 1)


def accuracy_percent() -> int:
    state = gs()
    if state["total_answered"] == 0:
        return 0
    return round(100 * state["correct_count"] / state["total_answered"])
