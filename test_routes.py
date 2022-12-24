# flake8: noqa
import routes

import random
import unittest
import uuid

from game import ra
from unittest import mock
from unittest.mock import patch

from typing import cast, Optional


class RoutesTest(unittest.TestCase):
    def test_get_game_repr(self) -> None:
        random.seed(10)
        self.maxDiff = None
        game = routes.RaGame(player_names=["P1", "P2"], randomize_play_order=True)
        self.assertEqual(
            routes.get_game_repr(game),
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

        User Action: """,
        )

    def test_list_empty(self) -> None:
        self.assertEqual(routes.list([]), routes.ListGamesResponse(total=0, games=[]))

    def test_list_single(self) -> None:
        testId = "12345678123456781234567812345678"
        testGame = routes.RaGame(
            randomize_play_order=False, player_names=["Name1", "Name2"]
        )
        self.assertEqual(
            routes.list([(testId, testGame)]),
            routes.ListGamesResponse(
                total=1,
                games=[
                    routes.GameInfo(
                        id=uuid.UUID("12345678123456781234567812345678"),
                        players=["Name1", "Name2"],
                    )
                ],
            ),
        )

    def test_list_many(self) -> None:
        testIds = [
            "12345678123456781234567812345678",
            "23456781234567812345678123456781",
        ]
        testGames = [
            routes.RaGame(
                randomize_play_order=False, player_names=["Game10", "Game11"]
            ),
            routes.RaGame(
                randomize_play_order=False, player_names=["Game20", "Game21"]
            ),
        ]
        self.assertEqual(
            routes.list(list(zip(testIds, testGames))),
            routes.ListGamesResponse(
                total=2,
                games=[
                    routes.GameInfo(
                        id=uuid.UUID("12345678123456781234567812345678"),
                        players=["Game10", "Game11"],
                    ),
                    routes.GameInfo(
                        id=uuid.UUID("23456781234567812345678123456781"),
                        players=["Game20", "Game21"],
                    ),
                ],
            ),
        )

    def test_start_no_players(self) -> None:
        with self.assertRaises(ValueError):
            routes.start(uuid.uuid4(), [])
        with self.assertRaises(ValueError):
            routes.start(uuid.uuid4(), ["One"])

    def test_start(self) -> None:
        self.maxDiff = None
        gameId = uuid.uuid4()
        with mock.patch("builtins.open", mock.mock_open()) as m:
            game, response = routes.start(gameId, ["Player 1", "Player 2"])
            m.assert_called_once_with(f"move_histories/{gameId}.txt", "w+")

        self.assertEqual(
            response,
            routes.StartResponse(
                gameId=gameId,
                gameState=game.serialize(),
                gameAsStr=routes.get_game_repr(game),
            ),
        )

    def test_message_types(self) -> None:
        self.assertEqual(routes.ErrorMessage("Unused")["level"], "error")
        self.assertEqual(routes.WarningMessage("Unused")["level"], "warning")
        self.assertEqual(routes.InfoMessage("Unused")["level"], "info")
        self.assertEqual(routes.SuccessMessage("Unused")["level"], "success")


class ActionRoutesTest(unittest.IsolatedAsyncioTestCase):
    async def test_action_no_game_id(self) -> None:
        async def fetchGame(gameId: uuid.UUID) -> None:
            return None

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(),
                playerIdx=None,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("gameId", response["message"])

    async def test_action_no_command(self) -> None:
        async def fetchGame(gameId: uuid.UUID) -> None:
            return None

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=uuid.uuid4().hex),
                playerIdx=None,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("action", response["message"])

    async def test_action_failed_fetch(self) -> None:
        async def fetchGame(gameId: uuid.UUID) -> None:
            return None

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=uuid.uuid4().hex, command="draw"),
                playerIdx=None,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("No active game", response["message"])

    async def test_action_unrecognized(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaGame:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="INVALD"),
                playerIdx=0,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("Unrecognized", response["message"])

    async def test_action_game_ended(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()
        game.game_state.set_game_ended()

        async def fetchGame(gameId: uuid.UUID) -> Optional[routes.RaGame]:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            self.assertEqual(gameId, testId)
            return True

        self.assertEqual(
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
            routes.ActionResponse(
                gameState=game.serialize(), gameAsStr=routes.get_game_repr(game)
            ),
        )

    async def test_action_spectator(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaGame:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=None,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("spectator mode", response["message"])

    async def test_action_wrong_player(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaGame:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=1,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("Current player is", response["message"])

    @patch.object(routes.ra, "get_possible_actions")  # pyre-ignore[56]
    async def test_action_no_valid_actions_remain(
        self, mock_action: mock.MagicMock
    ) -> None:
        mock_action.return_value = []
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaGame:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("No valid actions", response["message"])

    async def test_action_illegal_move(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaGame:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="god1"),
                playerIdx=0,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("Only legal actions", response["message"])

    async def test_action_failed_save(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaGame:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            # Fail to save.
            return False

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("Failed to update", response["message"])

    async def test_action_success(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaGame = routes.RaGame(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaGame:
            self.assertEqual(gameId, testId)
            return game

        storage: set[ra.RaGame] = set()

        async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
            self.assertEqual(gameId, testId)
            storage.add(game)
            return True

        response = cast(
            routes.ActionResponse,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )

        self.assertEqual(len(storage), 1)
        savedGame = storage.pop()
        self.assertGreater(len(savedGame.logged_moves), 0)
        firstMove = savedGame.logged_moves[0]
        self.assertTrue(isinstance(firstMove, tuple))
        self.assertEqual(firstMove[0], "0")
        self.assertEqual(
            response,
            routes.ActionResponse(
                gameState=savedGame.serialize(),
                gameAsStr=routes.get_game_repr(savedGame),
            ),
        )
