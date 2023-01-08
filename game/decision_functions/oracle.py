import pprint
import time
from typing import Callable, Dict, Generic, List, Mapping, TypedDict, TypeVar

from typing_extensions import ParamSpec

from game import copy
from game import info as gi
from game import ra
from game import state as gs
from game.decision_functions import evaluate_game_state as e
from game.decision_functions import search as s

DEFAULT_SEARCH_AUCTION_THRESHOLD = 1


def oracle_ai_player(game_state: gs.GameState) -> int:
    return oracle_search(game_state)


TAction = int
TPlayer = str
TScore = float


class Metrics(TypedDict):
    # Tracks the maximum search depth.
    maxDepth: int

    # The number of times we encountered a duplicated state.
    cacheHit: int
    # The percent of time we hit the cache (out of all fn calls)
    hitRate: float

    # The number of times we miss the cache.
    cacheMiss: int
    # The percent of time we miss the cache (out of all fn calls)
    missRate: float

    # The number of unique states which finished the game.
    numEnded: int
    percentEnded: float

    # The number of unique states for which we estimated a value.
    numEstimated: int
    percentEstimated: float

    # The number of unique intermediate states explored.
    numIntermediate: int
    percentIntermediate: float

    # The number of unique states with an ongoing auction.
    numAuctionStarted: int
    percentAuctionStarted: float

    # numInRound[i] is number of unique states in round i + 1.
    numInRound: List[int]
    percentInRound: List[float]

    # The number of times the function is called.
    numCalls: int


def finalizeMetrics(metrics: Metrics) -> Metrics:
    """Finalizes the metrics object by updating any rate values."""
    metrics["hitRate"] = 100 * (metrics["cacheHit"] / max(1, metrics["numCalls"]))
    metrics["missRate"] = 100 * (metrics["cacheMiss"] / max(1, metrics["numCalls"]))
    metrics["percentEnded"] = 100 * (metrics["numEnded"] / max(1, metrics["cacheMiss"]))
    metrics["percentEstimated"] = 100 * (
        metrics["numEstimated"] / max(1, metrics["cacheMiss"])
    )
    metrics["percentIntermediate"] = 100 * (
        metrics["numIntermediate"] / max(1, metrics["cacheMiss"])
    )
    metrics["percentAuctionStarted"] = 100 * (
        metrics["numAuctionStarted"] / max(1, metrics["cacheMiss"])
    )
    metrics["percentInRound"] = [
        100 * (num / max(1, metrics["cacheMiss"])) for num in metrics["numInRound"]
    ]

    return metrics


def default_metrics() -> Metrics:
    """Returns a metrics object with all default values."""
    return Metrics(
        maxDepth=0,
        cacheHit=0,
        hitRate=0,
        numEnded=0,
        percentEnded=0,
        numEstimated=0,
        percentEstimated=0,
        numCalls=0,
        cacheMiss=0,
        missRate=0,
        numIntermediate=0,
        percentIntermediate=0,
        numAuctionStarted=0,
        percentAuctionStarted=0,
        numInRound=[0, 0, 0],
        percentInRound=[0, 0, 0],
    )


def oracle_search(
    game_state: gs.GameState,
    num_auctions_allowed: int = DEFAULT_SEARCH_AUCTION_THRESHOLD,
) -> TAction:
    """
    Given the current game state, return an action to take and the valuation associated
    with it. Sees future tiles that will be drawn.
    """
    print("Beginning oracle search...")
    value_state.cache = {}
    start_time = time.time()
    metrics = default_metrics()
    action_values = oracle_search_internal(
        game_state,
        metrics,
        num_auctions_allowed,
        depth=0,
    )
    action = _get_best_action(game_state.get_current_player_name(), action_values)
    print(f"Total unique states explored: {len(value_state.cache)}")
    print(f"Collected metrics: {pprint.pformat(finalizeMetrics(metrics))}")
    print(f"Search ended. Time elapsed: {(time.time() - start_time)} s")
    return action


def _get_best_action(
    current_player: str, action_values: Mapping[TAction, Mapping[TPlayer, TScore]]
) -> TAction:
    """Returns the best action

    Args:
        current_player: The name of the player seeking to take an action.
        action_values: For each action, a mapping to the estimated score of each player
            after the specified action is taken.

    Returns:
        The action that leads to the current player having the highest rank.
    """
    best_action = None
    best_state_score = float("-inf")
    for action, player_values in action_values.items():
        curr_player_state_score = s.calculate_state_score_for_player(
            current_player, player_values
        )
        if curr_player_state_score > best_state_score:
            best_action = action
            best_state_score = curr_player_state_score

    assert best_action is not None, "no best action found"
    return best_action


T = TypeVar("T")
P = ParamSpec("P")


class CacheGames(Generic[T]):
    def __init__(self, func: Callable[[gs.GameState, Metrics, ...], T]) -> None:
        self.cache: Dict[gs.GameState, T] = {}
        self.func: Callable[[gs.GameState, Metrics, ...], T] = func

    def __call__(
        self,
        gameState: gs.GameState,
        metrics: Metrics,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        metrics["numCalls"] += 1
        if gameState not in self.cache:
            metrics["cacheMiss"] += 1
            self.cache[gameState] = self.func(gameState, metrics, *args, **kwargs)
        else:
            metrics["cacheHit"] += 1
        return self.cache[gameState]


def oracle_search_internal(
    game_state: gs.GameState,
    metrics: Metrics,
    max_auctions: int,
    depth: int,
) -> Dict[TAction, Dict[TPlayer, TScore]]:
    """Find action to take.

    Algorithm is based on minimax.

    Args:
        game_state: The state of the game from which to start the search. This
            state musth be hash-able.
        max_auctions: The maximum number of auctions to complete
            (eg, auction is performed an all tiles are taken).
        metrics: Stores statistics about the search.
        depth: Tracks how deep the current search has gone as measured by calls
            to `value_state` function.

    Returns:
        For each legal action in the current state, the value of the resulting
            state for each player.
    """
    legal_actions = ra.get_possible_actions(game_state)
    assert (
        legal_actions is not None and len(legal_actions) > 0
    ), "Cannot perform oracle_search_internal because no legal actions"

    # maps action to its resulting valuations
    action_results: Dict[TAction, Dict[TPlayer, TScore]] = {}

    # Simulate each legal action and find their resulting valuations
    for action in legal_actions:
        # TODO(albertz): Allow golden god actions
        if action in [
            gi.GOD_1,
            gi.GOD_2,
            gi.GOD_3,
            gi.GOD_4,
            gi.GOD_5,
            gi.GOD_6,
            gi.GOD_7,
            gi.GOD_8,
        ]:
            continue

        game_state_copy = copy.deepcopy(game_state)
        tile_drawn = ra.execute_action_internal(game_state_copy, action, legal_actions)
        if action == gi.DRAW:
            assert tile_drawn is not None, "Oracle_search could not draw tile"
        auctionStarted = tile_drawn == gi.INDEX_OF_RA or action == gi.AUCTION
        action_results[action] = value_state(
            game_state_copy,
            metrics,
            max_auctions - (1 if auctionStarted else 0),
            depth + 1,
        )

    # TODO(albertz): Uncomment this once we allow AI to do golden gods
    # assert len(action_results.keys()) == len(
    #     legal_actions
    # ), f"There are {len(action_results.keys())} action results but \
    #     {len(legal_actions)} legal actions"
    return action_results


@CacheGames
def value_state(
    game_state: gs.GameState,
    metrics: Metrics,
    max_auctions: int,
    depth: int,
) -> Dict[TPlayer, TScore]:
    """Computes the value of the state for each player.

    The value of the current state is the maximum across all possible actions
    the current player can take.

    Args:
        game_state: The state of the game to evaluate.
        max_auctions: The maximum number of auctions to complete
            (eg, auction is performed an all tiles are taken).
        metrics: Stores statistics about the search.
        depth: Keeps track of how deep the current search has gone.

    Returns:
        For each player, the value of this state from their POV.
    """
    metrics["maxDepth"] = max(metrics["maxDepth"], depth)
    metrics["numInRound"][game_state.current_round - 1] += 1
    if game_state.is_auction_started():
        metrics["numAuctionStarted"] += 1

    auction_tiles_are_empty = game_state.get_num_auction_tiles() == 0
    if game_state.is_game_ended():
        metrics["numEnded"] += 1
        final_scores = {}
        for player_state in game_state.player_states:
            final_scores[
                player_state.get_player_name()
            ] = player_state.get_player_points()
        return final_scores
    elif max_auctions <= 0 and auction_tiles_are_empty:
        metrics["numEstimated"] += 1
        return e.evaluate_game_state_no_auction_tiles(game_state)
    else:
        metrics["numIntermediate"] += 1
        resulting_player_state_valuations = oracle_search_internal(
            game_state,
            metrics,
            max_auctions,
            depth,
        )
        return resulting_player_state_valuations[
            _get_best_action(
                game_state.get_current_player_name(), resulting_player_state_valuations
            )
        ]
