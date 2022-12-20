from game import ra
from game import state as gs
from game import info as gi
from game.decision_functions import evaluation_utils as e

import random
import unittest


class RaTest(unittest.TestCase):
    def test_value_civs(self) -> None:
        auction_tiles = [gi.INDEX_OF_ASTR]
        self.assertEqual(e.value_civs(0, 0, 6, 3), 0) # no civs
        self.assertEqual(e.value_civs(0, 1, 6, 3), 0) # no new civs
        self.assertEqual(e.value_civs(1, 0, 6, 3), 5) # 1 new civ
        self.assertEqual(e.value_civs(2, 0, 6, 3), 7) # 2 new civs
        self.assertEqual(e.value_civs(1, 1, 6, 3), 2) # 1 additional civ
        self.assertEqual(e.value_civs(3, 0, 6, 3), 10) # 3 new civs
        self.assertEqual(e.value_civs(2, 2, 6, 3), 10) # 2 additional civs
        pass


if __name__ == "__main__":
    unittest.main()
