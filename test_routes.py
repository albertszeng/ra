# import routes

import random
import unittest

from game import ra


class RoutesTest(unittest.TestCase):
    def test_get_game_repr(self) -> None:
        random.seed(10)
        self.maxDiff = None
        game = ra.RaGame(player_names=['P1', 'P2'], randomize_play_order=True)
        game.init_game()

        pass

    def test_list(self) -> None:
        pass

    def test_start(self) -> None:
        pass

    def test_action(self) -> None:
        pass
