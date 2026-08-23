"""
Shared interface every game mode implements.

The rest of the engine (state machine, scoring, lives, streak, results
screen) only ever talks to a mode through this interface. This is what
lets Logic Lab, Memory Vault, Mystery Puzzle, and Daily Challenge be added
later without touching app.py or the core state machine.
"""

from abc import ABC, abstractmethod


class Challenge(ABC):
    """One question/puzzle instance within a mode."""

    @abstractmethod
    def check_answer(self, submitted_answer) -> bool:
        """Return True if submitted_answer is correct."""
        raise NotImplementedError

    @abstractmethod
    def get_explanation(self) -> str:
        """Short educational explanation shown after answering."""
        raise NotImplementedError

    @abstractmethod
    def get_hint(self) -> str:
        """Hint text (or hint effect) shown when the player spends a hint."""
        raise NotImplementedError


class ChallengeMode(ABC):
    """
    A full game mode (Knowledge Challenge, Logic Lab, etc).

    generate_level() must return a list of Challenge-compatible dicts for
    the requested level/category so the engine can drive the round without
    knowing mode-specific details.
    """

    name: str = "Unnamed Mode"
    description: str = ""

    @abstractmethod
    def generate_level(self, level_number: int, category: str, used_ids: set, language: str = "en") -> list:
        raise NotImplementedError
