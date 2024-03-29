import enum
import random
from typing import Callable, List, Mapping, Optional

from backend import ai_names
from game import decision_functions as ai
from game import state

AIFunc = Callable[[state.GameState], int]


@enum.unique
class AILevel(enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

    @staticmethod
    def from_str(label: Optional[str]) -> Optional["AILevel"]:
        if not label:
            return None
        label = label.upper()
        if label in ("EASY", "MEDIUM", "HARD"):
            return AILevel[label]
        return None


_AIs: Optional[Mapping[AILevel, AIFunc]] = None


def get() -> Mapping[AILevel, AIFunc]:
    global _AIs
    if _AIs is None:
        _AIs = {
            AILevel.EASY: ai.first_move,
            AILevel.MEDIUM: ai.random,
            AILevel.HARD: ai.oracle_ai,
        }
    return _AIs


def generate_name(level: AILevel, curr_players: List[str]) -> str:
    selectedName = " ".join(
        part.capitalize() for part in random.choice(ai_names.ALL).split(" ")
    )
    name = f"{level.name.capitalize()} {selectedName}"
    count = 0
    while (count == 0 and name in curr_players) or (f"{name}-{count}" in curr_players):
        count += 1
    return name if count == 0 else f"{name}-{count}"
