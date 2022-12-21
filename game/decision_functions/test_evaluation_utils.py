from game import ra
from game import state as gs
from game import info as gi
from game.decision_functions import evaluation_utils as e

import random
import unittest


class RaTest(unittest.TestCase):
    def test_value_civs_not_second_civ(self) -> None:
        auction_tiles = [gi.INDEX_OF_ASTR]
        self.assertEqual(e.value_civs(0, 0, 10, 4), 0.) # no civs
        self.assertEqual(e.value_civs(0, 1, 10, 4), 0.) # no new civs
        self.assertEqual(e.value_civs(1, 0, 10, 4), 5.) # 1 new civ
        self.assertEqual(e.value_civs(3, 0, 10, 4), 10.) # 3 new civs
        self.assertEqual(e.value_civs(2, 2, 10, 4), 10.) # 2 additional civs

    def test_value_civs_second_civ(self) -> None:
        auction_tiles = [gi.INDEX_OF_ASTR]
        self.assertEqual(e.value_civs(2, 0, 10, 4), 7.25) # 2 new civs
        self.assertEqual(e.value_civs(1, 1, 10, 4), 2.25) # 1 additional civ
        self.assertEqual(e.value_civs(1, 1, 0, 4), 0.) # 1 additional civ
        self.assertEqual(e.value_civs(1, 1, 1, 4), 0.25) # 1 additional civ
        self.assertEqual(e.value_civs(1, 1, 10, 1), 0.) # 1 additional civ

if __name__ == "__main__":
    unittest.main()
