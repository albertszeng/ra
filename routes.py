import uuid

from game import ra

from typing import Sequence, List, Union, Tuple
from typing_extensions import NotRequired, TypedDict


class Message(TypedDict):
    message: str


class ActResponse(TypedDict):
    gameAsStr: str
    gameState: ra.SerializedRaGame


class StartResponse(ActResponse):
    gameId: uuid.UUID


class JoinLeaveRequest(TypedDict):
    gameId: NotRequired[str]


class ListGamesResponse(TypedDict):
    total: int
    gameIds: List[uuid.UUID]


def get_game_repr(game: ra.RaGame) -> str:
    legal_actions = ra.get_possible_actions(game.game_state)
    val = str(game.game_state)
    if not legal_actions:
        return val
    prompt = game.get_action_prompt(legal_actions)
    return f"{val}\n\n{prompt}"


def list(dbGames: Sequence[str]) -> ListGamesResponse:
    """Generates a response from all available games in the database."""
    return ListGamesResponse(
        total=len(dbGames),
        gameIds=[uuid.UUID(gameIdStr) for gameIdStr in dbGames])


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
        return Message(message=f'Unrecognized action: {parsedMove}')

    if game.game_state.is_game_ended():
        return response
    legal_moves = ra.get_possible_actions(game.game_state)
    if not legal_moves:
        return Message(message='Internal Error: No valid actions. ')
    if parsedMove not in legal_moves:
        return Message(message=f'Only legal actions are: {legal_moves}')
    game.execute_action(parsedMove, legal_moves)
    return ActResponse(
        gameState=game.serialize(), gameAsStr=get_game_repr(game))
