from game.challenge_base import ChallengeMode
from game.levels import get_level
from game.question_bank import select_questions


class LogicLabMode(ChallengeMode):
    name = "Logic Lab"
    description = "Solve number sequences, patterns, odd-one-out, deduction, and math puzzles."

    def generate_level(self, level_number: int, category: str, used_ids: set, language: str = "en") -> list:
        level_cfg = get_level(level_number)
        questions = select_questions(
            mode="logic",
            category=category,
            difficulty=level_cfg["difficulty"],
            count=level_cfg["questions_per_level"],
            used_ids=used_ids,
            language=language,
        )
        return questions
