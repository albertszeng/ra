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
        game.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P2
        game.execute_action(gi.AUCTION)  # P1
        game.execute_action(gi.BID_NOTHING)  # P2
        game.execute_action(gi.BID_4)  # P1 bid 9

        evaluation2 = e.evaluate_game_state_no_auction_tiles(game.game_state)
        self.assertTrue(evaluation2["P1"] > evaluation2["P2"])

        game2 = ra.RaGame(player_names=["P1", "P2"], randomize_play_order=False)
        game2.init_game()
        self.assertTrue(evaluation["P1"] == evaluation["P2"])

        game2.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1
        game2.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P2
        game2.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1
        game2.execute_action(gi.DRAW, None, gi.INDEX_OF_GOLD)  # P2
        game2.execute_action(gi.AUCTION)  # P1
        game2.execute_action(gi.BID_NOTHING)  # P2
        game2.execute_action(gi.BID_1)  # P1 bid 2

        evaluation3 = e.evaluate_game_state_no_auction_tiles(game2.game_state)
        self.assertTrue(evaluation3["P1"] > evaluation3["P2"])
        self.assertTrue(
            evaluation3["P1"] > evaluation2["P1"]
        )  # bidding 2 better than bidding 9

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

    def test_value_one_players_usable_sun(self) -> None:
        usable_sun_0 = [2, 5, 8, 13]
        self.assert_close_enough(
            e.value_one_players_usable_sun(usable_sun_0, 3, 0), 24.0
        )

        usable_sun_1 = [2, 5, 8]
        self.assert_close_enough(
            e.value_one_players_usable_sun(usable_sun_1, 3, 2), 16.0
        )
        self.assert_close_enough(
            e.value_one_players_usable_sun(usable_sun_1, 3, 0), 16.0
        )

        usable_sun_3 = []
        self.assert_close_enough(
            e.value_one_players_usable_sun(usable_sun_3, 3, 0), 0.0
        )

        usable_sun_4 = [7]
        self.assert_close_enough(
            e.value_one_players_usable_sun(usable_sun_4, 4, 0), 6.0
        )
        self.assert_close_enough(
            e.value_one_players_usable_sun(usable_sun_4, 4, 8), 2.0
        )

    def test_value_of_usable_sun(self) -> None:
        game_state = gs.GameState(["P1", "P2"])

        usable_suns_valuations_1 = e.value_of_usable_sun(game_state)
        self.assert_close_enough(usable_suns_valuations_1["P1"], 25.0)  # [2,5,6,9]
        self.assert_close_enough(usable_suns_valuations_1["P2"], 25.0)  # [3,4,7,8]

        ra.execute_action_internal(game_state, gi.AUCTION)  # P1
        ra.execute_action_internal(game_state, gi.BID_1)  # P2 bids 3
        ra.execute_action_internal(game_state, gi.BID_NOTHING)  # P1
        usable_suns_valuations_2 = e.value_of_usable_sun(game_state)
        self.assert_close_enough(usable_suns_valuations_2["P1"], 25.0)  # [2,5,6,9]
        self.assert_close_enough(usable_suns_valuations_2["P2"], 20.0)  # [4,7,8]

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_RA)  # P2
        ra.execute_action_internal(game_state, gi.BID_NOTHING)  # P1
        ra.execute_action_internal(game_state, gi.BID_3)  # P2 bids 8
        usable_suns_valuations_3 = e.value_of_usable_sun(game_state)
        self.assert_close_enough(usable_suns_valuations_3["P1"], 20.83)  # [2,5,6,9]
        self.assert_close_enough(usable_suns_valuations_3["P2"], 12.5)  # [4,7]

    def assert_close_enough(self, n: float, m: float, epsilon: float = 0.1) -> None:
        """
        Asserts that n and m are within epsilon of each other.
        """
        self.assertTrue(
            abs(n - m) < epsilon,
            f"values {n} and {m} are not within {epsilon} of each other",
        )


if __name__ == "__main__":
    unittest.main()
