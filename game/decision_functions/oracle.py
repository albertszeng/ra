import logging
import pprint
import time
from typing import (
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    TypedDict,
    TypeVar,
    cast,
)

from typing_extensions import ParamSpec

from game import encoding
from game import info as gi
from game import ra
from game import state as gs
from game.decision_functions import evaluate_game_state as e
from game.decision_functions import search as s
from game.proxy import copy

logger: logging.Logger = logging.getLogger("uvicorn.info")

_MAX_RAS: int = max(gi.NUM_RAS_PER_ROUND.values())


def oracle_ai_player(game_state: gs.GameState) -> int:
    return oracle_search(game_state)


TAction = int
TPlayer = int
TScore = float


class Metrics(TypedDict):
    __slots__ = (
        "maxDepth",
        "cacheHit",
        "hitRate",
        "cacheMiss",
        "missRate",
        "numEnded",
        "percentEnded",
        "numEstimated",
        "percentEstimated",
        "numIntermediate",
        "percentIntermediate",
        "numAuctionStarted",
        "percentAuctionStarted",
        "numInRound",
        "percentInRound",
        "numCalls",
        "numRas",
        "percentRas",
    )
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
    numInRound: list[int]
    percentInRound: list[float]

    # numRas[i] is the number of unique states with i + 1 Ra's revealed.
    numRas: list[int]
    percentRas: list[float]

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
    metrics["percentRas"] = [
        100 * (num / max(1, metrics["cacheMiss"])) for num in metrics["numRas"]
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
        numInRound=[0] * gi.NUM_ROUNDS,
        percentInRound=[0.0] * gi.NUM_ROUNDS,
        numRas=[0] * _MAX_RAS,
        percentRas=[0.0] * _MAX_RAS,
    )


def oracle_search(
    game_state: gs.GameState,
    num_auctions_allowed: Optional[int] = None,
    optimize: bool = False,
    debug: bool = False,
) -> TAction:
    """
    Given the current game state, return an action to take and the valuation associated
    with it. Sees future tiles that will be drawn.
    """
    if debug:
        logger.info("Beginning oracle search...")
    start_time = time.time()
    metrics = default_metrics()
    internal_search_fn = oracle_search_stack if optimize else oracle_search_internal
    action_values = internal_search_fn(
        game_state,
        metrics,
        num_auctions_allowed or max(2, 4 - game_state.num_players),
        depth=0,
    )
    action = _get_best_action(game_state.get_current_player(), action_values)
    logger.info(f"Total unique states explored: {len(value_state.cache)}")
    logger.info(f"Collected metrics: {pprint.pformat(finalizeMetrics(metrics))}")
    logger.info(f"Search ended. Time elapsed: {(time.time() - start_time)} s")
    if len(value_state.cache) > 1e6:
        value_state.cache = {}
    return action


def _get_best_action(
    current_player: int, action_values: Mapping[TAction, tuple[TScore]]
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
        player_values = {idx: score for idx, score in enumerate(player_values)}
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
    def __init__(self, func: Callable[[gs.GameState, Metrics, int, ...], T]) -> None:
        # We store data in cache across requests?
        self.cache: Dict[int, int] = {}
        self.func: Callable[[gs.GameState, Metrics, int, ...], T] = func

    def __call__(
        self,
        gameState: gs.GameState,
        metrics: Metrics,
        max_auctions: int,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        metrics["numCalls"] += 1
        gameHash = hash((hash(gameState), max_auctions))
        if gameHash not in self.cache:
            metrics["cacheMiss"] += 1
            val = self.func(gameState, metrics, max_auctions, *args, **kwargs)
            self.cache[gameHash] = encoding.compress(val)
        else:
            metrics["cacheHit"] += 1
        val = cast(T, encoding.decompress(self.cache[gameHash]))
        return val


def _is_unsearchable(action: TAction) -> bool:
    # TODO(albertz): Allow golden god actions
    return action in [
        gi.GOD_1,
        gi.GOD_2,
        gi.GOD_3,
        gi.GOD_4,
        gi.GOD_5,
        gi.GOD_6,
        gi.GOD_7,
        gi.GOD_8,
    ]


def _is_bid(action: int) -> bool:
    return action in [gi.BID_1, gi.BID_2, gi.BID_3, gi.BID_4]


def filter_actions(actions: Iterable[int]) -> Iterator[int]:
    # Only ever return two actions.
    for action in actions:
        if _is_unsearchable(action):
            continue
        yield action


def oracle_search_stack(
    start_state: gs.GameState, metrics: Metrics, max_auctions: int, depth: int
) -> Dict[TAction, tuple[TScore]]:
    # same as internam search, but uses a stack to avoid recursive calls.

    # (game, depth, auctionsLeft)
    rootNode = (start_state, depth, max_auctions)
    stack: list[tuple[gs.GameState, int, int]] = [rootNode]
    cache: Dict[int, tuple[TScore]] = {}

    # We post-order traverse. Eg, process all children first, then the
    # parant game state.
    childValues: Dict[TAction, tuple[TScore]] = {}
    while stack:
        game_state, depth, auctionsLeft = stack[-1]
        metrics["maxDepth"] = max(depth, metrics["maxDepth"])
        gameHash = hash(game_state)
        # These are the terminal states.
        if game_state.is_game_ended():
            metrics["numCalls"] += 1
            metrics["cacheMiss"] += 1
            metrics["numInRound"][game_state.current_round - 1] += 1
            metrics["numEnded"] += 1
            cache[gameHash] = tuple(
                player_state.get_player_points()
                for player_state in game_state.player_states
            )
            stack.pop()
            continue
        elif auctionsLeft <= 0 and game_state.get_num_auction_tiles() == 0:
            metrics["numCalls"] += 1
            metrics["cacheMiss"] += 1
            metrics["numInRound"][game_state.current_round - 1] += 1
            metrics["numEstimated"] += 1
            ret = e.evaluate_game_state_no_auction_tiles(game_state)
            result = [0.0] * len(ret)
            for idx, score in ret.items():
                result[idx] = score
            cache[gameHash] = tuple(result)
            stack.pop()
            continue

        # We're in a non-terminal state, so continue the search.
        legal_actions = ra.get_possible_actions(game_state)
        assert (
            legal_actions is not None and len(legal_actions) > 0
        ), "Cannot perform oracle_search_stack because no legal actions"

        childValues = {}
        allChildrenProcessed = True
        for action in filter_actions(legal_actions):
            game_state_copy = copy.deepcopy(game_state)
            tile_drawn = ra.execute_action_internal(
                game_state_copy, action, legal_actions
            )
            nextStateHash = hash(game_state_copy)
            if nextStateHash in cache:
                childValues[action] = cache[nextStateHash]
                metrics["cacheHit"] += 1
                continue

            if action == gi.DRAW:
                assert tile_drawn is not None, "Oracle_search could not draw tile"
            auctionStarted = tile_drawn == gi.INDEX_OF_RA or action == gi.AUCTION
            allChildrenProcessed = False
            stack.append(
                (
                    game_state_copy,
                    depth + 1,
                    auctionsLeft - (1 if auctionStarted else 0),
                )
            )

        if allChildrenProcessed:
            # We finished one non-terminal state.
            metrics["numCalls"] += 1
            metrics["cacheMiss"] += 1
            metrics["numInRound"][game_state.current_round - 1] += 1
            metrics["numIntermediate"] += 1
            if game_state.is_auction_started():
                metrics["numAuctionStarted"] += 1
            cache[gameHash] = childValues[
                _get_best_action(game_state.get_current_player(), childValues)
            ]
            stack.pop()
            continue

    # The very last one processed is the root, so childValues.
    return childValues


def oracle_search_internal(
    game_state: gs.GameState,
    metrics: Metrics,
    max_auctions: int,
    depth: int,
) -> Dict[TAction, tuple[TScore]]:
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
    action_results: Dict[TAction, tuple[TScore]] = {}

    # Simulate each legal action and find their resulting valuations
    for action in filter_actions(legal_actions):
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
) -> tuple[TScore]:
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
    metrics["numRas"][game_state.num_ras_this_round] += 1
    if game_state.is_auction_started():
        metrics["numAuctionStarted"] += 1

    auction_tiles_are_empty = game_state.get_num_auction_tiles() == 0
    if game_state.is_game_ended():
        metrics["numEnded"] += 1
        final_scores = [0.0] * len(game_state.player_states)
        for player_state in game_state.player_states:
            final_scores[player_state.get_player_idx()] = float(
                player_state.get_player_points()
            )
        return tuple(final_scores)
    elif max_auctions <= 0 and auction_tiles_are_empty:
        metrics["numEstimated"] += 1
        ret = e.evaluate_game_state_no_auction_tiles(game_state)
        scores = [0.0] * len(ret)
        for idx, score in ret.items():
            scores[idx] = score
        return tuple(scores)
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
                game_state.get_current_player(), resulting_player_state_valuations
            )
        ]
