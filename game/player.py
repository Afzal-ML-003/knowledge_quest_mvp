"""
Player progression logic: XP -> rank mapping.

This is the *foundation* for a full rank system (achievements, rank-up
animations, etc. are intentionally left for a later milestone per the
MVP scope).
"""

RANKS = [
    ("Novice", 0),
    ("Learner", 300),
    ("Explorer", 800),
    ("Thinker", 1600),
    ("Strategist", 2800),
    ("Expert", 4500),
    ("Master", 7000),
]


def get_rank(xp: int) -> dict:
    """
    Given total XP, return the current rank name, the XP threshold for the
    next rank (or None if at max rank), and progress (0.0-1.0) toward it.
    """
    current_name, current_threshold = RANKS[0]
    next_threshold = None
    next_name = None

    for i, (name, threshold) in enumerate(RANKS):
        if xp >= threshold:
            current_name, current_threshold = name, threshold
            if i + 1 < len(RANKS):
                next_name, next_threshold = RANKS[i + 1]
            else:
                next_name, next_threshold = None, None
        else:
            break

    if next_threshold is None:
        progress = 1.0
    else:
        span = next_threshold - current_threshold
        progress = (xp - current_threshold) / span if span > 0 else 1.0
        progress = max(0.0, min(1.0, progress))

    return {
        "rank": current_name,
        "next_rank": next_name,
        "xp": xp,
        "current_threshold": current_threshold,
        "next_threshold": next_threshold,
        "progress": progress,
    }


STARTING_LIVES = 3
STARTING_HINTS = 3
