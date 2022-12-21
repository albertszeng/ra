from game import info as gi

from typing import List, Mapping, Tuple

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

def value_3_gold(num_3_gold: int) -> float:
    return num_3_gold * 3

def value_golden_god(num_new_golden_gods: int, num_current_golden_gods: int) -> float:
    # TODO(albertz): need to factor in a variety of things, including:
    # - Time left in round, eg. num ra tiles left
    # - Whether the player will have time to use the golden god, eg. num suns left
    # - Number of "priority" tiles left, of which there are the following:
    #     - +3rd Copy Monument
    #     - +7th Distinct Monument
    #     - Civs
    # - Number of golden gods total, since generally only the first is very valuable

    if num_current_golden_gods == 0:
        first_god_value = 3 if num_new_golden_gods > 0 else 0
        additional_god_value = 2 * max(num_new_golden_gods - 1, 0)
        return first_god_value + additional_god_value
    else:
        return num_new_golden_gods * 2

def value_pharaohs(
    num_new_pharaohs: int,  # How many pharaohs are in the auction set
    num_current_pharaohs: int,  # How many pharaohs the player has currently
    num_opponent_pharaohs: Mapping[str, Tuple[int, bool]], # player_name -> (num pharaohs, is active)
    num_rounds_left_inc_this_one: int
) -> float:
    if num_new_pharaohs == 0:
        return 0

    assert num_rounds_left_inc_this_one > 0, "Cannot evaluate pharaohs if no rounds left"

    most_opposing_pharaohs_possible = 0
    most_opposing_pharaohs_currently = 0
    least_opposing_pharaohs_currently = 0
    for _player_name, (num_opp_pharaohs, is_active) in num_opponent_pharaohs.items():
        most_opposing_pharaohs_possible = max(most_opposing_pharaohs_possible, num_opp_pharaohs + (num_new_pharaohs if is_active else 0))
        most_opposing_pharaohs_currently = max(most_opposing_pharaohs_currently, num_opp_pharaohs)
        least_opposing_pharaohs_currently = min(least_opposing_pharaohs_currently, num_opp_pharaohs)
    num_opp_players_less_pharaohs = len([n for (n, _is_active) in num_opponent_pharaohs.values() if n < num_current_pharaohs])
    at_risk_of_becoming_last = (
        num_current_pharaohs > least_opposing_pharaohs_currently and
        num_opp_players_less_pharaohs == 1 and
        least_opposing_pharaohs_currently + num_new_pharaohs >= num_current_pharaohs
    )

    # if way ahead in pharaohs, value pharaohs lightly
    if num_current_pharaohs > most_opposing_pharaohs_possible:
        return num_new_pharaohs * num_rounds_left_inc_this_one

    # if currently winning pharaohs, but can be tied, value pharaohs moderately
    elif num_current_pharaohs >= most_opposing_pharaohs_possible:
        return num_new_pharaohs * (1 + 2 * (num_rounds_left_inc_this_one - 1))

    # if player is winning, but can be overtaken, value pharaohs highly
    elif num_current_pharaohs <= most_opposing_pharaohs_possible and num_current_pharaohs >= most_opposing_pharaohs_currently:
        return num_new_pharaohs * (2.5 + 2 * (num_rounds_left_inc_this_one - 1))

    # if player can take the lead, value pharaohs very highly
    elif num_current_pharaohs + num_new_pharaohs > most_opposing_pharaohs_currently:
        return num_new_pharaohs * (3.5 + 2.5 * (num_rounds_left_inc_this_one - 1))

    # if player can tie for the lead in pharaohs, value pharaohs highy but a bit less than above
    elif num_current_pharaohs + num_new_pharaohs == most_opposing_pharaohs_currently:
        return num_new_pharaohs * (2.5 + 1.5 * (num_rounds_left_inc_this_one - 1))

    # if player cannot reach the pharaoh leader, and is not at risk of being last, value pharaohs lightly
    elif num_current_pharaohs + num_new_pharaohs < most_opposing_pharaohs_currently and not at_risk_of_becoming_last:
        return num_new_pharaohs * num_rounds_left_inc_this_one

    # if player is at risk of being last or is last current but can overtake last, value pharaohs moderately
    elif at_risk_of_becoming_last or (num_current_pharaohs + num_new_pharaohs > least_opposing_pharaohs_currently and num_current_pharaohs <= least_opposing_pharaohs_currently):
        return 2 + (num_rounds_left_inc_this_one - 1)

    # the only remaining case should be if the player cannot catch up to 2nd to last. In this case, value pharoahs lightly.
    else:
        return num_new_pharaohs * num_rounds_left_inc_this_one
