"""
Knowledge Challenge mode: multiple-choice questions across categories,
difficulty tied to the current level.
"""

from game.challenge_base import ChallengeMode
from game.levels import get_level
from game.question_bank import select_questions


class KnowledgeChallengeMode(ChallengeMode):
    name = "Knowledge Challenge"
    description = "Test what you know across science, geography, history, space, nature and more."

    def generate_level(self, level_number: int, category: str, used_ids: set) -> list:
        level_cfg = get_level(level_number)
        questions = select_questions(
            category=category,
            difficulty=level_cfg["difficulty"],
            count=level_cfg["questions_per_level"],
            used_ids=used_ids,
        )
        return questions
