from game import ra
from game import state as gs
from game import info as gi
from game.decision_functions import evaluate_auction_tiles_utils as e

import random
import unittest


class RaTest(unittest.TestCase):
    def test_value_civs_not_second_civ(self) -> None:
        self.assertEqual(e.value_civs(0, 0, 10, 4), 0.) # 0 new civs
        self.assertEqual(e.value_civs(0, 0, 10, 4), 0.) # no civs
        self.assertEqual(e.value_civs(0, 1, 10, 4), 0.) # no new civs
        self.assertEqual(e.value_civs(1, 0, 10, 4), 5.) # 1 new civ
        self.assertEqual(e.value_civs(3, 0, 10, 4), 10.) # 3 new civs
        self.assertEqual(e.value_civs(2, 2, 10, 4), 10.) # 2 additional civs

    def test_value_civs_second_civ(self) -> None:
        self.assertEqual(e.value_civs(2, 0, 10, 4), 7.25) # 2 new civs
        self.assertEqual(e.value_civs(1, 1, 10, 4), 2.25) # 1 additional civ
        self.assertEqual(e.value_civs(1, 1, 0, 4), 0.) # 1 additional civ
        self.assertEqual(e.value_civs(1, 1, 1, 4), 0.25) # 1 additional civ
        self.assertEqual(e.value_civs(1, 1, 10, 1), 0.) # 1 additional civ

    def test_value_floods_and_niles(self) -> None:
        self.assertEqual(e.value_niles_and_flood(0, 0, 0, 0, 10, 3), 0.) # 0 new tiles
        self.assertEqual(e.value_niles_and_flood(1, 0, 0, 0, 10, 3), 1.5) # 1 new nile
        self.assertEqual(e.value_niles_and_flood(1, 1, 0, 0, 10, 3), 3) # 1 new nile, 1 new flood
        self.assertEqual(e.value_niles_and_flood(1, 0, 0, 1, 10, 3), 2) # 1 new nile, 1 current flood
        self.assertEqual(e.value_niles_and_flood(1, 0, 0, 1, 10, 1), 1) # 1 new nile, 1 current flood, 1 round left
        self.assertEqual(e.value_niles_and_flood(1, 0, 1, 1, 10, 3), 2) # 1 new nile, 1 current nile, 1 current flood
        self.assertEqual(e.value_niles_and_flood(1, 0, 5, 1, 10, 3), 2) # 1 new nile, 5 current nile, 1 current flood
        self.assertEqual(e.value_niles_and_flood(1, 1, 0, 1, 10, 3), 3) # 1 new nile, 1 new flood, 1 current flood
        self.assertEqual(e.value_niles_and_flood(1, 1, 5, 1, 10, 3), 3) # 1 new nile, 1 new flood, 5 current nile, 1 current flood
        self.assertEqual(e.value_niles_and_flood(0, 1, 5, 0, 10, 3), 6) # 1 new flood, 5 current nile
        self.assertEqual(e.value_niles_and_flood(0, 2, 5, 0, 10, 3), 7) # 2 new flood, 5 current nile
        self.assertEqual(e.value_niles_and_flood(3, 2, 5, 0, 10, 3), 13) # 2 new flood, 5 current nile
        self.assertEqual(e.value_niles_and_flood(3, 2, 5, 0, 10, 1), 10) # 2 new flood, 5 current nile, 1 round left

    def test_value_3_gold(self) -> None:
        self.assertEqual(e.value_3_gold(0), 0)
        self.assertEqual(e.value_3_gold(1), 3)
        self.assertEqual(e.value_3_gold(2), 6)
        self.assertEqual(e.value_3_gold(3), 9)

    def test_value_golden_god(self) -> None:
        self.assertEqual(e.value_golden_god(0, 0), 0)
        self.assertEqual(e.value_golden_god(1, 0), 3)
        self.assertEqual(e.value_golden_god(2, 0), 5)
        self.assertEqual(e.value_golden_god(3, 0), 7)
        self.assertEqual(e.value_golden_god(1, 1), 2)
        self.assertEqual(e.value_golden_god(2, 1), 4)
        self.assertEqual(e.value_golden_god(3, 1), 6)

    def test_value_pharaohs_tied_for_lead(self) -> None:
        self.assertEqual(e.value_pharaohs(0, 0, {"P2": (0, True)}, 1), 0)
        self.assertTrue(e.value_pharaohs(1, 0, {"P2": (0, True)}, 3) > 5)
        self.assertTrue(e.value_pharaohs(1, 0, {"P2": (0, True)}, 1) >= 2.5)
        self.assertTrue(e.value_pharaohs(1, 1, {"P2": (1, True)}, 1) >= 2.5)
        self.assertTrue(e.value_pharaohs(1, 3, {"P2": (3, True)}, 1) >= 2.5)
        self.assertTrue(e.value_pharaohs(1, 0, {"P2": (0, False)}, 1) >= 0)
        self.assertTrue(e.value_pharaohs(5, 0, {"P2": (0, True)}, 1) >= 5)
        self.assertTrue(e.value_pharaohs(5, 0, {"P2": (0, True), "P3": (0, True), "P4": (0, True)}, 1) >= 5)

    def test_value_pharaohs_can_overtake_lead(self) -> None:
        self.assertTrue(e.value_pharaohs(2, 0, {"P2": (1, True)}, 1) >= 5)
        self.assertTrue(e.value_pharaohs(4, 0, {"P2": (1, True)}, 1) >= 5)
        self.assertTrue(e.value_pharaohs(2, 0, {"P2": (1, True)}, 3) >= 8)
        self.assertTrue(e.value_pharaohs(4, 0, {"P2": (1, True)}, 3) >= 8)
        self.assertTrue(e.value_pharaohs(6, 0, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 3) >= 8)
        self.assertTrue(e.value_pharaohs(6, 1, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 3) >= 8)
        self.assertTrue(e.value_pharaohs(6, 2, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 3) >= 8)
        self.assertTrue(e.value_pharaohs(6, 3, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 3) >= 8)

    def test_value_pharaohs_winning_by_alot(self) -> None:
        self.assertTrue(e.value_pharaohs(1, 4, {"P2": (0, True)}, 3) >= 0)
        self.assertTrue(e.value_pharaohs(1, 4, {"P2": (1, True)}, 3) >= 0)
        self.assertTrue(e.value_pharaohs(2, 4, {"P2": (0, True)}, 3) >= 0)
        self.assertTrue(e.value_pharaohs(2, 4, {"P2": (0, True)}, 1) >= 0)
        self.assertTrue(e.value_pharaohs(2, 4, {"P2": (0, True), "P3": (1, True), "P4": (1, True)}, 3) >= 0)
        self.assertTrue(e.value_pharaohs(2, 4, {"P2": (0, True), "P3": (1, True), "P4": (1, True)}, 3) >= 0)

    def test_value_pharaohs_losing(self) -> None:
        self.assertTrue(e.value_pharaohs(1, 0, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 3) >= 0)
        self.assertTrue(e.value_pharaohs(2, 0, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 3) >= 2)
        self.assertTrue(e.value_pharaohs(1, 0, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 1) >= 0)
        self.assertTrue(e.value_pharaohs(2, 0, {"P2": (1, True), "P3": (4, True), "P4": (5, True)}, 3) >= 2)

if __name__ == "__main__":
    unittest.main()
