import sys
from typing import Iterable, Mapping, Optional, Tuple, TypeVar

from game import info as gi
from game import state as gs
from game.proxy import copy

T = TypeVar("T")


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    for unit in ["Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_size(obj: T, seen: Optional[set[int]] = None) -> int:
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])  # pyre-ignore[16]
    return size


def calculate_round_end_points_gained(
    player_states: Iterable[gs.PlayerState], player_idx: Optional[int] = None
) -> Mapping[int, int]:
    """
    Calculates how many base-round-end points should be added for each
    player. Returns a mapping of player_idx -> points gained.
    Optionally provide a player name, and only the points for that player
    will be calced.
    """
    player_states_to_calc = (
        player_states
        if player_idx is None
        else [
            player_state
            for player_state in player_states
            if player_state.get_player_idx() == player_idx
        ]
    )
    assert (
        len(list(player_states_to_calc)) > 0
    ), f"Round points cannot \
    be calced for player '{player_idx}' because it does \
    not exist."

    points_gained = {
        player_state.get_player_idx(): 0 for player_state in player_states_to_calc
    }

    for player_state in player_states_to_calc:
        curret_player_idx = player_state.get_player_idx()

        # golden gods
        points_gained[curret_player_idx] += (
            player_state.collection[gi.INDEX_OF_GOD] * gi.POINTS_PER_GOD
        )

        # gold
        points_gained[curret_player_idx] += (
            player_state.collection[gi.INDEX_OF_GOLD] * gi.POINTS_PER_GOLD
        )

        # pharoahs
        least_num_pharoahs, most_num_pharoahs = least_and_most_num_pharoahs(
            player_states
        )
        if player_state.collection[gi.INDEX_OF_PHAR] == least_num_pharoahs:
            points_gained[curret_player_idx] += gi.POINTS_FOR_LEAST_PHAR
        if player_state.collection[gi.INDEX_OF_PHAR] == most_num_pharoahs:
            points_gained[curret_player_idx] += gi.POINTS_FOR_MOST_PHAR

        # niles and floods
        if player_state.collection[gi.INDEX_OF_FLOOD] > 0:
            points_gained[curret_player_idx] += (
                player_state.collection[gi.INDEX_OF_NILE]
                + player_state.collection[gi.INDEX_OF_FLOOD]
            )

        # civilizations
        points_gained[curret_player_idx] += gi.POINTS_FOR_CIVS[
            num_distinct_civs(player_state)
        ]

    return points_gained


def base_round_scoring(player_states: Iterable[gs.PlayerState]) -> None:
    """Gives points to each player based on tiles at end of round."""
    points_gained = calculate_round_end_points_gained(player_states)
    for player_state in player_states:
        player_state.add_points(points_gained[player_state.get_player_idx()])


def calculate_game_end_points_gained(
    player_states: Iterable[gs.PlayerState], player_idx: Optional[int] = None
) -> Mapping[int, int]:
    """
    Calculates how many game-end points should be added for each player.
    Returns a mapping of player_name -> points gained.
    Optionally provide a player name, and only the points for that player
    will be calced.
    """
    player_states_to_calc = (
        player_states
        if player_idx is None
        else [
            player_state
            for player_state in player_states
            if player_state.get_player_idx() == player_idx
        ]
    )
    assert (
        len(list(player_states_to_calc)) > 0
    ), f"Round points cannot \
    be calced for name '{player_idx}' because it \
    does not exist."

    points_gained = {
        player_state.get_player_idx(): 0 for player_state in player_states_to_calc
    }

    for player_state in player_states_to_calc:
        current_player_name = player_state.get_player_idx()

        # monuments
        points_gained[current_player_name] += monument_points(player_state)

        # suns
        least_suns, most_suns = least_and_most_suns(player_states)
        if sum_suns(player_state) == least_suns:
            points_gained[current_player_name] += gi.POINTS_FOR_LEAST_SUN
        if sum_suns(player_state) == most_suns:
            points_gained[current_player_name] += gi.POINTS_FOR_MOST_SUN

    return points_gained


def final_round_scoring(player_states: Iterable[gs.PlayerState]) -> None:
    """Gives points to each player based on final round scoring."""
    points_gained = calculate_game_end_points_gained(player_states)
    for player_state in player_states:
        player_state.add_points(points_gained[player_state.get_player_idx()])


def calculate_unrealized_points(
    player_states: Iterable[gs.PlayerState],
    is_final_round: bool,
) -> Mapping[int, int]:
    if is_final_round:
        round_end_points = calculate_round_end_points_gained(player_states)
        game_end_points = calculate_game_end_points_gained(player_states)
        return {
            playerIdx: round_end_points[playerIdx] + game_end_points[playerIdx]
            for playerIdx in round_end_points.keys()
        }
    else:
        return calculate_round_end_points_gained(player_states)


def calculate_value_of_auction_tiles(
    auction_tiles: Iterable[int], p_states: Iterable[gs.PlayerState]
) -> Mapping[int, int]:
    """
    Calculate how many points the current auction tiles would give each
    player. Return a mapping of player_idx -> points gained.
    """
    # TODO(albertz): Properly value disaster tiles
    relevant_auction_tiles = [
        tile
        for tile in auction_tiles
        if gi.TILE_INFO[tile]["tileType"] == gi.TileType.COLLECTIBLE
    ]

    # per player, calculate points gained if they had the auction tiles
    sim_p_states = copy.deepcopy(p_states)
    sim_p_gained = {p_state.get_player_idx(): 0 for p_state in p_states}
    for p_state in sim_p_states:
        cur_p_name = p_state.get_player_idx()
        p_state.add_tiles(relevant_auction_tiles)
        current_simulation_p_states = [
            base_p_state
            for base_p_state in p_states
            if base_p_state.get_player_idx() != cur_p_name
        ] + [p_state]

        cur_p_name = p_state.get_player_idx()
        sim_end_p_gained = calculate_round_end_points_gained(
            current_simulation_p_states, cur_p_name
        )
        sim_g_end_gained = calculate_game_end_points_gained(
            current_simulation_p_states, cur_p_name
        )
        sim_p_gained[cur_p_name] = (
            sim_end_p_gained[cur_p_name] + sim_g_end_gained[cur_p_name]
        )

    # for each player, calculate points gained without auction tiles
    def_p_gained = {p_state.get_player_idx(): 0 for p_state in p_states}
    def_end_p_gained = calculate_round_end_points_gained(p_states)
    default_game_end_points_gained = calculate_game_end_points_gained(p_states)
    for player_name in def_p_gained.keys():
        def_p_gained[player_name] += (
            def_end_p_gained[player_name] + default_game_end_points_gained[player_name]
        )

    # subtract default points gained from simulated points gained
    for player_name in sim_p_gained.keys():
        sim_p_gained[player_name] -= def_p_gained[player_name]

    return sim_p_gained


""" HELPER FUNCTIONS """


def least_and_most_num_pharoahs(
    player_states: Iterable[gs.PlayerState],
) -> Tuple[float, float]:
    least_so_far = float("inf")
    most_so_far = float("-inf")
    for player_state in player_states:
        least_so_far = min(least_so_far, player_state.collection[gi.INDEX_OF_PHAR])
        most_so_far = max(most_so_far, player_state.collection[gi.INDEX_OF_PHAR])
    return least_so_far, most_so_far


def num_distinct_civs(player_state: gs.PlayerState) -> int:
    collection_of_civs = gi.get_civs_from_collection(player_state.collection)
    return len([n for n in collection_of_civs if n > 0])


def sum_suns(player_state: gs.PlayerState) -> int:
    return sum(player_state.get_all_sun())


def least_and_most_suns(player_states: Iterable[gs.PlayerState]) -> Tuple[float, float]:
    least_so_far = float("inf")
    most_so_far = float("-inf")
    for player_state in player_states:
        least_so_far = min(least_so_far, sum_suns(player_state))
        most_so_far = max(most_so_far, sum_suns(player_state))
    return least_so_far, most_so_far


def monument_points(player_state: gs.PlayerState) -> int:
    monument_points = 0
    # monument copies
    monument_collection = gi.get_monuments_from_collection(player_state.collection)
    for amount in monument_collection:
        monument_points += gi.POINTS_FOR_MON_DEPTH[amount]

    # distinct monuments
    num_distinct = len([n for n in monument_collection if n > 0])
    monument_points += gi.POINTS_FOR_MON_BREADTH[num_distinct]

    return monument_points
