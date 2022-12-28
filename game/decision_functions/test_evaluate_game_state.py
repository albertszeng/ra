import random
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

        legal_actions = ra.get_possible_actions(game.game_state)
        assert legal_actions is not None, "Game has not ended."
        game.execute_action(gi.DRAW, legal_actions, gi.INDEX_OF_GOLD)  # P1
        legal_actions = ra.get_possible_actions(game.game_state)
        assert legal_actions is not None, "Game has not ended."
        game.execute_action(gi.DRAW, legal_actions, gi.INDEX_OF_GOLD)  # P2
        legal_actions = ra.get_possible_actions(game.game_state)
        assert legal_actions is not None, "Game has not ended."
        game.execute_action(gi.DRAW, legal_actions, gi.INDEX_OF_GOLD)  # P1
        legal_actions = ra.get_possible_actions(game.game_state)
        assert legal_actions is not None, "Game has not ended."
        game.execute_action(gi.AUCTION, legal_actions)  # P2
        legal_actions = ra.get_possible_actions(game.game_state)
        assert legal_actions is not None, "Game has not ended."
        game.execute_action(gi.BID_4, legal_actions)  # P1  # bid highest
        legal_actions = ra.get_possible_actions(game.game_state)
        assert legal_actions is not None, "Game has not ended."
        game.execute_action(gi.BID_NOTHING, legal_actions)  # P2  # bid nothing

        evaluation2 = e.evaluate_game_state_no_auction_tiles(game.game_state)
        self.assertTrue(evaluation2["P1"] > evaluation2["P2"])


if __name__ == "__main__":
    unittest.main()
