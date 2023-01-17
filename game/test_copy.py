import copy as sys_copy
import unittest

from game import state
from game.proxy import copy


class CopyTests(unittest.TestCase):
    def test_copy_tile_bag(self) -> None:
        tileBag = state.TileBag()
        self.assertEqual(tileBag, copy.deepcopy(tileBag))
        self.assertEqual(copy.deepcopy(tileBag), sys_copy.deepcopy(tileBag))

    def test_copy_player(self) -> None:
        player = state.PlayerState("test", [1, 3, 4])
        self.assertEqual(player, copy.deepcopy(player))
        self.assertEqual(copy.deepcopy(player), sys_copy.deepcopy(player))

    def test_copy_game(self) -> None:
        game = state.GameState(["test", "test2", "test3"])
        self.assertEqual(game, copy.deepcopy(game))
        self.assertEqual(copy.deepcopy(game), sys_copy.deepcopy(game))
