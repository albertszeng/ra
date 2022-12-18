# flake8: noqa
import routes

import random
import unittest
import uuid

from game import ra
from unittest import mock

from typing import cast


class RoutesTest(unittest.TestCase):
    def test_get_game_repr(self) -> None:
        random.seed(10)
        self.maxDiff = None
        game = ra.RaGame(player_names=['P1', 'P2'], randomize_play_order=True)
        self.assertEqual(routes.get_game_repr(game),
                         r"""-------------------------------------------------
Player: P2

Sun of P2
Usable Sun: [2, 5, 6, 9]
Unusable Sun: []

Tiles of P2:

Points: 10

Player: P1

Sun of P1
Usable Sun: [3, 4, 7, 8]
Unusable Sun: []

Tiles of P1:

Points: 10


Round: 1
Num Ras This Round: 0
Center Sun: 1
Scores: 
    P2:                     10 points
    P1:                     10 points

Auction Tiles: 


Player To Move: P2


Possible actions:
    0: Draw a Tile
    1: Start an Auction

        User Action: """)

    def test_list_empty(self) -> None:
        self.assertEqual(routes.list(
            []), routes.ListGamesResponse(total=0, games=[]))

    def test_list_single(self) -> None:
        testID = '12345678123456781234567812345678'
        testGame = ra.RaGame(randomize_play_order=False,
                             player_names=['Name1', 'Name2'])
        self.assertEqual(routes.list([(testID, testGame)]),
                         routes.ListGamesResponse(
            total=1, games=[
                routes.GameInfo(
                    id=uuid.UUID('12345678123456781234567812345678'),
                    players=['Name1', 'Name2'])
            ]))

    def test_list_many(self) -> None:
        testIDs = ['12345678123456781234567812345678',
                   '23456781234567812345678123456781']
        testGames = [ra.RaGame(
            randomize_play_order=False, player_names=['Game10', 'Game11']),
            ra.RaGame(
            randomize_play_order=False, player_names=['Game20', 'Game21'])]
        self.assertEqual(routes.list(
            list(zip(testIDs, testGames))),
            routes.ListGamesResponse(total=2, games=[
                routes.GameInfo(
                    id=uuid.UUID('12345678123456781234567812345678'),
                    players=['Game10', 'Game11']),
                routes.GameInfo(
                    id=uuid.UUID('23456781234567812345678123456781'),
                    players=['Game20', 'Game21']),
            ]))

    def test_start_no_players(self) -> None:
        with self.assertRaises(ValueError):
            routes.start(uuid.uuid4(), [])
        with self.assertRaises(ValueError):
            routes.start(uuid.uuid4(), ['One'])

    def test_start(self) -> None:
        self.maxDiff = None
        gameID = uuid.uuid4()
        with mock.patch('builtins.open', mock.mock_open()) as m:
            game, response = routes.start(gameID, ['Player 1', 'Player 2'])
            m.assert_called_once_with(f'move_histories/{gameID}.txt', 'w+')

        self.assertEqual(response, routes.StartResponse(
            gameId=gameID,
            gameState=game.serialize(),
            gameAsStr=routes.get_game_repr(game),
        ))

    def test_action_game_ended(self) -> None:
        self.maxDiff = None
        game = ra.RaGame(
            player_names=['Player 1', 'Player 2'],
        )
        game.init_game()
        game.game_state.set_game_ended()
        self.assertEqual(routes.action(game, playerIdx=0, move='draw'),
                         routes.ActResponse(
            gameState=game.serialize(), gameAsStr=routes.get_game_repr(game)))

    def test_action_unrecognized(self) -> None:
        self.maxDiff = None
        game = ra.RaGame(
            player_names=['Player 1', 'Player 2'],
        )
        game.init_game()
        response = cast(routes.Message, routes.action(
            game, playerIdx=0, move='INVALID'))
        self.assertIsNotNone(response['message'])
        self.assertIn("Unrecognized", response['message'])

    def test_action_illegal_move(self) -> None:
        game = ra.RaGame(
            player_names=['Player 1', 'Player 2'],
        )
        game.init_game()
        response = cast(routes.Message, routes.action(
            game, playerIdx=0, move='god1'))
        self.assertIsNotNone(response['message'])
        self.assertIn('Only legal actions', response['message'])

    def test_action_wrong_player(self) -> None:
        game = ra.RaGame(
            player_names=['Player 1', 'Player 2'],
        )
        game.init_game()
        response = cast(routes.Message, routes.action(
            game, playerIdx=1, move='draw'))
        self.assertIsNotNone(response['message'])
        self.assertIn('Current player is', response['message'])

    def test_action(self) -> None:
        game = ra.RaGame(
            player_names=['Player 1', 'Player 2'],
        )
        game.init_game()
        response = routes.action(game, playerIdx=0, move='draw')

        self.assertGreater(len(game.logged_moves), 0)
        firstMove = game.logged_moves[0]
        self.assertTrue(isinstance(firstMove, tuple))
        self.assertEqual(firstMove[0], '0')
        self.assertEqual(response, routes.ActResponse(
            gameState=game.serialize(), gameAsStr=routes.get_game_repr(game)))

    def test_message_types(self) -> None:
        self.assertEqual(routes.ErrorMessage("Unused")["level"], "error")
        self.assertEqual(routes.WarningMessage("Unused")["level"], "warning")
        self.assertEqual(routes.InfoMessage("Unused")["level"], "info")
        self.assertEqual(routes.SuccessMessage("Unused")["level"], "success")
