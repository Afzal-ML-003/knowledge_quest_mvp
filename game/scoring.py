"""
Scoring logic for Knowledge Quest.

Kept as pure functions with no Streamlit dependency so it can be
unit-tested independently of the UI layer.
"""

BASE_POINTS = {
    "easy": 100,
    "medium": 200,
    "hard": 400,
    "expert": 800,
}

HINT_PENALTY_MULTIPLIER = 0.5   # score halved if a hint was used
SPEED_BONUS_MULTIPLIER = 0.2    # +20% if answered in first half of the timer
SPEED_BONUS_THRESHOLD = 0.5     # time_left_ratio must exceed this to earn the bonus
STREAK_BONUS_PER_STEP = 10
STREAK_BONUS_CAP = 100
STREAK_BONUS_MIN_STREAK = 3


def compute_score(difficulty: str, hint_used: bool, time_left_ratio, streak_count: int) -> int:
    """
    Compute points earned for a single correct answer.

    difficulty: "easy" | "medium" | "hard" | "expert"
    hint_used: whether the player used a hint on this question
    time_left_ratio: float in [0, 1] representing fraction of time remaining
                      when answered, or None if the question had no timer
    streak_count: the player's current correct-answer streak (including this answer)
    """
    if difficulty not in BASE_POINTS:
        raise ValueError(f"Unknown difficulty: {difficulty}")

    base = BASE_POINTS[difficulty]

    if hint_used:
        base = int(base * HINT_PENALTY_MULTIPLIER)

    speed_bonus = 0
    if time_left_ratio is not None and time_left_ratio > SPEED_BONUS_THRESHOLD:
        speed_bonus = int(base * SPEED_BONUS_MULTIPLIER)

    streak_bonus = 0
    if streak_count >= STREAK_BONUS_MIN_STREAK:
        streak_bonus = min(streak_count * STREAK_BONUS_PER_STEP, STREAK_BONUS_CAP)

    return base + speed_bonus + streak_bonus


def xp_from_score(score: int) -> int:
    """Convert points earned into XP. Kept as a simple, transparent ratio."""
    return max(1, score // 5)
