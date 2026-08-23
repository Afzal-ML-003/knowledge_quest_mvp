"""
Question bank: loads question data from data/questions_en.json (English) or
data/questions.json (Roman Urdu), and selects questions for a level while
avoiding repeats within a session.

Both language files share identical question `id`s in the same order, so
anti-repetition (used_ids) works correctly regardless of which language is
active - switching language mid-session still avoids repeats correctly,
since a given id represents "the same question" in either language.

Kept separate from game logic so the content files can grow to hundreds of
questions without touching this module.
"""

import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

LANGUAGE_FILES = {
    "en": DATA_DIR / "questions_en.json",
    "ur": DATA_DIR / "questions.json",
}
DEFAULT_LANGUAGE = "en"

_CACHE = {}  # language -> list of question dicts


def _load_all(language: str = DEFAULT_LANGUAGE):
    if language not in LANGUAGE_FILES:
        raise ValueError(f"Unknown language '{language}'. Expected one of {list(LANGUAGE_FILES)}.")

    if language not in _CACHE:
        path = LANGUAGE_FILES[language]
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            _CACHE[language] = payload.get("questions", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(
                f"Could not load question bank from {path}: {e}"
            ) from e
    return _CACHE[language]


def all_categories(mode: str = "knowledge", language: str = DEFAULT_LANGUAGE):
    return sorted({q["category"] for q in _load_all(language) if q.get("mode", "knowledge") == mode})


def select_questions(mode: str, category: str, difficulty: str, count: int,
                      used_ids: set, language: str = DEFAULT_LANGUAGE) -> list:
    """
    Select up to `count` questions for the given mode and language, matching
    difficulty (and category, unless category == "Mixed"), preferring ones
    not already in used_ids.

    `mode` is a hard constraint: a Logic Lab round will never pull a
    Knowledge Challenge question, even as a last-resort fallback. Category
    and difficulty degrade gracefully if the ideal pool is too small, so a
    sparse dataset never crashes or stalls the game:
      1. Unused, same mode + category + difficulty
      2. Any (incl. previously used), same mode + category + difficulty
      3. Unused, same mode + difficulty (any category within that mode)
      4. Any, same mode + difficulty
      5. Unused, same mode only (any difficulty) - final safety net
      6. Any, same mode only
    """
    all_q = _load_all(language)
    mode_pool = [q for q in all_q if q.get("mode", "knowledge") == mode]

    def matches(q, use_category, use_difficulty=True):
        if use_difficulty and q["difficulty"] != difficulty:
            return False
        if use_category and category != "Mixed" and q["category"] != category:
            return False
        return True

    def pick(pool_fn, use_category, use_difficulty=True):
        unused = [q for q in mode_pool if pool_fn(q, use_category, use_difficulty) and q["id"] not in used_ids]
        if len(unused) >= count:
            return random.sample(unused, count)
        return None

    result = pick(matches, use_category=True)
    if result is not None:
        return result

    pool_any_cat = [q for q in mode_pool if matches(q, True)]
    if len(pool_any_cat) >= count:
        rest = [q for q in pool_any_cat if q["id"] not in used_ids]
        used = [q for q in pool_any_cat if q["id"] in used_ids]
        random.shuffle(rest)
        random.shuffle(used)
        return (rest + used)[:count]

    result = pick(matches, use_category=False)
    if result is not None:
        return result

    pool_any_diff = [q for q in mode_pool if matches(q, False)]
    if len(pool_any_diff) >= count:
        rest = [q for q in pool_any_diff if q["id"] not in used_ids]
        used = [q for q in pool_any_diff if q["id"] in used_ids]
        random.shuffle(rest)
        random.shuffle(used)
        return (rest + used)[:count]

    result = pick(matches, use_category=False, use_difficulty=False)
    if result is not None:
        return result

    random.shuffle(mode_pool)
    return mode_pool[:count]
