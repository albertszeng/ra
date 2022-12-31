import copy
import time
from typing import Dict, Tuple

from game import info as gi
from game import ra
from game import state as gs
from game.decision_functions import evaluate_game_state as e
from game.decision_functions import search as s

DEFAULT_SEARCH_AUCTION_THRESHOLD = 1


def oracle_ai_player(game_state: gs.GameState) -> int:
    return oracle_search(game_state)[0]


def oracle_search(
    game_state: gs.GameState,
    num_auctions_allowed: int = DEFAULT_SEARCH_AUCTION_THRESHOLD,
) -> Tuple[int, Dict[str, float]]:
    """
    Given the current game state, return an action to take and the valuation associated
    with it. Sees future tiles that will be drawn.
    """
    print("Beginning oracle search...")
    start_time = time.time()
    best_move, best_resulting_valuation = oracle_search_internal(
        game_state, num_auctions_allowed
    )
    print(f"Search ended. Time elapsed: {(time.time() - start_time)} s")
    return best_move, best_resulting_valuation


def oracle_search_internal(
    game_state: gs.GameState, num_auctions_left_to_occur: int
) -> Tuple[int, Dict[str, float]]:
    """
    Find action to take based on expectimax. Returns the best action and the
    resulting valuation of each player's state.

    Search stops when the number of auctions that have occurred drops below 1
    and the auction tiles are empty.
    """
    legal_actions = ra.get_possible_actions(game_state)
    assert (
        legal_actions is not None and len(legal_actions) > 0
    ), "Cannot perform oracle_search_internal because no legal actions"

    current_player_name = game_state.get_current_player_name()
    # maps action to its resulting valuations
    action_results: Dict[int, Dict[str, float]] = {}

    # Simulate each legal action and find their resulting valuations
    for action in legal_actions:
        if action == gi.DRAW:
            game_state_copy = copy.deepcopy(game_state)
            tile_drawn = ra.execute_action_internal(
                game_state_copy, action, legal_actions
            )
            assert tile_drawn is not None, "Oracle_search could not draw tile"
            action_results[action] = value_state(
                game_state_copy,
                num_auctions_left_to_occur - (1 if tile_drawn == gi.INDEX_OF_RA else 0),
            )

        # TODO(albertz): Allow golden god actions
        elif action in [
            gi.GOD_1,
            gi.GOD_2,
            gi.GOD_3,
            gi.GOD_4,
            gi.GOD_5,
            gi.GOD_6,
            gi.GOD_7,
            gi.GOD_8,
        ]:
            pass
        else:
            game_state_copy = copy.deepcopy(game_state)
            ra.execute_action_internal(game_state_copy, action, legal_actions)
            action_results[action] = value_state(
                game_state_copy,
                num_auctions_left_to_occur - (1 if action == gi.AUCTION else 0),
            )

    # TODO(albertz): Uncomment this once we allow AI to do golden gods
    # assert len(action_results.keys()) == len(
    #     legal_actions
    # ), f"There are {len(action_results.keys())} action results but \
    #     {len(legal_actions)} legal actions"

    # Pick the action that leads to the best resulting valuation for the current player
    best_action = None
    best_resulting_valuation = None
    best_state_score = float("-inf")
    for action, resulting_valuations in action_results.items():
        curr_player_state_score = s.calculate_state_score_for_player(
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
    game_state: gs.GameState, num_auctions_left_to_occur: int
) -> Dict[str, float]:
    """
    Return the score of the current state for each player as a dictionary of
    [player_name, score]. Search stops when the number of auctions that have
    occurred drops below 1 and the auction tiles are empty.
    If search does not stop, then continue propagation, and the value of the
    current state is the maximum across all possible actions the current player
    can take.
    """
    auction_tiles_are_empty = len(game_state.get_auction_tiles()) == 0

    if game_state.is_game_ended():
        final_scores = {}
        for player_state in game_state.player_states:
            final_scores[
                player_state.get_player_name()
            ] = player_state.get_player_points()
        return final_scores
    elif num_auctions_left_to_occur <= 0 and auction_tiles_are_empty:
        return e.evaluate_game_state_no_auction_tiles(game_state)
    else:
        _best_move, resulting_player_state_valuations = oracle_search_internal(
            game_state, num_auctions_left_to_occur
        )
        return resulting_player_state_valuations
