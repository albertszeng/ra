import random
import unittest

from game import info as gi
from game import ra


class RaTest(unittest.TestCase):
    def setUp(self) -> None:
        # Required since shuffling play order is used.
        random.seed(10)

    def test_serialize(self) -> None:
        self.maxDiff = None
        game = ra.RaGame(player_names=["P1", "P2"], randomize_play_order=True)
        game.init_game()
        self.assertEqual(
            game.serialize(), {**game.serialize(), **{"playerNames": ["P2", "P1"]}}
        )

    def test_integration_draw_6_ras(self) -> None:
        game = ra.RaGame(player_names=["P1", "P2"])

        num_ras_per_round = gi.NUM_RAS_PER_ROUND[2]
        round_action_list = [
            [str(gi.DRAW), str(gi.INDEX_OF_RA)],
            [str(gi.BID_NOTHING)],
            [str(gi.BID_NOTHING)],
        ] * (num_ras_per_round - 1) + [[str(gi.DRAW), str(gi.INDEX_OF_RA)]]

        game.load_actions(round_action_list)

        # Verify player scores
        player_scores = game.game_state.get_all_player_points().values()
        self.assertTrue(all(score == 8 for score in player_scores))

        # Verify 1 round has passed
        self.assertTrue(game.game_state.get_current_round() == 2)

        # Verify no new tiles have been drawn
        self.assertTrue(game.game_state.get_num_auction_tiles() == 0)

        # Verify center sun is still the default one
        self.assertTrue(game.game_state.get_center_sun() == gi.STARTING_CENTER_SUN)

        # Verify number of tiles drawn is expected
        self.assertTrue(
            game.game_state.get_num_tiles_left()
            == gi.STARTING_NUM_TILES - num_ras_per_round
        )

    def test_draw_tiles(self) -> None:
        game = ra.RaGame(player_names=["P1", "P2"])
        game.init_game()

        legal_actions = ra.get_possible_actions(game.game_state)
        tile_drawn = game.execute_action(gi.DRAW, legal_actions, gi.INDEX_OF_RA)
        self.assertEqual(tile_drawn, gi.INDEX_OF_RA)
        self.assertTrue(len(game.game_state.get_auction_tiles()) == 0)
        self.assertTrue(game.game_state.get_current_num_ras() == 1)
        try:
            game.serialize()
        except Exception as e:
            assert False, f"game serialization failed with error: {e}"

        game = ra.RaGame(player_names=["P1", "P2"])
        game.init_game()
        legal_actions = ra.get_possible_actions(game.game_state)
        tile_drawn = game.execute_action(gi.DRAW, legal_actions, gi.INDEX_OF_DIS_CIV)
        self.assertEqual(tile_drawn, gi.INDEX_OF_DIS_CIV)
        self.assertTrue(len(game.game_state.get_auction_tiles()) == 1)
        self.assertTrue(game.game_state.get_current_num_ras() == 0)
        try:
            game.serialize()
        except Exception as e:
            assert False, f"game serialization failed with error: {e}"

        game = ra.RaGame(player_names=["P1", "P2"])
        game.init_game()
        legal_actions = ra.get_possible_actions(game.game_state)
        tile_drawn = game.execute_action(gi.DRAW, legal_actions, gi.INDEX_OF_GOD)
        self.assertEqual(tile_drawn, gi.INDEX_OF_GOD)
        self.assertTrue(len(game.game_state.get_auction_tiles()) == 1)
        self.assertTrue(game.game_state.get_current_num_ras() == 0)
        try:
            game.serialize()
        except Exception as e:
            assert False, f"game serialization failed with error: {e}"


if __name__ == "__main__":
    unittest.main()
