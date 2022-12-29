from typing import Dict

from game import scoring_utils as scoring
from game import state as gs

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

    TODO(albertz): actually implement this, by evaluating:
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
    - Usable sun
       - Value suns based on the average haul per sun (6 points), modified by:
           - [-2, +2] based on their rank,
           - num ras left in round, and maybe average value of tile?
    - Unusable sun
       - Modify score by [-2, +2] based on rank
       - In final round, calculate end-of-game suns
    """
    unrealized_points = scoring.calculate_unrealized_points(
        game_state.player_states, game_state.is_final_round()
    )
    return {
        player_state.get_player_name(): player_state.get_player_points()
        + unrealized_points[player_state.get_player_name()]
        for player_state in game_state.player_states
    }


def value_usable_sun(game_state: gs.GameState) -> Dict[str, float]:
    """
    Returns the valuation of each player's remaining sun.
    """
    # TODO(albertz): rethink if we need to value usable sun differently if it's the final round

    return {"a": 0.0}


def value_of_unusable_sun(game_state: gs.GameState) -> Dict[str, float]:
    """
    Returns the valuation of each player's remaining sun. Does NOT
    give a value to unusable suns in the final round.
    """
    if game_state.is_final_round():
        # if final round, do not factor in unusable sun, because it's already taken into
        # account by the unrealized points
        return {name: 0.0 for name in game_state.get_player_names()}

    sun_modifiers = SUN_MODIFIER_MAPPING[game_state.get_num_players()]
    unusable_sun_valuations: Dict[str, float] = {}
    for player_state in game_state.player_states:
        player_name = player_state.get_player_name()
        player_suns = player_state.get_unusable_sun()

        unusable_sun_valuations[player_name] = sum(
            [sun_modifiers[sun] for sun in player_suns]
        )
    return {"a": 0.0}


def value_one_players_unusable_sun(unusable_sun: List[str], num_players) -> float:
    sun_modifiers = SUN_MODIFIER_MAPPING[num_players]
    return sum([sun_modifiers[sun] for sun in unusable_sun])
