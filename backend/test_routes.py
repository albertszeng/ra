import datetime as datetime_lib
import random
import unittest
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, cast
from unittest import mock
from unittest.mock import patch

import jwt

from backend import ai, ai_names, routes
from game import info, ra


class TestVisibility(unittest.TestCase):
    def test_from_str(self) -> None:
        self.assertIsNone(routes.Visibility.from_str(None))
        self.assertIsNone(routes.Visibility.from_str("invalid"))
        self.assertEqual(routes.Visibility.from_str("public"), routes.Visibility.PUBLIC)
        self.assertEqual(
            routes.Visibility.from_str("pRivate"), routes.Visibility.PRIVATE
        )


class TestRaExector(unittest.TestCase):
    def test_initialized(self) -> None:
        game = routes.RaExecutor(num_players=2, randomize_play_order=False)
        self.assertFalse(game.initialized())
        self.assertEqual(game.get_num_players(), 2)
        self.assertEqual(game.get_player_names(), [])

    def test_add_players(self) -> None:
        game = routes.RaExecutor(num_players=2, randomize_play_order=False)
        self.assertEqual(game.maybe_add_player("test1"), 0)
        self.assertEqual(game.maybe_add_player("test1"), 0)
        self.assertEqual(game.maybe_add_player("test1", allowDup=False), None)
        self.assertFalse(game.initialized())
        self.assertEqual(game.get_num_players(), 2)
        self.assertEqual(game.get_player_names(), ["test1"])

        self.assertEqual(game.maybe_add_player("test2"), 1)
        self.assertTrue(game.initialized())
        self.assertEqual(game.get_num_players(), 2)
        self.assertEqual(game.get_player_names(), ["test1", "test2"])

        # Should return existing index
        self.assertEqual(game.maybe_add_player("test1"), 0)
        self.assertEqual(game.maybe_add_player("test2"), 1)

    def test_add_ai_players(self) -> None:
        game = routes.RaExecutor(num_players=3, randomize_play_order=False)

        # Can't have game with all AIs.
        self.assertFalse(game.add_ai_players(levels=[ai.AILevel.EASY] * 3))

        self.assertTrue(game.add_ai_players(levels=[ai.AILevel.EASY]))
        self.assertFalse(game.add_ai_players(levels=[ai.AILevel.EASY] * 2))
        self.assertTrue(game.add_ai_players(levels=[ai.AILevel.EASY]))
        self.assertFalse(game.add_ai_players(levels=[ai.AILevel.EASY]))

        self.assertFalse(game.initialized())
        self.assertEqual(len(game.get_player_names()), 2)

        self.assertEqual(game.maybe_add_player("human"), 2)

        self.assertTrue(game.initialized())
        self.assertIn("human", game.get_player_names())
        self.assertEqual(len(game.get_player_names()), 3)

    def test_add_ai_players_last(self) -> None:
        game = routes.RaExecutor(num_players=3, randomize_play_order=False)

        self.assertEqual(game.maybe_add_player("human"), 0)
        self.assertFalse(game.add_ai_players(levels=[ai.AILevel.EASY] * 3))
        self.assertTrue(game.add_ai_players(levels=[ai.AILevel.EASY] * 2))

        self.assertTrue(game.initialized())
        self.assertIn("human", game.get_player_names())
        self.assertEqual(len(game.get_player_names()), 3)

    def test_execute_next_ai_action(self) -> None:
        game = routes.RaExecutor(num_players=2, randomize_play_order=False)
        self.assertEqual(game.maybe_add_player("human"), 0)
        self.assertTrue(game.add_ai_players(levels=[ai.AILevel.EASY]))

        # Human executes a draw.
        self.assertIsNotNone(game.execute_action(info.DRAW))
        self.assertEqual(len(game.logged_moves), 1)

        # AI Executes action.
        assert (aiInfo := game.execute_next_ai_action()) is not None
        name, action = aiInfo
        self.assertEqual(game.get_player_names(), ["human", name])
        self.assertEqual(len(game.logged_moves), 2)


class RoutesTest(unittest.TestCase):
    def test_single_game(self) -> None:
        self.assertEqual(
            routes.single_game("1234"),
            routes.ListGamesResponse(
                partial=True, games=[routes.GameInfo(id="1234", deleted=True)]
            ),
        )

        game = routes.RaExecutor(num_players=2)
        self.assertEqual(
            routes.single_game("test", game, routes.Visibility.PUBLIC),
            routes.ListGamesResponse(
                partial=True,
                games=[
                    routes.GameInfo(
                        id="test", numPlayers=2, visibility="PUBLIC", players=[]
                    )
                ],
            ),
        )
        self.assertIsNotNone(game.maybe_add_player("test"))
        self.assertEqual(
            routes.single_game("test", game, routes.Visibility.PUBLIC),
            routes.ListGamesResponse(
                partial=True,
                games=[
                    routes.GameInfo(
                        id="test", numPlayers=2, visibility="PUBLIC", players=["test"]
                    )
                ],
            ),
        )

    def test_list_empty(self) -> None:
        self.assertEqual(
            routes.list("user", []), routes.ListGamesResponse(partial=False, games=[])
        )

    def test_incomplete_game(self) -> None:
        testId = uuid.uuid4()
        testGame = routes.RaExecutor(num_players=4)
        testGame.maybe_add_player("testPlayer")
        testVisibility = routes.Visibility.PRIVATE
        self.assertEqual(
            routes.list("testPlayer", [(testId, testGame, testVisibility)]),
            routes.ListGamesResponse(
                partial=False,
                games=[
                    routes.GameInfo(
                        id=str(testId),
                        players=["testPlayer"],
                        visibility=testVisibility.name,
                        numPlayers=4,
                    )
                ],
            ),
        )

    def test_list_single(self) -> None:
        testId = uuid.uuid4()
        testGame = routes.RaExecutor(
            randomize_play_order=False, player_names=["Name1", "Name2"]
        )
        testVisibility = routes.Visibility.PUBLIC
        self.assertEqual(
            routes.list("user", [(testId, testGame, testVisibility)]),
            routes.ListGamesResponse(
                partial=False,
                games=[
                    routes.GameInfo(
                        id=str(testId),
                        players=["Name1", "Name2"],
                        visibility=testVisibility.name,
                        numPlayers=2,
                    )
                ],
            ),
        )

    def test_list_many_public(self) -> None:
        testIds = [
            uuid.uuid4(),
            uuid.uuid4(),
        ]
        testGames = [
            routes.RaExecutor(
                randomize_play_order=False, player_names=["Game10", "Game11"]
            ),
            routes.RaExecutor(
                randomize_play_order=False, player_names=["Game20", "Game21"]
            ),
        ]
        testVisibilites = [routes.Visibility.PUBLIC, routes.Visibility.PUBLIC]
        self.assertEqual(
            routes.list("user", list(zip(testIds, testGames, testVisibilites))),
            routes.ListGamesResponse(
                partial=False,
                games=[
                    routes.GameInfo(
                        id=str(testIds[0]),
                        players=["Game10", "Game11"],
                        visibility=routes.Visibility.PUBLIC.name,
                        numPlayers=2,
                    ),
                    routes.GameInfo(
                        id=str(testIds[1]),
                        players=["Game20", "Game21"],
                        visibility=routes.Visibility.PUBLIC.name,
                        numPlayers=2,
                    ),
                ],
            ),
        )

    def test_list_many_mixed(self) -> None:
        testIds = [
            uuid.uuid4(),
            uuid.uuid4(),
        ]
        testGames = [
            routes.RaExecutor(
                randomize_play_order=False, player_names=["Game10", "Game11"]
            ),
            routes.RaExecutor(
                randomize_play_order=False, player_names=["Game20", "Game21"]
            ),
        ]
        testVisibilites = [routes.Visibility.PUBLIC, routes.Visibility.PRIVATE]
        self.assertEqual(
            routes.list("Game20", list(zip(testIds, testGames, testVisibilites))),
            routes.ListGamesResponse(
                partial=False,
                games=[
                    routes.GameInfo(
                        id=str(testIds[0]),
                        players=["Game10", "Game11"],
                        visibility=routes.Visibility.PUBLIC.name,
                        numPlayers=2,
                    ),
                    routes.GameInfo(
                        id=str(testIds[1]),
                        players=["Game20", "Game21"],
                        visibility=routes.Visibility.PRIVATE.name,
                        numPlayers=2,
                    ),
                ],
            ),
        )

        self.assertEqual(
            routes.list("Game10", list(zip(testIds, testGames, testVisibilites))),
            routes.ListGamesResponse(
                partial=False,
                games=[
                    routes.GameInfo(
                        id=str(testIds[0]),
                        players=["Game10", "Game11"],
                        visibility=routes.Visibility.PUBLIC.name,
                        numPlayers=2,
                    ),
                ],
            ),
        )

    def test_message_types(self) -> None:
        self.assertEqual(routes.ErrorMessage("Unused")["level"], "error")
        self.assertEqual(routes.WarningMessage("Unused")["level"], "warning")
        self.assertEqual(routes.InfoMessage("Unused")["level"], "info")
        self.assertEqual(routes.SuccessMessage("Unused")["level"], "success")

    def test_gen_exp(self) -> None:
        self.assertIsNotNone(routes.gen_exp())

    def test_authenticate_invalid_or_expired_token(self) -> None:
        self.assertIsNone(routes.authenticate_token(None, "secret"))

        invalidToken = jwt.encode(
            {"username": "user", "_exp": 100}, "bad", algorithm="HS256"
        )
        self.assertIsNone(routes.authenticate_token(invalidToken, "secret"))

        expiredToken = jwt.encode(
            {
                "username": "user",
                # Experied 1-hour ago.
                "exp": (datetime.utcnow() - datetime_lib.timedelta(days=1)).timestamp(),
            },
            "secret",
            algorithm="HS256",
        )
        self.assertIsNone(routes.authenticate_token(expiredToken, "secret"))

    def test_authenticate_and_refresh_valid_token(self) -> None:
        validToken = jwt.encode(
            {
                "username": "user",
                # Will expire in 1-hour from now.
                "_exp": (
                    datetime.utcnow() + datetime_lib.timedelta(hours=1)
                ).timestamp(),
            },
            "secret",
            algorithm="HS256",
        )
        response = routes.authenticate_token(validToken, "secret")
        assert response is not None
        token = response.get("token")
        self.assertIsNotNone(token)
        self.assertNotEqual(token, validToken)
        # Decode response and validate it's been refreshed correctly.
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        self.assertEqual(payload.get("username"), "user")
        self.assertGreater(
            payload.get("exp"),
            (datetime.utcnow() + datetime_lib.timedelta(hours=1)).timestamp(),
        )


class DeleteRouteTest(unittest.IsolatedAsyncioTestCase):
    async def test_delete_invalid(self) -> None:
        async def fetchGame(gameId: uuid.UUID) -> Optional[routes.RaExecutor]:
            return routes.RaExecutor(player_names=["test1", "test2"])

        async def persistDelete(gameId: uuid.UUID) -> bool:
            return True

        async def failFetch(gameId: uuid.UUID) -> Optional[routes.RaExecutor]:
            return None

        async def failPersist(gameId: uuid.UUID) -> bool:
            return False

        validGameId = str(uuid.uuid4())
        msg, _ = await routes.delete("invalid", "test1", fetchGame, persistDelete)
        self.assertEqual(msg["level"], "error")

        msg, _ = await routes.delete(
            validGameId, "test1", fetchGame=failFetch, persistDelete=persistDelete
        )
        self.assertEqual(msg["level"], "warning")

        msg, _ = await routes.delete(validGameId, "invalid", fetchGame, persistDelete)
        self.assertEqual(msg["level"], "warning")

        msg, _ = await routes.delete(
            validGameId, "test1", fetchGame, persistDelete=failPersist
        )
        self.assertEqual(msg["level"], "warning")

    async def test_delete(self) -> None:
        storage: dict[str, routes.RaExecutor] = {}

        async def fetchGame(gameId: uuid.UUID) -> Optional[routes.RaExecutor]:
            storage[str(gameId)] = routes.RaExecutor(player_names=["test1", "test2"])
            return storage[str(gameId)]

        async def persistDelete(gameId: uuid.UUID) -> bool:
            del storage[str(gameId)]
            return True

        gameId = uuid.uuid4()
        msg, lst = await routes.delete(str(gameId), "test1", fetchGame, persistDelete)
        self.assertEqual(msg["level"], "success")
        self.assertEqual(storage, {})
        self.assertEqual(
            lst,
            routes.ListGamesResponse(
                partial=True, games=[routes.GameInfo(id=str(gameId), deleted=True)]
            ),
        )


class StartRoutesTest(unittest.IsolatedAsyncioTestCase):
    async def test_start_wrong_players(self) -> None:
        async def commitGame(
            gameId: uuid.UUID, game: routes.RaExecutor, visibility: routes.Visibility
        ) -> None:
            return

        # Too few human.
        msg, _ = await routes.start(
            routes.StartRequest(numPlayers=0),
            username="user",
            commitGame=commitGame,
        )
        self.assertEqual(msg["level"], "warning")

        # Too few human.
        msg, _ = await routes.start(
            routes.StartRequest(numPlayers=1),
            username="user",
            commitGame=commitGame,
        )
        self.assertEqual(msg["level"], "warning")

        # Too many all human.
        msg, _ = await routes.start(
            routes.StartRequest(numPlayers=6),
            username="user",
            commitGame=commitGame,
        )
        self.assertEqual(msg["level"], "warning")

        # Too few mixed.
        msg, _ = await routes.start(
            routes.StartRequest(numPlayers=0, numAIPlayers=1),
            username="user",
            commitGame=commitGame,
        )
        self.assertEqual(msg["level"], "warning")

        # Can't have all AIs.
        msg, _ = await routes.start(
            routes.StartRequest(numPlayers=0, numAIPlayers=2),
            username="user",
            commitGame=commitGame,
        )
        self.assertEqual(msg["level"], "warning")

        # Too many mixed.
        msg, _ = await routes.start(
            routes.StartRequest(numPlayers=1, numAIPlayers=5),
            username="user",
            commitGame=commitGame,
        )
        self.assertEqual(msg["level"], "warning")

    # AI will be named AI Panda.
    @patch.object(ai_names, "ALL", new=["panda"])
    async def test_start(self) -> None:
        self.maxDiff = None
        # Required to maintain shuffle order of players.
        random.seed(42)

        storage: Dict[str, Any] = {}

        async def commitGame(
            gameId: uuid.UUID, game: routes.RaExecutor, visibility: routes.Visibility
        ) -> None:
            storage["gameId"] = gameId
            storage["game"] = game
            storage["visibility"] = visibility

        msg, lst = await routes.start(
            routes.StartRequest(
                numPlayers=2,
                visibility="PRIVATE",
                numAIPlayers=1,
                AILevel="MEDIUM",
            ),
            username="user",
            commitGame=commitGame,
        )
        storedGameId, storedGame, storedVisibility = (
            storage.get("gameId"),
            storage.get("game"),
            storage.get("visibility"),
        )
        self.assertIsNotNone(storedGameId)
        self.assertIsNotNone(storedGame)
        self.assertEqual(storedVisibility, routes.Visibility.PRIVATE)
        self.assertEqual(msg["level"], "success")
        self.assertEqual(
            lst,
            routes.ListGamesResponse(
                partial=True,
                games=[
                    routes.GameInfo(
                        id=str(storedGameId),
                        players=["user", "AI Panda"],
                        visibility=routes.Visibility.PRIVATE.name,
                        numPlayers=3,
                    )
                ],
            ),
        )


class ActionRoutesTest(unittest.IsolatedAsyncioTestCase):
    async def test_action_no_game_id(self) -> None:
        async def fetchGame(gameId: uuid.UUID) -> None:
            return None

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(),
                playerIdx=None,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("gameId", response["message"])

    async def test_action_no_command(self) -> None:
        async def fetchGame(gameId: uuid.UUID) -> None:
            return None

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=uuid.uuid4().hex),
                playerIdx=None,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("action", response["message"])

    async def test_action_failed_fetch(self) -> None:
        async def fetchGame(gameId: uuid.UUID) -> None:
            return None

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=uuid.uuid4().hex, command="draw"),
                playerIdx=None,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("No active game", response["message"])

    async def test_action_unrecognized(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaExecutor:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="INVALD"),
                playerIdx=0,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("Unrecognized", response["message"])

    async def test_action_game_ended(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()
        game.game_state.set_game_ended()

        async def fetchGame(gameId: uuid.UUID) -> Optional[routes.RaExecutor]:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            self.assertEqual(gameId, testId)
            return True

        self.assertEqual(
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
            [
                routes.ActionResponse(
                    gameState=game.serialize(),
                    username="user",
                    action="Load finished game.",
                )
            ],
        )

    async def test_action_spectator(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaExecutor:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=None,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("spectator mode", response["message"])

    async def test_action_wrong_player(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaExecutor:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=1,
                username="user",
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
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaExecutor:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("No valid actions", response["message"])

    async def test_action_illegal_move(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaExecutor:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            return True

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="god1"),
                playerIdx=0,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("Only legal actions", response["message"])

    async def test_action_failed_save(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaExecutor:
            self.assertEqual(gameId, testId)
            return game

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            # Fail to save.
            return False

        response = cast(
            routes.Message,
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                username="user",
                fetchGame=fetchGame,
                saveGame=saveGame,
            ),
        )
        self.assertIn("message", response)
        self.assertIn("Failed to update", response["message"])

    async def test_action_success(self) -> None:
        testId: uuid.UUID = uuid.uuid4()
        game: routes.RaExecutor = routes.RaExecutor(
            player_names=["Player 1", "Player 2"],
        )
        game.init_game()

        async def fetchGame(gameId: uuid.UUID) -> routes.RaExecutor:
            self.assertEqual(gameId, testId)
            return game

        storage: set[ra.RaGame] = set()

        async def saveGame(gameId: uuid.UUID, game: routes.RaExecutor) -> bool:
            self.assertEqual(gameId, testId)
            storage.add(game)
            return True

        response = cast(
            List[routes.ActionResponse],
            await routes.action(
                routes.ActionRequest(gameId=testId.hex, command="draw"),
                playerIdx=0,
                username="user",
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
            [
                routes.ActionResponse(
                    gameState=savedGame.serialize(),
                    username="user",
                    action=info.DRAW_DESC,
                )
            ],
        )
