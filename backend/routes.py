import datetime as datetime_lib
import uuid
from datetime import datetime
from typing import Awaitable, Callable, Dict, List, Optional, Sequence, Tuple, Union

import jwt
from sqlalchemy.ext import mutable
from typing_extensions import NotRequired, TypedDict

from game import info, ra


class RaGame(mutable.Mutable, ra.RaGame):
    """Required so database can update on changes to state."""

    def __getstate__(self) -> Dict[str, str]:
        d = self.__dict__.copy()
        d.pop("_parents", None)
        return d


class Message(TypedDict):
    level: str
    message: str


def ErrorMessage(message: str) -> Message:
    return Message(level="error", message=message)


def WarningMessage(message: str) -> Message:
    return Message(level="warning", message=message)


def InfoMessage(message: str) -> Message:
    return Message(level="info", message=message)


def SuccessMessage(message: str) -> Message:
    return Message(level="success", message=message)


class ActionResponse(TypedDict):
    gameAsStr: str
    gameState: ra.SerializedRaGame


class LoginOrRegisterRequest(TypedDict):
    username: NotRequired[str]
    password: NotRequired[str]
    # The user can provide a token to restore a previous login.
    token: NotRequired[str]


class LoginResponse(Message):
    # We return a token on successful login/registration so the client
    # can cache it.
    token: str
    username: str


class StartResponse(ActionResponse):
    gameId: uuid.UUID


class JoinLeaveRequest(TypedDict):
    gameId: NotRequired[str]
    name: NotRequired[str]


class ActionRequest(TypedDict):
    gameId: NotRequired[str]
    command: NotRequired[str]


class GameInfo(TypedDict):
    id: uuid.UUID
    players: List[str]


class ListGamesResponse(TypedDict):
    total: int
    games: List[GameInfo]


def get_game_repr(game: ra.RaGame) -> str:
    legal_actions = ra.get_possible_actions(game.game_state)
    val = str(game.game_state)
    if not legal_actions:
        return val
    prompt = game.get_action_prompt(legal_actions)
    return f"{val}\n\n{prompt}"


def list(dbGames: Sequence[Tuple[str, ra.RaGame]]) -> ListGamesResponse:
    """Generates a response from all available games in the database."""
    return ListGamesResponse(
        total=len(dbGames),
        games=[
            GameInfo(id=uuid.UUID(gameIdStr), players=game.player_names)
            for gameIdStr, game in dbGames
        ],
    )


def start(gameId: uuid.UUID, players: List[str]) -> Tuple[ra.RaGame, StartResponse]:
    game = RaGame(player_names=players, outfile=f"{gameId}.txt")
    game.init_game()
    return game, StartResponse(
        gameId=gameId, gameState=game.serialize(), gameAsStr=get_game_repr(game)
    )


async def action(
    request: ActionRequest,
    playerIdx: Optional[int],
    fetchGame: Callable[[uuid.UUID], Awaitable[Optional[RaGame]]],
    saveGame: Callable[[uuid.UUID, RaGame], Awaitable[bool]],
) -> Union[Message, ActionResponse]:
    """Performs the action as specified by the request.

    Args:
        request: The request information required to validate and make the action.
        playerIdx: The index of the player trying to make the action.
        fetchGame: A funcion that generates a game for the provided game UUID.
        saveGame: A function that given a game, persist it in storage under the
            provided UUID.

    Returns:
        The reponse to return to the client as well as boolean indicating if
        the requested action was successful.
    """
    if not (gameIdStr := request.get("gameId")):
        return ErrorMessage(message="Must provide a gameId with request.")

    gameId = uuid.UUID(gameIdStr)
    action = request.get("command")
    if not action:
        return ErrorMessage(message=f"Must provide action to act on game: {gameIdStr}")

    if not (game := await fetchGame(gameId)):
        return WarningMessage(message=f"No active game with id: {gameId}")

    parsedAction = ra.parse_action(action)

    if parsedAction < 0:
        return WarningMessage(message="Unrecognized action.")

    if game.game_state.is_game_ended():
        return ActionResponse(gameState=game.serialize(), gameAsStr=get_game_repr(game))
    currIdx = game.game_state.current_player

    if playerIdx is None:
        return InfoMessage(message="Currently in spectator mode. Join an open game.")
    if playerIdx != currIdx:
        return WarningMessage(
            message=f"{game.player_names[playerIdx]} cannot make action. \
            Current player is: {game.player_names[currIdx]}"
        )
    legal_actions = ra.get_possible_actions(game.game_state)

    if not legal_actions:
        return ErrorMessage(message="Internal Error: No valid actions.")

    if parsedAction not in legal_actions:
        description = [
            info.action_description(legal_action) for legal_action in legal_actions
        ]
        return InfoMessage(message=f"Only legal actions are: {description}")
    game.execute_action(parsedAction, legal_actions)

    if not (await saveGame(gameId, game)):
        return ErrorMessage(f"Failed to update game: {gameId}. Repeat action.")

    return ActionResponse(gameState=game.serialize(), gameAsStr=get_game_repr(game))


def gen_exp() -> float:
    return (datetime.utcnow() + datetime_lib.timedelta(days=2)).timestamp()


def authenticate_token(token: Optional[str], secret: str) -> Optional[LoginResponse]:
    """Authenticates the provided token. On success, returns a LongReponse"""
    if not token:
        return
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except:  # noqa: E722
        # Invalid or expired token.
        return

    # Token is valid - refresh deadline, and send along.
    username = payload.get("username")
    refreshedToken = jwt.encode(
        {
            "username": username,
            "exp": gen_exp(),
        },
        secret,
        algorithm="HS256",
    )
    return LoginResponse(
        token=refreshedToken,
        username=username,
        level="success",
        message=f"{username} successfully logged in.",
    )
