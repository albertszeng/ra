import unittest

from game import info as gi
from game import ra
from game import state as gs
from game.decision_functions import evaluate_game_state as e


class EvaluateGameStateTest(unittest.TestCase):
    def test_evaluate_game_state_no_auction_tiles(self) -> None:
        game = ra.RaGame(player_names=["P1", "P2"], randomize_play_order=False)
        game.init_game()
        evaluation = e.evaluate_game_state_no_auction_tiles(game.game_state)
        self.assertTrue(evaluation["P1"] == evaluation["P2"])

        game.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1
        game.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P2
        game.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1
        game.execute_action(gi.AUCTION)  # P2
        game.execute_action(gi.BID_4)  # P1  # bid highest
        game.execute_action(gi.BID_NOTHING)  # P2  # bid nothing

        evaluation2 = e.evaluate_game_state_no_auction_tiles(game.game_state)
        self.assertTrue(evaluation2["P1"] > evaluation2["P2"])

    def test_value_one_players_unusable_sun(self) -> None:
        unusable_sun_0 = []
        self.assertEqual(e.value_one_players_unusable_sun(unusable_sun_0, 3), 0.0)

        unusable_sun_1 = [1]
        self.assertEqual(e.value_one_players_unusable_sun(unusable_sun_1, 3), -2.0)

        unusable_sun_2 = [1]
        self.assertEqual(e.value_one_players_unusable_sun(unusable_sun_2, 5), -2.0)

        unusable_sun_3 = [1, 2]
        self.assertEqual(e.value_one_players_unusable_sun(unusable_sun_3, 5), -3.625)

        unusable_sun_4 = [1, 2, 14]
        self.assertEqual(e.value_one_players_unusable_sun(unusable_sun_4, 5), -2.25)

    def test_value_of_unusable_sun(self) -> None:
        game_state = gs.GameState(["P1", "P2"])

        unusable_suns_valuations_1 = e.value_of_unusable_sun(game_state)
        self.assertEqual(unusable_suns_valuations_1["P1"], 0.0)  # No unusable sun
        self.assertEqual(unusable_suns_valuations_1["P2"], 0.0)  # No unusable sun

        ra.execute_action_internal(game_state, gi.AUCTION)  # P1
        ra.execute_action_internal(game_state, gi.BID_1)  # P2 bids 3, gets 1
        ra.execute_action_internal(game_state, gi.BID_NOTHING)  # P1
        unusable_suns_valuations_2 = e.value_of_unusable_sun(game_state)
        self.assertEqual(unusable_suns_valuations_2["P1"], 0.0)  # No unusable sun
        self.assertEqual(unusable_suns_valuations_2["P2"], -2.0)  # [1]

        ra.execute_action_internal(game_state, gi.AUCTION)  # P2
        ra.execute_action_internal(game_state, gi.BID_NOTHING)  # P1
        ra.execute_action_internal(game_state, gi.BID_3)  # P2 bids 8, gets 3
        unusable_suns_valuations_3 = e.value_of_unusable_sun(game_state)
        self.assertEqual(unusable_suns_valuations_3["P1"], 0.0)  # No unusable sun
        self.assertEqual(unusable_suns_valuations_3["P2"], -3.0)  # [1, 3]

        ra.execute_action_internal(game_state, gi.AUCTION)  # P1
        ra.execute_action_internal(game_state, gi.BID_1)  # P2 bids 4, gets 8
        ra.execute_action_internal(game_state, gi.BID_NOTHING)  # P1
        unusable_suns_valuations_4 = e.value_of_unusable_sun(game_state)
        self.assertEqual(unusable_suns_valuations_4["P1"], 0.0)  # No unusable sun
        self.assertEqual(unusable_suns_valuations_4["P2"], -1.5)  # [1, 3]


if __name__ == "__main__":
    unittest.main()
