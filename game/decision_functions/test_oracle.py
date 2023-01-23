"""
This test file is purposefully not run automatically with other unittests because
they may take a long time to run. You should run it manually if you want to
test the functions in oracle_search.py
"""

import random
import unittest

from game import info as gi
from game import ra
from game import state as gs
from game.decision_functions import oracle as o


class OracleSearchTest(unittest.TestCase):
    def setUp(self) -> None:
        # Required since tile bags are randomly ordered is used.
        random.seed(10)

    def test_oracle_search_internal_full_tiles(self) -> None:
        game_state = gs.GameState(["P1", "P2"])
        assert 2 in game_state.get_player_usable_sun(0)  # P1 has 2,5,6,9
        assert 3 in game_state.get_player_usable_sun(1)  # P2 has 3,4,7,8

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        best_move = o.oracle_search(game_state)
        self.assertEqual(best_move, gi.AUCTION)

    def test_oracle_search_internal_many_tiles(self) -> None:
        game_state = gs.GameState(["P1", "P2"])
        assert 2 in game_state.get_player_usable_sun(0)  # P1 has 2,5,6,9
        assert 3 in game_state.get_player_usable_sun(1)  # P2 has 3,4,7,8

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_GOLD)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P1

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P2

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PHAR)  # P1

        game_state.get_tile_bag().set_next_tile_to_be_drawn(gi.INDEX_OF_GOLD)

        best_move = o.oracle_search(game_state)
        self.assertEqual(best_move, gi.AUCTION)

    def test_oracle_search_some_tiles(self) -> None:
        game_state = gs.GameState(["P1", "P2"])
        assert 2 in game_state.get_player_usable_sun(0)  # P1 has 2,5,6,9
        assert 3 in game_state.get_player_usable_sun(1)  # P2 has 3,4,7,8

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_FORT)  # P1
        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PYR)  # P2
        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_STE)  # P1
        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_NILE)  # P2
        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_NILE)  # P1
        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_NILE)  # P2
        game_state.get_tile_bag().set_next_tile_to_be_drawn(gi.INDEX_OF_GOLD)

        best_move = o.oracle_search(game_state)
        self.assertEqual(best_move, gi.DRAW)

    def test_oracle_search_few_tiles(self) -> None:
        game_state = gs.GameState(["P1", "P2"])
        assert 2 in game_state.get_player_usable_sun(0)  # P1 has 2,5,6,9
        assert 3 in game_state.get_player_usable_sun(1)  # P2 has 3,4,7,8

        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_FORT)  # P1
        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_PYR)  # P2
        ra.execute_action_internal(game_state, gi.DRAW, None, gi.INDEX_OF_STE)  # P1

        best_move = o.oracle_search(game_state)
        self.assertEqual(best_move, gi.DRAW)

    def test_oracle_search_internal_no_tiles(self) -> None:
        game_state = gs.GameState(["P1", "P2"])
        assert 2 in game_state.get_player_usable_sun(0)  # P1 has 2,5,6,9
        assert 3 in game_state.get_player_usable_sun(1)  # P2 has 3,4,7,8

        best_move = o.oracle_search(game_state)
        self.assertEqual(best_move, gi.DRAW)

    def test_oracle_search_vary_auctions_allowed(self) -> None:
        for nPlayers in range(2, 6):
            game_state = gs.GameState([f"P{i + 1}" for i in range(nPlayers)])
            best_move = o.oracle_search(game_state)
            self.assertEqual(best_move, gi.DRAW)

    # def test_oracle_search_vary_auctions_allowed(self) -> None:
    #     import logging
    #     import sys

    #     root = logging.getLogger()
    #     root.setLevel(logging.DEBUG)
    #     handler = logging.StreamHandler(sys.stdout)
    #     handler.setLevel(logging.DEBUG)
    #     formatter = logging.Formatter(
    #         "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    #     )
    #     handler.setFormatter(formatter)
    #     root.addHandler(handler)

    #     # These are reasonable values for players.
    #     # 5 Player ==> 2 auctions takes 10s, 11mib
    #     # 4 Player ==> 2 auctions takes 3s, 5mib
    #     # 3 Player ==> 2 auctions takes 2s, 3.5mib
    #     # 2 Player ==> 3 auctions takes 7s, 12.8mib

    #     optimize = False
    #     auctionsToSearch = 3
    #     nPlayers = 2

    #     game_state = gs.GameState([f"P{i + 1}" for i in range(nPlayers)])

    #     print(f"\n==== Searching for {auctionsToSearch} auctions. ====")
    #     print(f"==== optimize={optimize} and players={nPlayers} ====")
    #     best_move = o.oracle_search(game_state, auctionsToSearch, optimize=optimize)
    #     # print("best_move:", best_move)
    #     # print("resulting_valuations:", resulting_valuations)
    #     # print("draw order:", game_state.get_tile_bag().get_draw_order())
    #     self.assertEqual(best_move, gi.DRAW)


if __name__ == "__main__":
    # import cProfile

    # cProfile.run("unittest.main()")
    unittest.main()
