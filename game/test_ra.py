from . import ra

import random
import unittest


class RaTest(unittest.TestCase):
    def setUp(self) -> None:
        # Required since shuffling play order is used.
        random.seed(10)

    def test_serialize(self) -> None:
        self.maxDiff = None
        game = ra.RaGame(player_names=['P1', 'P2'], randomize_play_order=True)
        game.init_game()
        self.assertEqual(
            game.serialize(),
            {**game.serialize(), **{
                'player_names': ['P2', 'P1']}}
        )
