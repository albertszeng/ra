import unittest

from game import info as gi
from game import scoring_utils
from game import state as gs


class RaTest(unittest.TestCase):
    def test_calculate_value_of_auction_tiles(self) -> None:
        player1_state = gs.PlayerState(
            "P1", player_idx=0, starting_sun=gi.STARTING_SUN[2][:][0]
        )
        player2_state = gs.PlayerState(
            "P2", player_idx=1, starting_sun=gi.STARTING_SUN[2][:][1]
        )
        # dummy_ra_game = ra.RaGame(['P1', 'P2'])  # create a dummy ra game

        values0 = scoring_utils.calculate_value_of_auction_tiles(
            [], [player1_state, player2_state]
        )
        self.assertTrue(values0[0] == 0)
        self.assertTrue(values0[1] == 0)

        auction_tiles = [
            gi.INDEX_OF_GOD,
            gi.INDEX_OF_GOLD,
            gi.INDEX_OF_PHAR,
            gi.INDEX_OF_NILE,
            gi.INDEX_OF_FLOOD,
            gi.INDEX_OF_ASTR,
            gi.INDEX_OF_FORT,
        ]

        values1 = scoring_utils.calculate_value_of_auction_tiles(
            auction_tiles, [player1_state, player2_state]
        )
        self.assertTrue(values1[0] == 15)
        self.assertTrue(values1[1] == 15)

        player1_state.add_tiles(auction_tiles)
        values2 = scoring_utils.calculate_value_of_auction_tiles(
            auction_tiles, [player1_state, player2_state]
        )
        self.assertTrue(values2[0] == 7)
        self.assertTrue(values2[1] == 18)

        auction_tiles_2 = [
            gi.INDEX_OF_PHAR,
            gi.INDEX_OF_PHAR,
            gi.INDEX_OF_NILE,
            gi.INDEX_OF_NILE,
            gi.INDEX_OF_FORT,
            gi.INDEX_OF_FORT,
        ]
        values3 = scoring_utils.calculate_value_of_auction_tiles(
            auction_tiles_2, [player1_state, player2_state]
        )
        self.assertTrue(values3[0] == 7)
        self.assertTrue(values3[1] == 8)

    def test_calculate_unrealized_points(self) -> None:
        player1_state = gs.PlayerState(
            "P1", player_idx=0, starting_sun=gi.STARTING_SUN[2][:][0]
        )
        player2_state = gs.PlayerState(
            "P2", player_idx=1, starting_sun=gi.STARTING_SUN[2][:][1]
        )

        unrealized_points = scoring_utils.calculate_unrealized_points(
            [player1_state, player2_state], False
        )  # Not final round
        self.assertTrue(unrealized_points[0] == -2)
        self.assertTrue(unrealized_points[1] == -2)

        tiles = [
            gi.INDEX_OF_GOD,
            gi.INDEX_OF_GOLD,
            gi.INDEX_OF_PHAR,
            gi.INDEX_OF_NILE,
            gi.INDEX_OF_FLOOD,
            gi.INDEX_OF_ASTR,
            gi.INDEX_OF_FORT,
        ]
        player1_state.add_tiles(tiles)
        player1_state.exchange_sun(
            player1_state.get_usable_sun()[0], gi.STARTING_CENTER_SUN
        )

        unrealized_points2 = scoring_utils.calculate_unrealized_points(
            [player1_state, player2_state], False
        )  # Not final round
        self.assertTrue(unrealized_points2[0] == 12)
        self.assertTrue(unrealized_points2[1] == -7)

        unrealized_points3 = scoring_utils.calculate_unrealized_points(
            [player1_state, player2_state], True
        )  # Is final round
        self.assertTrue(unrealized_points3[0] == 8)
        self.assertTrue(unrealized_points3[1] == -2)


if __name__ == "__main__":
    unittest.main()
