import copy
from typing import Dict, Mapping, Tuple

from game import info as gi
from game import ra
from game import state as gs
from game.decision_functions import evaluate_game_state as e


def search(game_state: gs.GameState) -> int:
    """
    Given the current game state, return an action to take.
    """
    return 0


def search_internal(
    game_state: gs.GameState, auction_has_occurred: bool
) -> Tuple[int, Dict[str, float]]:
    """
    Find action to take based on expectimax. Returns the best action and the resulting valuation of
    each player's state.

    Continues until at least 1 auction has occurred and the auction tiles are empty.
    """
    legal_actions = ra.get_possible_actions(game_state)
    assert (
        legal_actions is not None and len(legal_actions) > 0
    ), "Cannot perform search_internal because no legal actions"

    # Simulate each legal action and find their resulting valuations
    action_results: Dict[int, Dict[str, float]] = {}
    for action in legal_actions:
        game_state_copy = copy.deepcopy(game_state)
        if action == gi.DRAW:
            # TODO(albertz): do expectimax
            return (0, {})
        else:
            ra.execute_action_internal(game_state_copy, action, legal_actions)
            action_results[action] = value_state(
                game_state_copy, auction_has_occurred or action == gi.AUCTION
            )

    assert len(action_results.keys()) == len(
        legal_actions
    ), f"There are {len(action_results.keys())} action results but {len(legal_actions)} legal actions"

    # Pick the action that leads to the best resulting valuation for the current player
    current_player_name = game_state.get_current_player_name()
    best_action = None
    best_resulting_valuation = None
    best_state_score = float("-inf")
    for action, resulting_valuations in action_results.items():
        curr_player_state_score = calculate_state_score_for_player(
            current_player_name, resulting_valuations
        )
        if curr_player_state_score > best_state_score:
            best_state_score = curr_player_state_score
            best_resulting_valuation = resulting_valuations
            best_action = action

    assert (
        best_action is not None and best_resulting_valuation is not None
    ), "no best action found"
    return (best_action, best_resulting_valuation)


def value_state(
    game_state: gs.GameState, auction_has_occurred: bool
) -> Dict[str, float]:
    """
    Return the score of the current state for each player as a dictionary of [player_name, score].
    Search stops when at least 1 auction has occurred and the auction tiles are empty.
    If search does not stop, then continue propagation, and the value of the current state is the
    maximum across all possible actions the current player can take.
    """
    auction_tiles_are_empty = len(game_state.get_auction_tiles()) > 0
    if auction_has_occurred and auction_tiles_are_empty:
        return e.evaluate_game_state_no_auction_tiles(game_state)
    else:
        _best_move, resulting_player_state_valuations = search_internal(
            game_state, auction_has_occurred
        )
        return resulting_player_state_valuations


def calculate_state_score_for_player(
    player_name: str, player_state_valuations: Dict[str, float]
) -> float:
    """
    Given the valuations of each player's state, calculate a "state score" for a given player. This score
    represents how well the player is doing.

    Currently, this is calculated to be how far ahead the player is, or how far behind #1 the player is.
    """
    player_valuation = player_state_valuations[player_name]
    max_other_player_valuation = max(
        [
            valuation
            for name, valuation in player_state_valuations.items()
            if name != player_name
        ]
    )
    return player_valuation - max_other_player_valuation
