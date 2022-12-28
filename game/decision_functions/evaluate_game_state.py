from typing import Dict, List, Mapping, Tuple

from game import info as gi
from game import scoring_utils as scoring
from game import state as gs


def evaluate_game_state_no_auction_tiles(game_state: gs.GameState) -> Dict[str, float]:
    """
    Given a gamestate, provide a "score" for each player's state. Does NOT factor in
    auction tiles into evaluation, so this should only be called if there are no
    auction tiles.

    The scores for each player are NOT the same as the actual points they have, nor
    is it an estimation for how many points they will have. The only intended
    guarantee is that better states will have higher scores.
    """
    # TODO(albertz): actually implement this, by evaluating:
    # - Currently held tiles
    #    - Niles + Floods: need to value for future, based on ras remaining
    #    - Pharaohs: value based on differential from min and max, compared to expected pharaohs to be drawn in the current round
    #    - Civs: all 5 points, except 2nd civ is between 0-2 points based on num ras left in round
    #    - Monuments:
    #        - 1 point for first copy. 5 points for +3rd copy. If exactly 2 copies, 2nd's value is modified by copies left in deck and ras left in game.
    #        - 6th distinct is valued at 2 points (if exactly 6). 7th distinct is valued at 4, 8th distinct is 5.
    #    - Golden God: just 2 points for now. In future, need to look for key tiles, ras left, etc.
    #    - 3 gold: just 3 gold
    # - Usable sun
    #    - Value suns based on the average haul per sun (6 points), modified by:
    #        - [-2, +2] based on their rank,
    #        - num ras left in round, and maybe average value of tile?
    # - Unusable sun
    #    - Modify score by [-2, +2] based on rank
    #    - In final round, calculate end-of-game suns
    unrealized_points = scoring.calculate_unrealized_points(
        game_state.player_states, game_state.is_final_round()
    )
    return {
        player_state.get_player_name(): player_state.get_player_points()
        + unrealized_points[player_state.get_player_name()]
        for player_state in game_state.player_states
    }
