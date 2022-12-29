import datetime as datetime_lib
import uuid
from datetime import datetime
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import jwt
from sqlalchemy.ext import mutable
from typing_extensions import NotRequired, TypedDict

from game import info, ra


class RaGame(ra.RaGame, mutable.Mutable):
    """Required so database can update on changes to state."""

    def __init__(self, num_players: Optional[int] = None, **kwargs: Any) -> None:
        self._kwargs: Dict[str, Any] = kwargs
        self._player_names: List[str] = kwargs.get("player_names", [])
        self._num_players: int = (
            num_players if num_players is not None else len(self._player_names)
        )
        self._initialized: bool = False
        self._init_game()

    def _init_game(self) -> bool:
        """Actually initializes the RaGame if all players have joined."""
        if len(self._player_names) != self._num_players:
            return False

        self._kwargs["player_names"] = self._player_names
        super().__init__(**self._kwargs)
        super().init_game()
        self._initialized = True
        return True

    def add_player(self, username: str) -> bool:
        if self.is_active():
            return False

        if username in self._player_names:
            return False
        self._player_names.append(username)
        if len(self._player_names) == self._num_players:
            return self._init_game()
        return True

    def is_active(self) -> bool:
        """Returns true if the game is active and ongoing."""
        return self._initialized

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
    action: str
    username: str


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


class StartRequest(TypedDict):
    numPlayers: NotRequired[int]
    # TODO: Remove. This is for backwards compatibility.
    playerNames: NotRequired[List[str]]


class StartResponse(ActionResponse):
    gameId: str


class JoinLeaveRequest(TypedDict):
    gameId: NotRequired[str]


class JoinSessionSuccess(TypedDict):
    gameId: str
    playerName: str
    playerIdx: NotRequired[int]


class ActionRequest(TypedDict):
    gameId: NotRequired[str]
    command: NotRequired[str]


class DeleteRequest(TypedDict):
    gameId: NotRequired[str]


class GameInfo(TypedDict):
    id: str
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


def list(dbGames: Sequence[Tuple[uuid.UUID, ra.RaGame]]) -> ListGamesResponse:
    """Generates a response from all available games in the database."""
    return ListGamesResponse(
        total=len(dbGames),
        games=[
            GameInfo(id=str(gameId), players=game.player_names)
            for gameId, game in dbGames
        ],
    )


async def start(
    request: StartRequest,
    username: str,
    commitGame: Callable[[uuid.UUID, RaGame], Awaitable[None]],
) -> StartResponse:
    """Starts a RaGame.

    Args:
        request: The start request with information requires to initialize.
        commitGame: Callback to commit the game to persistent storage.

    Returns:
        Response to client.
    """
    gameId = uuid.uuid4()
    game = RaGame(player_names=request.get("playerNames", []))
    await commitGame(gameId, game)
    return StartResponse(
        gameId=str(gameId),
        gameState=game.serialize(),
        gameAsStr=get_game_repr(game),
        username=username,
        action="Start game.",
    )


async def join(
    username: str,
    request: JoinLeaveRequest,
    fetchGame: Callable[[uuid.UUID], Awaitable[Optional[RaGame]]],
    saveGame: Callable[[uuid.UUID, RaGame], Awaitable[bool]],
) -> Union[JoinSessionSuccess, Message]:
    """"""
    if not (gameIdStr := request.get("gameId")):
        return WarningMessage("Must provide gameId to join game.")
    try:
        gameId = uuid.UUID(gameIdStr)
    except ValueError as e:
        return ErrorMessage(f"Unparseable gameId: {e}")
    if not (game := await fetchGame(gameId)):
        return WarningMessage(f"Cannot join non-existant game: {gameId}.")
    idxs = [
        i
        for i, (occupied, player) in enumerate(
            zip(game.player_in_game, game.player_names)
        )
        if not occupied and player.lower() == username.lower()
    ]
    if not idxs:
        return JoinSessionSuccess(gameId=gameIdStr, playerName=username)

    # Take first available index. Must be unique because usernames are unique.
    playerIdx = idxs[0]
    game.player_in_game[playerIdx] = True
    if not await saveGame(gameId, game):
        return ErrorMessage(f"{username} failed to join gameId: {gameId}.")
    return JoinSessionSuccess(
        gameId=gameIdStr, playerName=username, playerIdx=playerIdx
    )


async def delete(
    gameIdStr: str,
    username: str,
    fetchGame: Callable[[uuid.UUID], Awaitable[Optional[RaGame]]],
    persistDelete: Callable[[uuid.UUID], Awaitable[bool]],
) -> Message:
    try:
        gameId = uuid.UUID(gameIdStr)
    except ValueError as err:
        return ErrorMessage(message=str(err))
    if not (game := await fetchGame(gameId)):
        return WarningMessage(message=f"No game with id {gameId} found.")
    if username not in game.player_names:
        return WarningMessage(
            message=f"Cannot delete game: {gameId} since {username} is not a player."
        )
    if not await persistDelete(gameId):
        return WarningMessage(message=f"No game with id {gameId} found.")
    return SuccessMessage(message=f"Deleted game: {gameId}")


async def action(
    request: ActionRequest,
    playerIdx: Optional[int],
    username: str,
    fetchGame: Callable[[uuid.UUID], Awaitable[Optional[RaGame]]],
    saveGame: Callable[[uuid.UUID, RaGame], Awaitable[bool]],
) -> Union[Message, ActionResponse]:
    """Performs the action as specified by the request.

    Args:
        request: The request information required to validate and make the action.
        playerIdx: The index of the player trying to make the action.
        username: The name of the user attempting to take the action.
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

    if game.game_state.is_game_ended():
        return ActionResponse(
            gameState=game.serialize(),
            gameAsStr=get_game_repr(game),
            action="Load finished game.",
            username=username,
        )

    parsedAction = ra.parse_action(action)
    if parsedAction < 0:
        return WarningMessage(message="Unrecognized action.")

    if playerIdx is None:
        return InfoMessage(message="Currently in spectator mode. Join an open game.")

    currIdx = game.game_state.current_player
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

    return ActionResponse(
        gameState=game.serialize(),
        gameAsStr=get_game_repr(game),
        username=username,
        action=info.action_description(parsedAction),
    )


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
