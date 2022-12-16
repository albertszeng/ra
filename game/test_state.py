import random
import unittest
from game import info as gi
from game import state as gs


class TileBagTests(unittest.TestCase):
    def setUp(self) -> None:
        self.num_iterations = 100
        self.num_draws = 5

    def test_starting_num_tiles(self) -> None:
        """Test that bag starts with right number of tiles."""
        t = gs.TileBag()
        starting_num_tiles = t.get_num_tiles_left()
        self.assertEqual(starting_num_tiles, gi.STARTING_NUM_TILES)
        self.assertEqual(gi.NUM_TILE_TYPES, len(t.get_bag_contents()))

    def test_single_draws(self) -> None:
        """Test that drawing single tiles are recorded properly."""
        for i in range(self.num_iterations):
            t = gs.TileBag()
            current_collection = t.get_bag_contents()
            num_tiles_left = t.get_num_tiles_left()
            for j in range(self.num_draws):
                tile_index_drawn = t.draw_tile()
                self.assertIsNotNone(tile_index_drawn)
                new_collection = t.get_bag_contents()
                self.assertEqual(
                    current_collection[tile_index_drawn],
                    new_collection[tile_index_drawn] + 1
                )
                self.assertEqual(
                    num_tiles_left,
                    t.get_num_tiles_left() + 1
                )
                current_collection = new_collection
                num_tiles_left = t.get_num_tiles_left()

    def test_drawing_all(self) -> None:
        """Test that drawing all the tiles results in an empty tile bag."""
        t = gs.TileBag()
        starting_num_tiles = t.get_num_tiles_left()
        for i in range(starting_num_tiles):
            _ = t.draw_tile()
        self.assertEqual(0, t.get_num_tiles_left())
        self.assertEqual([0] * gi.NUM_TILE_TYPES, t.get_bag_contents())
        self.assertEqual(None, t.draw_tile(log=False))


class PlayerStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.num_adds = 50  # number of times we add tiles
        self.num_iterations = 100
        self.max_sun = 10
        self.min_sun = 1
        self.num_sun = 10
        self.max_magnitude = 20  # max points we add to a player in a test

    def test_serialize(self) -> None:
        self.maxDiff = None
        player = gs.PlayerState("Test Player", starting_sun=[1, 2, 3])
        serialized = player.serialize()

        self.assertEqual(serialized, {**serialized, **{
            'points': 10,
            'playerName': "Test Player",
            'collection': [],
            'unusableSun': [],
        }})
        self.assertCountEqual(serialized['usableSun'], [1, 2, 3])

        player.add_points(10)
        self.assertEqual(player.serialize(),
                         {**player.serialize(), **{'points': 20}})

        # Check collection.
        player.add_tiles(
            [gi.INDEX_OF_GOLD, gi.INDEX_OF_GOLD, gi.INDEX_OF_PHAR, gi.INDEX_OF_NILE])
        self.assertCountEqual(player.serialize()['collection'], [
            gi.TILE_INFO[gi.INDEX_OF_GOLD],
            gi.TILE_INFO[gi.INDEX_OF_GOLD],
            gi.TILE_INFO[gi.INDEX_OF_PHAR],
            gi.TILE_INFO[gi.INDEX_OF_NILE],
        ])
        player.add_tiles(
            [gi.INDEX_OF_GOLD, gi.INDEX_OF_GOLD, gi.INDEX_OF_PHAR, gi.INDEX_OF_NILE])
        self.assertCountEqual(player.serialize()['collection'], [
            gi.TILE_INFO[gi.INDEX_OF_GOLD],
            gi.TILE_INFO[gi.INDEX_OF_GOLD],
            gi.TILE_INFO[gi.INDEX_OF_GOLD],
            gi.TILE_INFO[gi.INDEX_OF_GOLD],
            gi.TILE_INFO[gi.INDEX_OF_PHAR],
            gi.TILE_INFO[gi.INDEX_OF_PHAR],
            gi.TILE_INFO[gi.INDEX_OF_NILE],
            gi.TILE_INFO[gi.INDEX_OF_NILE],
        ])

        # Check swapping sun.
        player.exchange_sun(sun_to_give=2, sun_to_receive=13)
        self.assertCountEqual(player.serialize()['usableSun'], [1, 3])
        self.assertCountEqual(player.serialize()['unusableSun'], [13])

        player.exchange_sun(sun_to_give=3, sun_to_receive=9)
        self.assertCountEqual(player.serialize()['usableSun'], [1])
        self.assertCountEqual(player.serialize()['unusableSun'], [9, 13])

        player.exchange_sun(sun_to_give=1, sun_to_receive=4)
        self.assertCountEqual(player.serialize()['usableSun'], [])
        self.assertCountEqual(player.serialize()['unusableSun'], [4, 9, 13])

    def test_add_tiles(self) -> None:
        p_state = gs.PlayerState("Test Player", [1, 2, 3])
        current_collection = p_state.get_player_collection()

        # assert that collection starts empty
        self.assertEqual(sum(current_collection), 0)

        # check that adding tiles one at a time works
        for _i in range(self.num_adds):
            random_indx = random.randint(0, len(current_collection) - 1)
            current_collection[random_indx] += 1
            p_state.add_tiles([random_indx])
            self.assertEqual(current_collection,
                             p_state.get_player_collection())

        # check that adding tiles 3 at at ime works
        for _i in range(self.num_adds):
            random_indx_1 = random.randint(0, len(current_collection) - 1)
            random_indx_2 = random.randint(0, len(current_collection) - 1)
            random_indx_3 = random.randint(0, len(current_collection) - 1)
            current_collection[random_indx_1] += 1
            current_collection[random_indx_2] += 1
            current_collection[random_indx_3] += 1
            p_state.add_tiles([random_indx_1, random_indx_2, random_indx_3])
            self.assertEqual(current_collection,
                             p_state.get_player_collection())

    def test_remove_single_tiles_by_index(self) -> None:
        p_state = gs.PlayerState("Test Player", [1, 2, 3])
        added_tile_indexes = []
        for _i in range(self.num_adds):
            random_indx = random.randint(
                0, len(p_state.get_player_collection()) - 1)
            added_tile_indexes.append(random_indx)
        p_state.add_tiles(added_tile_indexes)
        current_collection = p_state.get_player_collection()

        # sanity check that tiles were added correctly
        self.assertEqual(sum(current_collection), self.num_adds)

        # check that removing tiles one at a time works
        for added_tile in added_tile_indexes:
            p_state.remove_single_tiles_by_index([added_tile], log=False)
            current_collection[added_tile] -= 1
            self.assertEqual(current_collection,
                             p_state.get_player_collection())

        # check that removing tiles all at once works
        p_state.add_tiles(added_tile_indexes)
        self.assertEqual(sum(p_state.get_player_collection()), self.num_adds)
        p_state.remove_single_tiles_by_index(added_tile_indexes, log=False)
        self.assertEqual(sum(p_state.get_player_collection()), 0)

        # check that removing tiles when there are none does nothing
        empty_collection = p_state.get_player_collection()
        for added_tile in added_tile_indexes:
            p_state.remove_single_tiles_by_index([added_tile], log=False)
            self.assertEqual(empty_collection, p_state.get_player_collection())

    def test_remove_all_tiles_by_index(self) -> None:
        p_state = gs.PlayerState("Test Player", [1, 2, 3])
        added_tile_indexes = []
        for _i in range(self.num_adds):
            random_indx = random.randint(
                0, len(p_state.get_player_collection()) - 1)
            added_tile_indexes.append(random_indx)
        p_state.add_tiles(added_tile_indexes)
        current_collection = p_state.get_player_collection()

        # sanity check that tiles were added correctly
        self.assertEqual(sum(current_collection), self.num_adds)

        # check that removing tiles one at a time works properly
        for added_tile in added_tile_indexes:
            p_state.remove_all_tiles_by_index([added_tile], log=False)
            current_collection[added_tile] = 0
            self.assertEqual(current_collection,
                             p_state.get_player_collection())

        # check that removing tiles all at once works
        p_state.add_tiles(added_tile_indexes)
        self.assertEqual(sum(p_state.get_player_collection()), self.num_adds)
        p_state.remove_all_tiles_by_index(added_tile_indexes, log=False)
        self.assertEqual(sum(p_state.get_player_collection()), 0)

        # check that removing tiles when there are none does nothing
        empty_collection = p_state.get_player_collection()
        for added_tile in added_tile_indexes:
            p_state.remove_all_tiles_by_index([added_tile], log=False)
            self.assertEqual(empty_collection, p_state.get_player_collection())
        return

    def test_exchange_sun(self) -> None:
        test_sun = []
        for i in range(self.num_sun):
            test_sun.append(random.randint(self.min_sun, self.max_sun))
        test_sun.sort()

        p_state = gs.PlayerState("Test Player", test_sun)

        # check that starting sun is correct and unusable sun is empty
        self.assertEqual(p_state.get_usable_sun(), test_sun)
        self.assertEqual(sum(p_state.get_unusable_sun()), 0)

        # check that exchanging sun works properly
        shuffled_test_sun = test_sun[:]
        random.shuffle(shuffled_test_sun)
        removed_sun = []
        added_sun = []
        for old_sun in test_sun:
            new_sun = random.randint(self.min_sun, self.max_sun)
            p_state.exchange_sun(old_sun, new_sun)
            removed_sun.append(old_sun)
            added_sun.append(new_sun)

            self.assertEqual(
                sorted(p_state.get_usable_sun() + removed_sun), test_sun)
            self.assertEqual(p_state.get_unusable_sun(), sorted(added_sun))

    def test_make_all_suns_usable(self) -> None:
        test_sun = []
        for i in range(self.num_sun):
            test_sun.append(random.randint(self.min_sun, self.max_sun))
        test_sun.sort()

        p_state = gs.PlayerState("Test Player", test_sun)

        # make all sun unusable
        added_suns = []
        for old_sun in test_sun:
            new_sun = random.randint(self.min_sun, self.max_sun)
            p_state.exchange_sun(old_sun, new_sun)
            added_suns.append(new_sun)
        added_suns.sort()

        # sanity check that all suns are unusable
        self.assertEqual(sum(p_state.get_usable_sun()), 0)
        self.assertEqual(p_state.get_unusable_sun(), added_suns)

        # check that all suns are made usable properly
        p_state.make_all_suns_usable()
        self.assertEqual(p_state.get_usable_sun(), added_suns)
        self.assertEqual(sum(p_state.get_unusable_sun()), 0)

    def test_add_points(self) -> None:
        p_state = gs.PlayerState("Test Player", [1, 2, 3])
        current_points = p_state.get_player_points()

        # check num_iterations times that adding points works properly
        for _i in range(self.num_iterations):
            diff = random.randint(-self.max_magnitude, self.max_magnitude)
            current_points += diff
            p_state.add_points(diff)
            self.assertEqual(current_points, p_state.get_player_points())


class GameStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.num_iterations = 100
        self.num_draws = 5

    def test_serialize_default(self) -> None:
        self.maxDiff = None
        g_state = gs.GameState(["Player 1", "Player 2"])
        self.assertEqual(g_state.serialize(), {**g_state.serialize(), **{
            'currentRound': 1,
            'activePlayers': [True, True],
            'numRasThisRound': 0,
            'centerSun': gi.STARTING_CENTER_SUN,
            'auctionTiles': [],
            'auctionSuns': [None, None],
            'auctionStarted': False,
            'currentPlayer': 0,
            'auctionWinningPlayer': None,
            'gameEnded': False,
        }})
        # Check player states.
        self.assertCountEqual(g_state.serialize()['playerStates'], [dict(
            collection=[],
            playerName='Player 1',
            points=10,
            unusableSun=[],
            usableSun=[2, 5, 6, 9],
        ),
            dict(
                collection=[],
                playerName='Player 2',
                points=10,
                unusableSun=[],
                usableSun=[3, 4, 7, 8],
        )])

    def test_serialize_changes(self) -> None:
        self.maxDiff = None
        g_state = gs.GameState(["Player 1", "Player 2"])
        g_state.increase_round_number()
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(), **{'currentRound': 2}})

        g_state.increase_num_ras_this_round()
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(),
                          **{'numRasThisRound': 1}})

        g_state.add_tile_to_auction_tiles(gi.INDEX_OF_GOD)
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(), **{'auctionTiles': [
                             gi.TILE_INFO[gi.INDEX_OF_GOD]]}})

        g_state.set_auction_winning_player(winning_player=1)
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(),
                          **{'auctionWinningPlayer': 1}})

        g_state.set_current_player(new_player_index=1)
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(),
                          **{'currentPlayer': 1}})

        g_state.mark_player_passed(player_index=1)
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(),
                          **{'activePlayers': [True, False]}})

        g_state.start_auction(forced=True, start_player=0)
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(),
                          **{'auctionStarted': True}})

        g_state.add_auction_sun(player=1, sun=4)
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(),
                          **{'auctionSuns': [None, 4]}})

        g_state.set_center_sun(new_sun=4)
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(),
                          **{'centerSun': 4}})

        g_state.set_game_ended()
        self.assertEqual(g_state.serialize(),
                         {**g_state.serialize(), **{'gameEnded': True}})

    def test_increase_round_number(self) -> None:
        g_state = gs.GameState(["Test Player 1", "Test Player 2"])
        max_rounds = g_state.get_total_rounds()
        starting_round = g_state.get_current_round()

        # check that increasing rounds works properly
        for i in range(max_rounds - starting_round):
            g_state.increase_round_number()
            self.assertEqual(g_state.get_current_round(),
                             starting_round + i + 1)

        # check that increasing rounds when on the last round throws an error
        with self.assertRaises(Exception):
            g_state.increase_round_number()

    def test_single_draws(self) -> None:
        # test that drawing single tiles are recorded properly
        for i in range(self.num_iterations):
            g_state = gs.GameState(["Test Player 1", "Test Player 2"])
            current_collection = g_state.get_tile_bag_contents()
            num_tiles_left = g_state.get_num_tiles_left()
            for j in range(self.num_draws):
                tile_index_drawn = g_state.draw_tile()
                self.assertIsNotNone(tile_index_drawn)
                new_collection = g_state.get_tile_bag_contents()
                self.assertEqual(
                    current_collection[tile_index_drawn],
                    new_collection[tile_index_drawn] + 1
                )
                self.assertEqual(
                    num_tiles_left,
                    g_state.get_num_tiles_left() + 1
                )
                current_collection = new_collection
                num_tiles_left = g_state.get_num_tiles_left()

    def test_drawing_all(self) -> None:
        g_state = gs.GameState(["Test Player 1", "Test Player 2"])

        # test that drawing all the tiles results in an empty tile bag
        starting_num_tiles = g_state.get_num_tiles_left()
        for _i in range(starting_num_tiles):
            _ = g_state.draw_tile()
        self.assertEqual(0, g_state.get_num_tiles_left())
        self.assertEqual(
            [0] * gi.NUM_TILE_TYPES,
            g_state.get_tile_bag().get_bag_contents()
        )

        # test that trying to draw a tile after none are left returns none
        self.assertEqual(None, g_state.draw_tile(log=False))

    def test_increase_num_ras_this_round(self) -> None:
        g_state = gs.GameState(["Test Player 1", "Test Player 2"])

        max_ras = g_state.get_num_ras_per_round()
        starting_num_ras = g_state.get_current_num_ras()

        # sanity check that game starts with 0 ras
        self.assertEqual(starting_num_ras, 0)

        # test that ras are incremented by 1 properly
        for i in range(max_ras):
            g_state.increase_num_ras_this_round()
            self.assertEqual(g_state.get_current_num_ras(), i + 1)

        # test thhat trying to increase num ras more than max throws excpetion
        with self.assertRaises(Exception):
            g_state.increase_num_ras_this_round()

    def test_reset_num_ras_this_round(self) -> None:
        g_state = gs.GameState(["Test Player 1", "Test Player 2"])

        max_ras = g_state.get_num_ras_per_round()
        starting_num_ras = g_state.get_current_num_ras()

        # sanity check that game starts with 0 ras
        self.assertEqual(starting_num_ras, 0)

        # test that ras are reset properly
        for i in range(self.num_iterations):
            num_ras_to_add = random.randint(1, max_ras)
            for j in range(num_ras_to_add):
                g_state.increase_num_ras_this_round()
            self.assertEqual(num_ras_to_add, g_state.get_current_num_ras())
            g_state.reset_num_ras_this_round()
            self.assertEqual(0, g_state.get_current_num_ras())

    # testing: add_tile_to_auction_tiles, remove_auction_tile
    def test_add_remove_auction_tiles(self) -> None:
        g_state = gs.GameState(["Test Player 1", "Test Player 2"])
        max_index = gi.NUM_AUCTIONABLE_TILE_TYPES - 1
        max_auction_tiles = g_state.get_max_auction_tiles()

        # test add and remove
        for _i in range(self.num_iterations):
            tiles_added = []

            # check that adding auction tiles works
            for _j in range(max_auction_tiles):
                rand_tile = random.randint(0, max_index - 1)
                tiles_added.append(rand_tile)
                g_state.add_tile_to_auction_tiles(rand_tile)
                self.assertEqual(tiles_added, g_state.get_auction_tiles())

            # check that adding too many auction tiles doesn't work
            rand_tile = random.randint(0, max_index - 1)
            with self.assertRaises(Exception):
                g_state.add_tile_to_auction_tiles(rand_tile)

            # check that removing auction tiles works
            for _j in range(len(tiles_added)):
                indx_to_remove = random.randint(0, len(tiles_added) - 1)
                tiles_added.pop(indx_to_remove)
                g_state.remove_auction_tile(indx_to_remove)

                self.assertEqual(tiles_added, g_state.get_auction_tiles())

    def test_clear_auction_tiles(self) -> None:
        g_state = gs.GameState(["Test Player 1", "Test Player 2"])
        max_index = gi.NUM_AUCTIONABLE_TILE_TYPES
        max_auction_tiles = g_state.get_max_auction_tiles()

        for _i in range(self.num_iterations):
            num_to_add = random.randint(0, max_auction_tiles)
            tiles_added = []

            # check that adding auction tiles works
            for _j in range(num_to_add):
                rand_tile = random.randint(0, max_index - 1)
                tiles_added.append(rand_tile)
                g_state.add_tile_to_auction_tiles(rand_tile)
                self.assertEqual(tiles_added, g_state.get_auction_tiles())

            # check that clearing auction tiles works
            g_state.clear_auction_tiles()
            self.assertEqual(g_state.get_auction_tiles(), [])

    def test_give_tiles_to_player(self) -> None:
        g_state = gs.GameState(["Test Player 1", "Test Player 2"])

        for _i in range(self.num_iterations):
            auction_tiles = []
            # add a random number of collectible tiles to a list
            num_auction_tiles = random.randint(
                1, g_state.get_max_auction_tiles() - 1)
            for _j in range(num_auction_tiles):
                t = g_state.draw_tile(log=False)
                if t is None:
                    break
                if gi.index_is_collectible(t):
                    auction_tiles.append(t)

            player_index = random.randint(0, 1)
            old_player_collection = g_state.get_player_collection(player_index)

            g_state.give_tiles_to_player(player_index, auction_tiles)

            new_player_collection = g_state.get_player_collection(player_index)

            # check that new player collection has 1 more of each auction tile
            for tile in auction_tiles:
                self.assertEqual(
                    old_player_collection[tile] + auction_tiles.count(tile),
                    new_player_collection[tile]
                )

    def test_set_current_player(self) -> None:
        g_state = gs.GameState(
            ["Test Player 1", "Test Player 2", "Test Player 3"])
        num_players = g_state.get_num_players()

        # check that current player can be set properly
        for _i in range(self.num_iterations):
            new_current_player = random.randint(0, num_players - 1)
            g_state.set_current_player(new_current_player)
            self.assertEqual(new_current_player, g_state.get_current_player())

        # check that exceptions are thrown if invalid player numbers are given
        with self.assertRaises(Exception):
            g_state.set_current_player(-1)

        with self.assertRaises(Exception):
            g_state.set_current_player(g_state.get_num_players() + 1)

    def test_mark_player_passed(self) -> None:
        for _i in range(self.num_iterations):
            g_state = gs.GameState(
                ["Test Player 1", "Test Player 2", "Test Player 3"])
            player_indexes = [0, 1, 2]
            random.shuffle(player_indexes)

            # mark players passed and make sure they are properly marked
            for index in player_indexes:
                g_state.mark_player_passed(index)
                self.assertTrue(not g_state.is_player_active(index))

    def test_reset_active_players(self) -> None:
        for _i in range(self.num_iterations):
            g_state = gs.GameState(
                ["Test Player 1", "Test Player 2", "Test Player 3"])

            # mark some players passed
            player_indexes = [0, 1, 2]
            random.shuffle(player_indexes)
            player_indexes = player_indexes[:(random.randint(0, 3))]
            for index in player_indexes:
                g_state.mark_player_passed(index)

            # mark all players active
            g_state.reset_active_players()

            # make sure all players active
            for j in range(3):
                self.assertTrue(g_state.is_player_active(j))

    def test_get_next_active_player(self) -> None:
        pass

    def test_advance_current_player(self) -> None:
        pass

    # testing: set_auction_start_player, remove_auction_start_player
    def test_set_remove_auction_start_player(self) -> None:
        pass

    # testing: start_auction, end_auction, add_auction_sun,
    # clear_auction_suns
    def test_auction_functions(self) -> None:
        pass

    def test_add_points_for_player(self) -> None:
        pass

    def test_current_player_has_god(self) -> None:
        pass

    def test_is_auction_started(self) -> None:
        pass
