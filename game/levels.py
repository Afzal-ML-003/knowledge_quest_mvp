"""
Level configuration for Knowledge Quest.

Levels progressively increase difficulty and introduce the timer gradually,
per the project's difficulty-progression guidelines (no random difficulty
spikes, mechanics introduced one at a time).
"""

LEVELS = [
    {
        "number": 1,
        "name": "Beginner",
        "difficulty": "easy",
        "questions_per_level": 5,
        "timer_seconds": None,
    },
    {
        "number": 2,
        "name": "Explorer",
        "difficulty": "easy",
        "questions_per_level": 5,
        "timer_seconds": 30,
    },
    {
        "number": 3,
        "name": "Challenger",
        "difficulty": "medium",
        "questions_per_level": 5,
        "timer_seconds": 25,
    },
    {
        "number": 4,
        "name": "Expert",
        "difficulty": "hard",
        "questions_per_level": 5,
        "timer_seconds": 20,
    },
    {
        "number": 5,
        "name": "Master",
        "difficulty": "expert",
        "questions_per_level": 5,
        "timer_seconds": 15,
    },
]

KNOWLEDGE_CATEGORIES = [
    "Mixed",
    "Science",
    "Geography",
    "History",
    "Space",
    "Nature",
    "General Knowledge",
]

# Backward-compatible alias (existing UI code imports CATEGORIES for Knowledge Challenge)
CATEGORIES = KNOWLEDGE_CATEGORIES

LOGIC_CATEGORIES = [
    "Mixed",
    "Number Sequence",
    "Pattern Recognition",
    "Odd One Out",
    "Logical Deduction",
    "Math Reasoning",
]

MODE_CATEGORIES = {
    "knowledge": KNOWLEDGE_CATEGORIES,
    "logic": LOGIC_CATEGORIES,
}

MODE_LABELS = {
    "knowledge": "Knowledge Challenge",
    "logic": "Logic Lab",
}

LANGUAGES = {
    "en": "English",
    "ur": "Roman Urdu",
}
DEFAULT_LANGUAGE = "en"

TOTAL_LEVELS = len(LEVELS)


def get_level(number: int) -> dict:
    """Return the level config for a given 1-indexed level number."""
    for lvl in LEVELS:
        if lvl["number"] == number:
            return lvl
    raise ValueError(f"No level config for level {number}")
