"""
Unit tests for the core engine logic (scoring, ranks, levels, question bank).

These test modules deliberately have no Streamlit dependency, so they can
run in any plain Python environment:

    cd knowledge_quest
    python -m pytest tests/ -v

or, without pytest installed:

    cd knowledge_quest
    python tests/test_engine.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.scoring import compute_score, xp_from_score, BASE_POINTS
from game.player import get_rank, RANKS
from game.levels import (
    LEVELS, get_level, TOTAL_LEVELS, CATEGORIES, KNOWLEDGE_CATEGORIES,
    LOGIC_CATEGORIES, MODE_CATEGORIES, MODE_LABELS, LANGUAGES,
)
from game.question_bank import select_questions, all_categories
from game.modes.knowledge import KnowledgeChallengeMode
from game.modes.logic import LogicLabMode


# ---------------------------------------------------------------- scoring
def test_base_points_by_difficulty():
    for diff, expected in [("easy", 100), ("medium", 200), ("hard", 400), ("expert", 800)]:
        score = compute_score(diff, hint_used=False, time_left_ratio=None, streak_count=0)
        assert score == expected, f"{diff}: expected {expected}, got {score}"


def test_hint_halves_score():
    full = compute_score("easy", hint_used=False, time_left_ratio=None, streak_count=0)
    hinted = compute_score("easy", hint_used=True, time_left_ratio=None, streak_count=0)
    assert hinted == full // 2


def test_speed_bonus_applies_above_threshold():
    slow = compute_score("medium", hint_used=False, time_left_ratio=0.4, streak_count=0)
    fast = compute_score("medium", hint_used=False, time_left_ratio=0.9, streak_count=0)
    assert fast > slow
    assert fast == 200 + int(200 * 0.2)


def test_speed_bonus_none_when_untimed():
    score = compute_score("medium", hint_used=False, time_left_ratio=None, streak_count=0)
    assert score == 200


def test_streak_bonus_applies_after_threshold():
    below = compute_score("easy", hint_used=False, time_left_ratio=None, streak_count=2)
    at_threshold = compute_score("easy", hint_used=False, time_left_ratio=None, streak_count=3)
    assert below == 100
    assert at_threshold == 130  # 100 base + 3*10 streak bonus


def test_streak_bonus_is_capped():
    huge_streak = compute_score("easy", hint_used=False, time_left_ratio=None, streak_count=50)
    assert huge_streak == 100 + 100  # capped at STREAK_BONUS_CAP = 100


def test_invalid_difficulty_raises():
    try:
        compute_score("legendary", hint_used=False, time_left_ratio=None, streak_count=0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_xp_from_score_never_zero():
    assert xp_from_score(0) >= 1
    assert xp_from_score(100) == 20


# ---------------------------------------------------------------- ranks
def test_rank_starts_at_novice():
    info = get_rank(0)
    assert info["rank"] == "Novice"
    assert info["next_rank"] == "Learner"


def test_rank_progresses_with_xp():
    info = get_rank(500)
    assert info["rank"] == "Learner"


def test_rank_caps_at_master():
    info = get_rank(999999)
    assert info["rank"] == "Master"
    assert info["next_rank"] is None
    assert info["progress"] == 1.0


def test_rank_progress_is_bounded():
    for xp in [0, 150, 300, 1000, 5000, 100000]:
        info = get_rank(xp)
        assert 0.0 <= info["progress"] <= 1.0


# ---------------------------------------------------------------- levels
def test_five_levels_configured():
    assert TOTAL_LEVELS == 5
    assert len(LEVELS) == 5


def test_difficulty_increases_with_level():
    order = ["easy", "medium", "hard", "expert"]
    prev_rank = -1
    for lvl in LEVELS:
        rank = order.index(lvl["difficulty"])
        assert rank >= prev_rank, "difficulty should not decrease as levels progress"
        prev_rank = rank


def test_timer_introduced_gradually():
    assert get_level(1)["timer_seconds"] is None
    assert get_level(2)["timer_seconds"] is not None
    assert get_level(5)["timer_seconds"] < get_level(2)["timer_seconds"]


def test_get_level_invalid_raises():
    try:
        get_level(99)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_categories_include_mixed():
    assert "Mixed" in CATEGORIES


# ---------------------------------------------------------------- question bank
def test_question_bank_has_all_categories():
    cats = all_categories(mode="knowledge")
    for c in CATEGORIES:
        if c != "Mixed":
            assert c in cats, f"missing category {c} in data"


def test_select_questions_respects_difficulty():
    qs = select_questions(mode="knowledge", category="Mixed", difficulty="easy", count=5, used_ids=set())
    assert len(qs) == 5
    assert all(q["difficulty"] == "easy" for q in qs)


def test_select_questions_respects_category():
    qs = select_questions(mode="knowledge", category="Science", difficulty="medium", count=3, used_ids=set())
    assert len(qs) == 3
    assert all(q["category"] == "Science" for q in qs)


def test_select_questions_avoids_repeats_when_pool_allows():
    used = set()
    for _ in range(3):
        qs = select_questions(mode="knowledge", category="Mixed", difficulty="hard", count=5, used_ids=used)
        ids = {q["id"] for q in qs}
        assert ids.isdisjoint(used), "should not repeat questions while pool has unused ones"
        used |= ids


def test_select_questions_never_mixes_modes():
    # Even with category="Mixed", a Logic Lab round must never draw a Knowledge question.
    for _ in range(5):
        qs = select_questions(mode="logic", category="Mixed", difficulty="easy", count=5, used_ids=set())
        assert all(q["mode"] == "logic" for q in qs), "logic mode leaked a knowledge question"

    for _ in range(5):
        qs = select_questions(mode="knowledge", category="Mixed", difficulty="easy", count=5, used_ids=set())
        assert all(q["mode"] == "knowledge" for q in qs), "knowledge mode leaked a logic question"


def test_select_questions_logic_lab_category_filter():
    qs = select_questions(mode="logic", category="Number Sequence", difficulty="medium", count=2, used_ids=set())
    assert len(qs) == 2
    assert all(q["category"] == "Number Sequence" and q["mode"] == "logic" for q in qs)


def test_select_questions_never_crashes_on_depleted_pool():
    # Exhaust a whole category+difficulty pool, then request more anyway.
    used = {q["id"] for q in select_questions(mode="knowledge", category="Science", difficulty="easy", count=3, used_ids=set())}
    qs = select_questions(mode="knowledge", category="Science", difficulty="easy", count=3, used_ids=used)
    assert len(qs) == 3  # falls back to reusing questions rather than crashing


def test_question_options_have_valid_correct_index():
    from game.question_bank import _load_all
    for lang in ("en", "ur"):
        for q in _load_all(lang):
            assert 0 <= q["correct"] < len(q["options"])
            assert len(q["options"]) == 4


# ---------------------------------------------------------------- modes / registry
def test_mode_category_registry_matches_labels():
    assert set(MODE_CATEGORIES.keys()) == set(MODE_LABELS.keys()) == {"knowledge", "logic"}
    assert "Mixed" in KNOWLEDGE_CATEGORIES
    assert "Mixed" in LOGIC_CATEGORIES
    assert KNOWLEDGE_CATEGORIES != LOGIC_CATEGORIES


def test_logic_lab_generates_full_level():
    mode = LogicLabMode()
    level_cfg = get_level(3)
    qs = mode.generate_level(3, "Mixed", used_ids=set(), language="en")
    assert len(qs) == level_cfg["questions_per_level"]
    assert all(q["mode"] == "logic" and q["difficulty"] == level_cfg["difficulty"] for q in qs)


def test_logic_lab_never_returns_knowledge_questions():
    mode = LogicLabMode()
    for level_num in range(1, TOTAL_LEVELS + 1):
        qs = mode.generate_level(level_num, "Mixed", used_ids=set(), language="en")
        assert all(q["mode"] == "logic" for q in qs)


def test_knowledge_mode_never_returns_logic_questions():
    mode = KnowledgeChallengeMode()
    for level_num in range(1, TOTAL_LEVELS + 1):
        qs = mode.generate_level(level_num, "Mixed", used_ids=set(), language="en")
        assert all(q["mode"] == "knowledge" for q in qs)


# ---------------------------------------------------------------- language
def test_both_language_files_load():
    en = select_questions(mode="knowledge", category="Mixed", difficulty="easy", count=3, used_ids=set(), language="en")
    ur = select_questions(mode="knowledge", category="Mixed", difficulty="easy", count=3, used_ids=set(), language="ur")
    assert len(en) == 3 and len(ur) == 3


def test_language_ids_align_across_files():
    from game.question_bank import _load_all
    en_ids = {q["id"] for q in _load_all("en")}
    ur_ids = {q["id"] for q in _load_all("ur")}
    assert en_ids == ur_ids, "English and Roman Urdu question banks must have identical id sets"


def test_language_switch_preserves_anti_repeat():
    # Answering in English then switching to Urdu should still avoid repeats,
    # since ids match across both language files.
    used = {q["id"] for q in select_questions(mode="knowledge", category="Science", difficulty="easy", count=3, used_ids=set(), language="en")}
    ur_followup = select_questions(mode="knowledge", category="Science", difficulty="easy", count=3, used_ids=used, language="ur")
    ur_ids = {q["id"] for q in ur_followup}
    # Science+easy pool has exactly 3 questions, so with 3 used it must fall back
    # to reusing rather than crash - but should still return valid Science/easy items.
    assert len(ur_ids) == 3
    assert all(q["difficulty"] == "easy" for q in ur_followup)


def test_invalid_language_raises():
    try:
        select_questions(mode="knowledge", category="Mixed", difficulty="easy", count=1, used_ids=set(), language="fr")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_language_registry_has_english_and_urdu():
    assert LANGUAGES.get("en") == "English"
    assert LANGUAGES.get("ur") == "Roman Urdu"


ALL_TESTS = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]

if __name__ == "__main__":
    passed, failed = 0, 0
    for t in ALL_TESTS:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
