"""
This test file is purposefully not run automatically with other unittests because
they may take a long time to run. You should run it manually if you want to
test the functions in search.py
"""

import unittest

from game import info as gi
from game import ra
from game import state as gs
from game.decision_functions import evaluate_game_state as e
from game.decision_functions import search as s


class SearchTest(unittest.TestCase):
    def test_calculate_state_score_for_player(self) -> None:
        state_valuations_1 = {
            "P1": 20.0,
            "P2": 10.0,
        }
        self.assertEqual(
            s.calculate_state_score_for_player("P1", state_valuations_1), 10.0
        )
        self.assertEqual(
            s.calculate_state_score_for_player("P2", state_valuations_1), -10.0
        )

        state_valuations_2 = {
            "P1": 20.0,
            "P2": 10.0,
            "P3": 5.0,
            "P4": -10.0,
        }
        self.assertEqual(
            s.calculate_state_score_for_player("P1", state_valuations_2), 10.0
        )
        self.assertEqual(
            s.calculate_state_score_for_player("P2", state_valuations_2), -10.0
        )
        self.assertEqual(
            s.calculate_state_score_for_player("P3", state_valuations_2), -15.0
        )
        self.assertEqual(
            s.calculate_state_score_for_player("P4", state_valuations_2), -30.0
        )

    def test_search_internal_full_tiles(self) -> None:
        game_state = gs.GameState(["P1", "P2"])
        assert 2 in game_state.get_player_usable_sun(0)  # P1 has 2,5,6,9
        assert 3 in game_state.get_player_usable_sun(1)  # P2 has 3,4,7,8

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        best_move, resulting_valuations = s.search_internal(game_state, False)
        print("best_move:", best_move)
        print("resulting_valuations:", resulting_valuations)
        self.assertEqual(best_move, gi.AUCTION)


if __name__ == "__main__":
    unittest.main()
