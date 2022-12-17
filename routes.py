import uuid

from game import info, ra

from typing import Sequence, List, Union, Tuple
from typing_extensions import NotRequired, TypedDict


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


class ActResponse(TypedDict):
    gameAsStr: str
    gameState: ra.SerializedRaGame


class StartResponse(ActResponse):
    gameId: uuid.UUID


class JoinLeaveRequest(TypedDict):
    gameId: NotRequired[str]


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
            GameInfo(
                id=uuid.UUID(gameIdStr),
                players=game.player_names)
            for gameIdStr, game
            in dbGames
        ])


def start(gameId: uuid.UUID,
          players: List[str]
          ) -> Tuple[ra.RaGame, StartResponse]:
    game = ra.RaGame(
        player_names=players,
        outfile=f"{gameId}.txt"
    )
    game.init_game()
    return game, StartResponse(
        gameId=gameId,
        gameState=game.serialize(),
        gameAsStr=get_game_repr(game))


def action(game: ra.RaGame, move: str) -> Union[Message, ActResponse]:
    response = ActResponse(
        gameState=game.serialize(), gameAsStr=get_game_repr(game))
    if move.upper() == "LOAD":
        return response

    parsedMove = ra.parse_action(move)
    if parsedMove < 0:
        return WarningMessage(message='Unrecognized action.')

    if game.game_state.is_game_ended():
        return response
    legal_moves = ra.get_possible_actions(game.game_state)
    if not legal_moves:
        return ErrorMessage(message='Internal Error: No valid actions. ')
    if parsedMove not in legal_moves:
        description = [info.action_description(
            legal_move) for legal_move in legal_moves]
        return InfoMessage(message=f'Only legal actions are: {description}')
    game.execute_action(parsedMove, legal_moves)
    return ActResponse(
        gameState=game.serialize(), gameAsStr=get_game_repr(game))
