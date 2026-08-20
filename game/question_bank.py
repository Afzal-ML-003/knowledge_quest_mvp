"""
Question bank: loads question data from data/questions.json and selects
questions for a level while avoiding repeats within a session.

Kept separate from game logic so the content file can grow to hundreds of
questions without touching this module.
"""

import json
import random
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "questions.json"

_CACHE = None


def _load_all():
    global _CACHE
    if _CACHE is None:
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                payload = json.load(f)
            _CACHE = payload.get("questions", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(
                f"Could not load question bank from {DATA_PATH}: {e}"
            ) from e
    return _CACHE


def all_categories():
    return sorted({q["category"] for q in _load_all()})


def select_questions(category: str, difficulty: str, count: int, used_ids: set) -> list:
    """
    Select up to `count` questions matching difficulty (and category, unless
    category == "Mixed"), preferring ones not already in used_ids.

    Fallback order if the ideal pool is too small (keeps the game from
    crashing or stalling on a sparse dataset):
      1. Unused questions matching category + difficulty
      2. Any questions (including previously used) matching category + difficulty
      3. Unused questions matching difficulty only (any category)
      4. Any questions matching difficulty only
    """
    all_q = _load_all()

    def matches(q, use_category, use_difficulty_only=False):
        if q["difficulty"] != difficulty:
            return False
        if use_category and category != "Mixed" and q["category"] != category:
            return False
        return True

    pool_unused_cat = [q for q in all_q if matches(q, True) and q["id"] not in used_ids]
    if len(pool_unused_cat) >= count:
        return random.sample(pool_unused_cat, count)

    pool_any_cat = [q for q in all_q if matches(q, True)]
    if len(pool_any_cat) >= count:
        # prioritize unused first, fill remainder with used ones
        rest = [q for q in pool_any_cat if q["id"] not in used_ids]
        used = [q for q in pool_any_cat if q["id"] in used_ids]
        random.shuffle(rest)
        random.shuffle(used)
        combined = rest + used
        return combined[:count]

    pool_unused_diff = [q for q in all_q if matches(q, False) and q["id"] not in used_ids]
    if len(pool_unused_diff) >= count:
        return random.sample(pool_unused_diff, count)

    pool_any_diff = [q for q in all_q if matches(q, False)]
    random.shuffle(pool_any_diff)
    return pool_any_diff[:count]
