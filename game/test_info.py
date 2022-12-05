import info

import unittest

from parameterized import parameterized  # pyre-ignore[21]


class InfoTests(unittest.TestCase):
    @parameterized.expand([  # pyre-ignore[56]
        (tile['name'], idx, tile) for idx, tile in enumerate(info.TILE_INFO)
    ])
    def test_tile_info(
            self, name: str, idx: int, tile: info.TileTypeInfo) -> None:
        self.assertEqual(info.tile_starting_num(tile), tile['startingNum'])
        self.assertEqual(info.tile_name(tile), tile['name'])
        self.assertEqual(info.index_to_tile(idx), tile)
        self.assertEqual(info.index_to_tile_name(idx), tile['name'])
        self.assertEqual(info.index_to_starting_num(idx), tile['startingNum'])

    @parameterized.expand([  # pyre-ignore[56]
        (tile['name'], idx) for idx, tile in enumerate(info.TILE_INFO)
        if tile['tileType'] == info.TileType.DISASTER
    ])
    def test_disaster(self, name: str, idx: int) -> None:
        self.assertTrue(info.index_is_disaster(idx))

    @parameterized.expand([  # pyre-ignore[56]
        (tile['name'], idx) for idx, tile in enumerate(info.TILE_INFO)
        if tile['tileType'] == info.TileType.RA
    ])
    def test_ra(self, name: str, idx: int) -> None:
        self.assertTrue(info.index_is_ra(idx))

    @parameterized.expand([  # pyre-ignore[56]
        (tile['name'], idx) for idx, tile in enumerate(info.TILE_INFO)
        if tile['tileType'] == info.TileType.COLLECTIBLE
    ])
    def test_collectible(self, name: str, idx: int) -> None:
        self.assertTrue(info.index_is_collectible(idx))

    @parameterized.expand([  # pyre-ignore[56]
        ('negative', -1),
        ('too_large', 24),
    ])
    def test_tile_idx_failure(self, name: str, idx: int) -> None:
        with self.assertRaises(AssertionError):
            info.index_to_tile(idx)
        with self.assertRaises(AssertionError):
            info.index_to_tile_name(idx)
        with self.assertRaises(AssertionError):
            info.index_to_starting_num(idx)
        with self.assertRaises(AssertionError):
            info.index_is_collectible(idx)
        with self.assertRaises(AssertionError):
            info.index_is_disaster(idx)
        with self.assertRaises(AssertionError):
            info.index_is_ra(idx)

    def test_list_of_temporary_collectible_indexes(self) -> None:
        self.assertEqual(info.list_of_temporary_collectible_indexes(), [
                         0, 1, 4, 5, 6, 7, 8, 9])

    def test_get_civs_from_collection(self) -> None:
        self.assertEqual(
            info.get_civs_from_collection(
                collection=[3, 1, 4, 2, 24, 2, 1, 4, 5, 3, 4, 1, 3]),
            [2, 1, 4, 5, 3])

        self.assertEqual(info.get_civs_from_collection(
            collection=[3, 1, 4, 2, 24, 2, 1, 4]), [2, 1, 4])

        self.assertEqual(info.get_civs_from_collection(
            collection=[3, 1, 4, 2, 24]), [])

        self.assertEqual(info.get_civs_from_collection(
            collection=[]), [])
