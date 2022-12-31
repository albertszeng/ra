import enum
import random
from typing import Callable, List, Mapping, Optional

from backend import ai_names
from game import state
from game.decision_functions import ai_base

AIFunc = Callable[[state.GameState], int]


class AILevel(enum.Enum):
    EASY = 1


_AIs: Optional[Mapping[AILevel, AIFunc]] = None


def get() -> Mapping[AILevel, AIFunc]:
    global _AIs
    if _AIs is None:
        _AIs = {AILevel.EASY: ai_base.make_first_move_ai}
    return _AIs


def generate_name(curr_players: List[str]) -> str:
    name = random.choice(ai_names.ALL)
    count = 1
    while (count == 1 and name in curr_players) or (f"{name}-{count}" in curr_players):
        count += 1
    return name if count == 1 else f"{name}-{count}"
