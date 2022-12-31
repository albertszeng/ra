import enum
import random
from typing import Callable, List, Mapping, Optional

from backend import ai_names
from game import decision_functions as ai
from game import state

AIFunc = Callable[[state.GameState], int]


class AILevel(enum.Enum):
    EASY = 1
    RANDOM = 2
    ORACLE = 3


_AIs: Optional[Mapping[AILevel, AIFunc]] = None


def get() -> Mapping[AILevel, AIFunc]:
    global _AIs
    if _AIs is None:
        _AIs = {
            AILevel.EASY: ai.first_move,
            AILevel.RANDOM: ai.random,
            AILevel.ORACLE: ai.oracle,
        }
    return _AIs


def generate_name(curr_players: List[str]) -> str:
    name = random.choice(ai_names.ALL)
    count = 1
    while (count == 1 and name in curr_players) or (f"{name}-{count}" in curr_players):
        count += 1
    return name if count == 1 else f"{name}-{count}"
