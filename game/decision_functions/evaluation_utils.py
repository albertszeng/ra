from game import info as gi

from typing import List

##### Top-level Evaluation Functions

def value_auction_tiles(
        auction_tiles: List[int],
        verbose: bool = True,  # will print out its reasoning
 ) -> float:
    """
    Estimate the "value" of a set of auction tiles.

    This does NOT correspond to the actual value of the tiles, but rather
    attempts to assign a number to auction tile sets such that more valuable
    sets have a higher number and less valuable sets have a lower number.
    Theoretically, there is no relation between the number returned by this
    function and the actual value of the tiles so long as the above requirement
    is upheld, though there is some attempt to not make the number too far
    off from the actual value of the tiles.
    """
    return 0


##### Helper Evaluation Functions

def value_civs(
    num_distinct_new_civs: int,  # The number of distinct civ tiles that the player does not have.
    num_distinct_current_civs: int,  # Number of distinct civ tiles the player currently has.
    ra_tiles_left_in_round: int,  # Number of ra tiles left before the round ends.
    how_many_sun_left: int,
) -> float:
    """
    Evaluate the worth of new civ tiles.
    """
    assert 0 <= num_distinct_new_civs and num_distinct_new_civs <= 5, f"cannot evaluate {num_distinct_new_civs} new civs"
    assert 0 <= num_distinct_current_civs and num_distinct_current_civs <= 5, f"there cannot be {num_distinct_current_civs} current civs"
    assert 0 <= ra_tiles_left_in_round and ra_tiles_left_in_round <= gi.NUM_RAS_PER_ROUND[5], f"there cannot be {ra_tiles_left_in_round} ra tiles left"

    def second_civ_value(ra_tiles_left_in_round: int, how_many_sun_left: int) -> float:
        # The less ra tiles left, the less valuable the 2nd civ is
        ra_tile_modifier: float = max(ra_tiles_left_in_round / 10., 0.)
        # The less suns the player has, the less valuable the 2nd civ is
        sun_modifier: float = max((how_many_sun_left - 1) / 4., 0.)
        return min(2.5 * ra_tile_modifier, 3 * sun_modifier)

    # The cumulative value of each new distinct civ
    cumulative_new_civ_values = {
        0: 0,
        1: 5,
        2: 5 + second_civ_value(ra_tiles_left_in_round, how_many_sun_left),
        3: 10,
        4: 15,
        5: 20
    }
    cumulative_current_civ_values = {
        0: 0,
        1: 5,
        2: 5,
        3: 10,
        4: 15,
        5: 20
    }
    return cumulative_new_civ_values[num_distinct_new_civs + num_distinct_current_civs] - cumulative_current_civ_values[num_distinct_current_civs]

def value_niles_and_flood(
    num_new_niles: int,
    num_new_floods: int,
    num_current_niles: int,
    num_current_floods: int,
    num_ras_left_in_current_round: int,
    num_rounds_left_inc_this_one: int
) -> float:
    # TODO(albertz): should factor in the number of ras left in the current round
    nile_value = num_new_niles * (num_rounds_left_inc_this_one * 0.5 + (0.5 if num_new_floods + num_current_floods > 0 else 0))
    flood_value = num_new_floods + (num_current_niles if num_current_floods == 0 else 0)
    return nile_value + flood_value
