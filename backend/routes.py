import copy
import dataclasses
import datetime as datetime_lib
import enum
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

from backend import ai
from game import info, ra


@enum.unique
class Visibility(enum.Enum):
    PUBLIC = 1
    PRIVATE = 2

    @staticmethod
    def from_str(label: Optional[str]) -> Optional["Visibility"]:
        """Creates from the given label if possible."""
        if not label:
            return None
        label = label.upper()
        if label in ("PUBLIC", "PRIVATE"):
            return Visibility[label]
        return None


@dataclasses.dataclass(frozen=True)
class PlayerInfo:
    name: str
    # When set, this player is not a human player but rather an AI.
    quality: Optional[ai.AILevel] = None


class RaExecutor(ra.RaGame, mutable.Mutable):
    """Required so database can update on changes to state."""

    def __init__(self, num_players: Optional[int] = None, **kwargs: Any) -> None:
        self._kwargs: Dict[str, Any] = kwargs
        self._player_names: List[str] = kwargs.get("player_names", [])
        self._players: List[PlayerInfo] = [
            PlayerInfo(name=name) for name in self._player_names
        ]
        self._num_players: int = (
            num_players if num_players is not None else len(self._players)
        )
        self._initialized: bool = False
        if len(self._players) == self._num_players:
            self._init_game()

    def _init_game(self) -> None:
        """Actually initializes the RaGame if all players have joined."""
        if len(self._players) != self._num_players:
            raise ValueError("Should never call init w/o the right number of players")

        self._player_names = [player.name for player in self._players]
        self._kwargs["player_names"] = self._player_names
        super().__init__(**self._kwargs)
        super().init_game()

        # Init above might shuffle player names. Update self._players to match.
        nameToPlayer = {player.name: player for player in self._players}
        self._players = [nameToPlayer[name] for name in self.player_names]

        # Check if we need to execute some AI actions, and if so, do so.
        while self._execute_next_ai_action() is not None:
            pass

        self._initialized = True

    def _execute_next_ai_action(self) -> Optional[Tuple[str, int]]:
        # Assumes we're initialized.
        if self.game_state.is_game_ended():
            return None
        if not (level := self._players[self.game_state.current_player].quality):
            # Not an AI.
            return None
        name = self.player_names[self.game_state.current_player]
        action = ai.get()[level](self.game_state)
        self.execute_action(action)
        return name, action

    def add_ai_players(self, levels: List[ai.AILevel]) -> bool:
        """Adds AI players of the specified levels to the game.

        Note that we can never have a game that is all AIs.

        Returns if successful in adding all.
        """
        if self.initialized():
            return False
        toAdd = len(levels)
        currAIs = len([player for player in self._players if player.quality])
        if currAIs + toAdd == self._num_players:
            # Can't have a game with all AIs.
            return False
        if len(self._players) + toAdd > self._num_players:
            # Can't add these name AIs to this game.
            return False

        for level in levels:
            name = ai.generate_name([player.name for player in self._players])
            self._players.append(PlayerInfo(name=name, quality=level))
        if len(self._players) == self._num_players:
            # Automatically initialize if
            self._init_game()
        return True

    def execute_next_ai_action(self) -> Optional[Tuple[str, int]]:
        """Executes the next AI action, if available. Returns the action executed."""
        if not self.initialized():
            return None
        return self._execute_next_ai_action()

    def maybe_add_player(self, username: str, allowDup: bool = True) -> Optional[int]:
        """Maybe adds a human player to the game.

        Args:
            username - The name of the human player, should be unique.
            allowDup - If True and username is already in game, returns the index of the
                user.

        Returns:
            The index of the human player with the given username.
        """
        humanPlayer = PlayerInfo(name=username)
        if humanPlayer in self._players:
            return self._players.index(humanPlayer) if allowDup else None

        if self.initialized():
            return None

        self._players.append(humanPlayer)
        if len(self._players) == self._num_players:
            # Automatically initialize if we've hit max players.
            self._init_game()
        return len(self._players) - 1

    def initialized(self) -> bool:
        """Returns true if the game has been initialized."""
        return self._initialized

    def get_num_players(self) -> int:
        """Returns the max number of players in this game."""
        return self._num_players

    def get_player_names(self) -> List[str]:
        """Returns the names of the currently joined players."""
        return [player.name for player in self._players]

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


class ActionRequest(TypedDict):
    gameId: NotRequired[str]
    command: NotRequired[str]


class ActionResponse(TypedDict):
    gameState: ra.SerializedRaGame
    action: str
    username: str


class RegisterRequest(TypedDict):
    username: NotRequired[str]
    password: NotRequired[str]


class LoginRequest(RegisterRequest):
    # The user can provide a token to restore a previous login.
    token: NotRequired[str]


class LoginResponse(Message):
    # We return a token on successful login/registration so the client
    # can cache it.
    token: str
    username: str


class StartRequest(TypedDict):
    numPlayers: NotRequired[int]
    numAIPlayers: NotRequired[int]
    AILevel: NotRequired[str]
    visibility: NotRequired[str]


class StartResponse(ActionResponse):
    gameId: str


class JoinLeaveRequest(TypedDict):
    gameId: NotRequired[str]


class JoinSessionSuccess(TypedDict):
    gameId: str
    playerName: str
    playerIdx: NotRequired[int]


class DeleteRequest(TypedDict):
    gameId: NotRequired[str]


class AddPlayerRequest(TypedDict):
    gameId: Optional[str]


class GameInfo(TypedDict):
    # Unique identifier for this game.
    id: str
    # Usernames of the players that have joined.
    players: NotRequired[List[str]]
    # Game visibility. Private games are only sent to members of the game.
    visibility: NotRequired[str]
    # How many total players this game hosts.
    numPlayers: NotRequired[int]
    # When specified, means this game was deleted.
    deleted: NotRequired[bool]


class ListGamesResponse(TypedDict):
    # When set to true, this response should be treated as a partial
    # update on whatever data is available to the local client.
    partial: bool
    games: List[GameInfo]


def single_game(
    gameId: str,
    game: Optional[RaExecutor] = None,
    visibility: Optional[Visibility] = None,
) -> ListGamesResponse:
    """Creates a partial ListGamesResponse with a single game.

    When either game or visibility is missing, this is assumed to be a deletion.
    """
    if game and visibility:
        return ListGamesResponse(
            partial=True,
            games=[
                GameInfo(
                    id=gameId,
                    players=game.get_player_names(),
                    visibility=visibility.name,
                    numPlayers=game.get_num_players(),
                )
            ],
        )
    return ListGamesResponse(partial=True, games=[GameInfo(id=gameId, deleted=True)])


def list(
    username: str, dbGames: Sequence[Tuple[uuid.UUID, RaExecutor, Visibility]]
) -> ListGamesResponse:
    """Generates a response from all available games in the database."""
    return ListGamesResponse(
        partial=False,
        games=[
            GameInfo(
                id=str(gameId),
                players=game.get_player_names(),
                visibility=visibility.name,
                numPlayers=game.get_num_players(),
            )
            for gameId, game, visibility in dbGames
            if visibility == Visibility.PUBLIC or username in game.get_player_names()
        ],
    )


async def start(
    request: StartRequest,
    username: str,
    commitGame: Callable[[uuid.UUID, RaExecutor, Visibility], Awaitable[None]],
) -> Tuple[Message, Optional[ListGamesResponse]]:
    """Starts a RaGame.

    Args:
        request: The start request with information requires to initialize.
        commitGame: Callback to commit the game to persistent storage.

    Returns:
        Response to client.
    """
    # Reasonable default is 0.
    numAIPlayers = request.get("numAIPlayers", 0)
    # Reasonable default is EASY.
    aiLevel = ai.AILevel.from_str(request.get("AILevel")) or ai.AILevel.EASY
    if (
        not (numPlayers := request.get("numPlayers"))
        or numPlayers + numAIPlayers < info.MIN_NUM_PLAYERS
        or numPlayers + numAIPlayers > info.MAX_NUM_PLAYERS
        # Cannot start a game with only AIs.
        or numPlayers == 0
    ):
        return (
            WarningMessage(
                f"Cannot start a game with {numPlayers} humans and {numAIPlayers} AIs."
            ),
            None,
        )

    gameId = uuid.uuid4()
    game = RaExecutor(num_players=numPlayers + numAIPlayers)
    if game.maybe_add_player(username) is None:
        return ErrorMessage("Failed to start game. Internal error."), None
    if not game.add_ai_players(levels=[aiLevel for _ in range(numAIPlayers)]):
        return ErrorMessage("Failed to start game. Internal error."), None
    visibility = Visibility.from_str(request.get("visibility")) or Visibility.PUBLIC
    await commitGame(gameId, game, visibility)
    return SuccessMessage(f"{username} created game: {gameId}."), single_game(
        str(gameId), game, visibility
    )


async def add_player(
    username: str,
    gameIdStr: Optional[str],
    fetchGame: Callable[
        [uuid.UUID], Awaitable[Optional[Tuple[RaExecutor, Visibility]]]
    ],
    saveGame: Callable[[uuid.UUID, RaExecutor], Awaitable[bool]],
) -> Tuple[Message, Optional[ListGamesResponse]]:
    """Attempts to add a player to the indicated game."""
    if not gameIdStr:
        return WarningMessage("Must provide gameId to join game."), None
    try:
        gameId = uuid.UUID(gameIdStr)
    except ValueError as e:
        return WarningMessage(f"Unparseable gameId: {e}"), None
    if not (gameInfo := await fetchGame(gameId)):
        return (
            WarningMessage(f"Cannot add player to non-existant game: {gameId}."),
            None,
        )
    game, visibility = gameInfo
    if game.maybe_add_player(username, allowDup=False) is None:
        return (
            WarningMessage(f"{username} cannot be added to {gameId}."),
            None,
        )
    if not await saveGame(gameId, game):
        return (
            ErrorMessage(f"{username} failed to add {username} to game: {gameId}."),
            None,
        )

    return SuccessMessage(f"{username} added to game: {gameId}"), single_game(
        gameIdStr, game, visibility
    )


async def join_game(
    username: str,
    request: JoinLeaveRequest,
    fetchGame: Callable[[uuid.UUID], Awaitable[Optional[RaExecutor]]],
    saveGame: Callable[[uuid.UUID, RaExecutor], Awaitable[bool]],
) -> Union[JoinSessionSuccess, Message]:
    """Attempts to add the user to the requested game."""
    if not (gameIdStr := request.get("gameId")):
        return WarningMessage("Must provide gameId to join game.")
    try:
        gameId = uuid.UUID(gameIdStr)
    except ValueError as e:
        return ErrorMessage(f"Unparseable gameId: {e}")
    if not (game := await fetchGame(gameId)):
        return WarningMessage(f"Cannot join non-existant game: {gameId}.")
    if (playerIdx := game.maybe_add_player(username)) is None:
        # Join as spectator.
        return JoinSessionSuccess(gameId=gameIdStr, playerName=username)
    if not await saveGame(gameId, game):
        return ErrorMessage(f"{username} failed to join gameId: {gameId}.")
    return JoinSessionSuccess(
        gameId=gameIdStr, playerName=username, playerIdx=playerIdx
    )


async def delete(
    gameIdStr: str,
    username: str,
    fetchGame: Callable[[uuid.UUID], Awaitable[Optional[RaExecutor]]],
    persistDelete: Callable[[uuid.UUID], Awaitable[bool]],
) -> Tuple[Message, Optional[ListGamesResponse]]:
    try:
        gameId = uuid.UUID(gameIdStr)
    except ValueError as err:
        return ErrorMessage(message=str(err)), None
    if not (game := await fetchGame(gameId)):
        return WarningMessage(message=f"No game with id {gameId} found."), None
    if username not in game.get_player_names():
        return (
            WarningMessage(
                message=f"Cannot delete game: {gameId} since \
                {username} is not a player."
            ),
            None,
        )
    if not await persistDelete(gameId):
        return WarningMessage(message=f"No game with id {gameId} found."), None
    return SuccessMessage(message=f"Deleted game: {gameId}"), single_game(str(gameId))


# flake8: noqa: C901
async def action(
    request: ActionRequest,
    playerIdx: Optional[int],
    username: str,
    fetchGame: Callable[[uuid.UUID], Awaitable[Optional[RaExecutor]]],
    saveGame: Callable[[uuid.UUID, RaExecutor], Awaitable[bool]],
) -> Union[Message, List[ActionResponse]]:
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
        return ErrorMessage(message=f"Must provide action to act on game: {gameIdStr}.")

    if not (game := await fetchGame(gameId)):
        return WarningMessage(message=f"No active game with id: {gameId}.")
    if not game.initialized():
        return WarningMessage(
            message=f"Cannot take action on un-initialized games: {gameId}."
        )

    if game.game_state.is_game_ended():
        return [
            ActionResponse(
                gameState=game.serialize(),
                action="Load finished game.",
                username=username,
            )
        ]

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
    responses = [
        ActionResponse(
            gameState=copy.deepcopy(game.serialize()),
            username=username,
            action=info.action_description(parsedAction),
        )
    ]
    while (aiInfo := game.execute_next_ai_action()) is not None:
        name, action = aiInfo
        responses.append(
            ActionResponse(
                gameState=copy.deepcopy(game.serialize()),
                username=name,
                action=info.action_description(action),
            )
        )

    if not (await saveGame(gameId, game)):
        return ErrorMessage(f"Failed to update game: {gameId}. Repeat action.")

    return responses


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
