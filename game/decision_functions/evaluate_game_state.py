from typing import Dict, List, Mapping

from game import info as gi
from game import scoring_utils as scoring
from game import state as gs

STARTING_BASE_VALUE_OF_SUN = 6

SUN_MODIFIERS_2P: Mapping[int, float] = {
    1: -2.0,
    2: -1.5,
    3: -1.0,
    4: -0.5,
    5: 0.0,
    6: 0.5,
    7: 1.0,
    8: 1.5,
    9: 2.0,
}

SUN_MODIFIERS_3P_AND_4P: Mapping[int, float] = {
    1: -2.0,
    2: -1.67,
    3: -1.33,
    4: -1.0,
    5: -0.67,
    6: -0.33,
    7: 0.0,
    8: 0.33,
    9: 0.67,
    10: 1.0,
    11: 1.33,
    12: 1.67,
    13: 2.0,
}

SUN_MODIFIERS_5P: Mapping[int, float] = {
    1: -2.0,
    2: -1.625,
    3: -1.375,
    4: -1.125,
    5: -0.875,
    6: -0.625,
    7: -0.375,
    8: -0.125,
    9: 0.125,
    10: 0.375,
    11: 0.625,
    12: 0.875,
    13: 1.125,
    14: 1.375,
    15: 1.625,
    16: 2.0,
}

# Maps a number of players to the sun modifiers
SUN_MODIFIER_MAPPING: Mapping[int, Mapping[int, float]] = {
    2: SUN_MODIFIERS_2P,
    3: SUN_MODIFIERS_3P_AND_4P,
    4: SUN_MODIFIERS_3P_AND_4P,
    5: SUN_MODIFIERS_5P,
}


def evaluate_game_state_no_auction_tiles(game_state: gs.GameState) -> Dict[str, float]:
    """
    Given a gamestate, provide a "valuation" for each player's state. Does NOT factor in
    auction tiles into evaluation, so this should only be called if there are no
    auction tiles.

    The valuations for each player are NOT the same as the actual points they have, nor
    is it an estimation for how many points they will have. The only intended
    guarantee is that better states will have higher scores.

    TODO(albertz): If the game has ended, the valuation is simply the end-game points

    TODO(albertz): instead of using unrealized points, actually value their hand by
    evaluating:
    - Currently held tiles
       - Niles + Floods: need to value for future, based on ras remaining
       - Pharaohs: value based on differential from min and max, compared to expected
          pharaohs to be drawn in the current round
       - Civs: all 5 points, except 2nd civ is between 0-2 points based on num ras
          left in round
       - Monuments:
           - 1 point for first copy. 5 points for +3rd copy. If exactly 2 copies,
              2nd's value is modified by copies left in deck and ras left in game.
           - 6th distinct is valued at 2 points (if exactly 6). 7th distinct is valued
              at 4, 8th distinct is 5.
       - Golden God: just 2 points for now. In future, need to look for key tiles,
            ras left, etc.
       - 3 gold: just 3 gold
    """
    unrealized_points = scoring.calculate_unrealized_points(
        game_state.player_states, game_state.is_final_round()
    )
    usable_sun_valuations = value_of_usable_sun(game_state)
    unusable_sun_valuations = value_of_unusable_sun(game_state)

    # Each player's valuation is a sum of:
    # - their current points
    # - their unrealized points
    # - value of usable sun
    # - value of unusable sun
    player_state_valuations = {}
    for player_state in game_state.player_states:
        player_name = player_state.get_player_name()
        player_state_valuations[player_name] = (
            player_state.get_player_points()
            + unrealized_points[player_name]
            + usable_sun_valuations[player_name]
            + unusable_sun_valuations[player_name]
        )
    return player_state_valuations


def value_of_usable_sun(game_state: gs.GameState) -> Dict[str, float]:
    """
    Returns the valuation of each player's remaining sun.
    """
    usable_sun_valuations: Dict[str, float] = {}
    for player_state in game_state.player_states:
        usable_sun_valuations[
            player_state.get_player_name()
        ] = value_one_players_usable_sun(
            player_state.get_usable_sun(),
            game_state.get_num_players(),
            game_state.get_current_num_ras(),
        )
    return usable_sun_valuations


def value_one_players_usable_sun(
    usable_sun: List[int], num_players: int, num_ras_so_far: int
) -> float:
    """
    TODO(albertz): this needs to be much more complex, factoring in both how many
    opponent suns are left, and also what those opposing suns are.

    TODO(albertz): also, instead of having a mutliplicative sun_value_modifier,
    it can be a flat modifier based on how many sun tiles have been drawn compared to
    how many sun you have.

    TODO(albertz): rethink if we need to value usable sun differently if it's the final
    round, or whether it's already taken into account if we add unrealized points.
    """
    num_usable_sun = len(usable_sun)
    if num_usable_sun == 0:
        return 0.0
    num_starting_sun = len(gi.STARTING_SUN[num_players][0])
    num_ras_per_round = gi.NUM_RAS_PER_ROUND[num_players]

    # Decrease/Increase value of suns based on progress compared to ra tiles being drawn
    ra_progress: float = (num_ras_per_round - num_ras_so_far) / num_ras_per_round
    sun_progress: float = num_usable_sun / num_starting_sun

    # Cap sun_value_multiplier at 1.0
    # TODO(albertz): This cap may need to exist, but should be less brute force. In some
    # edge cases, eg. no one else has sun, this multiplier can be up to 2x.
    sun_value_multiplier = min(ra_progress / sun_progress, 1.0)

    sun_modifiers = SUN_MODIFIER_MAPPING[num_players]
    return sum(
        [
            (STARTING_BASE_VALUE_OF_SUN + sun_modifiers[sun]) * sun_value_multiplier
            for sun in usable_sun
        ]
    )


def value_of_unusable_sun(game_state: gs.GameState) -> Dict[str, float]:
    """
    Returns the valuation of each player's remaining sun. Does NOT
    give a value to unusable suns in the final round.
    """
    if game_state.is_final_round():
        # if final round, do not factor in unusable sun, because it's already taken into
        # account by the unrealized points
        return {name: 0.0 for name in game_state.get_player_names()}

    unusable_sun_valuations: Dict[str, float] = {}
    for player_state in game_state.player_states:
        unusable_sun_valuations[
            player_state.get_player_name()
        ] = value_one_players_unusable_sun(
            player_state.get_unusable_sun(), game_state.get_num_players()
        )
    return unusable_sun_valuations


def value_one_players_unusable_sun(unusable_sun: List[int], num_players: int) -> float:
    sun_modifiers = SUN_MODIFIER_MAPPING[num_players]
    return sum([sun_modifiers[sun] for sun in unusable_sun])
