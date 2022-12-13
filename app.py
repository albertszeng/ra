import quart.flask_patch  # pyre-ignore[21]: Manually patched.

from game import ra

import asyncio
import copy
import flask_sqlalchemy
import logging
import os
import quart  # pyre-ignore[21]
import quart_cors
import socketio  # pyre-ignore[21]
import uuid


from quart import request
from sqlalchemy.ext import mutable
from sqlalchemy.sql import expression


from typing import Dict, List, Union
from typing_extensions import NotRequired, TypedDict

logger: logging.Logger = logging.getLogger("uvicorn.info")


app = quart.Quart(__name__)  # pyre-ignore[5]
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
logger.info('Connected to %s', os.environ['DATABASE_URL'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# For Database support.
db = flask_sqlalchemy.SQLAlchemy(app)


class RaGame(mutable.Mutable, ra.RaGame):
    """Required so database can update on changes to state."""

    def __getstate__(self) -> Dict[str, str]:
        d = self.__dict__.copy()
        d.pop('_parents', None)
        return d


class Game(db.Model):  # pyre-ignore[11]
    """Database used to persist games across requests. """
    # We use the uuid.hex property, which is 32-char string.
    # pyre-ignore[11]
    id: db.Column = db.Column(db.String(32), primary_key=True)

    # This is a pickle-d version of the game so we can restore state.
    data: db.Column = db.Column(db.PickleType, nullable=False)


# Creates the database and tables as specified by all db.Model classes.
async def setup() -> None:
    async with app.app_context():
        db.create_all()

try:
    asyncio.get_running_loop().create_task(setup())
except RuntimeError:  # 'RuntimeError: There is no current event loop...'
    asyncio.run(setup())


def get_game_repr(game: ra.RaGame) -> str:
    legal_actions = ra.get_possible_actions(game.game_state)
    val = str(game.game_state)
    if not legal_actions:
        return val
    prompt = game.get_action_prompt(legal_actions)
    return f"{val}\n\n{prompt}"


class Message(TypedDict):
    message: str


class ActResponse(TypedDict):
    gameAsStr: str
    gameState: ra.SerializedRaGame


class StartResponse(ActResponse):
    gameId: uuid.UUID


class JoinLeaveRequest(TypedDict):
    gameId: NotRequired[str]


# For websocket support.
sio = socketio.AsyncServer(  # pyre-ignore[5]
    cors_allowed_origins="*", async_mode='asgi')


@app.route("/", methods=["GET"])  # pyre-ignore[56]
async def hello_world() -> str:
    return "<p>Hello, World!</p>"


class ListGamesResponse(TypedDict):
    total: int
    gameIds: List[uuid.UUID]


@app.route("/list", methods=["GET", "POST"])  # pyre-ignore[56]
async def list() -> ListGamesResponse:
    """Lists all available games in the database."""
    results = db.session.scalars(expression.select(Game.id)).all()
    return ListGamesResponse(
        total=len(results),
        gameIds=[uuid.UUID(gameIdStr) for gameIdStr in results])


@app.route("/start", methods=["POST"])  # pyre-ignore[56]
async def start() -> Union[Message, StartResponse]:
    gameId = uuid.uuid4()
    if (not (players := (await request.json).get("playerNames"))
            or len(players) < 2):
        return Message(message='Cannot start game. Need player names.')

    game = ra.RaGame(
        player_names=players,
        outfile=f"{gameId}.txt"
    )
    game.init_game()

    # Add game to database.
    dbGame = Game(id=gameId.hex, data=game)  # pyre-ignore[28]
    db.session.add(dbGame)
    db.session.commit()

    return StartResponse(
        gameId=gameId,
        gameState=game.serialize(),
        gameAsStr=get_game_repr(game))


@app.route("/delete", methods=["POST"])  # pyre-ignore[56]
async def delete() -> Message:
    if not (gameIdStr := (await request.json).get('gameId')):
        return Message(message='Invalid request.')

    gameId = uuid.UUID(gameIdStr)
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return Message(message=f'No game with id {gameId} found.')

    db.session.delete(dbGame)
    db.session.commit()
    return Message(message=f'Deleted game: {gameId}')


@app.route("/action", methods=["POST"])  # pyre-ignore[56]
async def action() -> Union[Message, ActResponse]:
    _SERVER_ACTIONS = ['LOAD']
    if not (gameIdStr := (await request.json).get('gameId')):
        return Message(message=f'Cannot act on non-existing game: {gameIdStr}')
    gameId = uuid.UUID(gameIdStr)
    action = (await request.json).get("command")
    if not action:
        return Message(message='No action')

    if action not in _SERVER_ACTIONS:
        action = ra.parse_action(action)
        if isinstance(action, str):
            return Message(message=f'Unrecognized action: {action}')

    if not (dbGame := db.session.get(Game, gameId.hex)):
        return Message(message=f'No active game with id: {gameId}')
    game = dbGame.data
    sid = (await request.json).get('socketId')
    response = ActResponse(
        gameState=game.serialize(), gameAsStr=get_game_repr(game))
    if game.game_state.is_game_ended():
        return response
    if action == 'LOAD':
        sio.enter_room(sid, gameIdStr)
        return response

    legal_actions = ra.get_possible_actions(game.game_state)
    if not legal_actions:
        return Message(message='Internal Error: No valid actions. ')
    if action not in legal_actions:
        return Message(message=f'Only legal actions are: {legal_actions}')
    game.execute_action(action, legal_actions)
    dbGame.data = copy.copy(game)
    db.session.commit()

    response = ActResponse(
        gameState=game.serialize(), gameAsStr=get_game_repr(game))
    # Update all connected clients with the updated game except client that
    # sent the update.
    await sio.emit('update', response, to=gameIdStr, skip_sid=sid)

    # Update the initiator of the event.
    return response


# Clients can join and leave specific rooms to listen to the updates
# as the game progresses.
@sio.event  # pyre-ignore[56]
async def join(sid: str, data: JoinLeaveRequest) -> None:
    gameIdStr = data.get('gameId')
    if not gameIdStr:
        return
    gameId = uuid.UUID(gameIdStr)
    async with app.app_context():
        if not db.session.get(Game, gameId.hex):
            return
    sio.enter_room(sid, gameIdStr)
    logger.info("Client %s JOINED room: %s", sid, gameIdStr)
    return


@sio.event  # pyre-ignore[56]
async def leave(sid: str, data: JoinLeaveRequest) -> None:
    gameIdStr = data.get('gameId')
    if not gameIdStr:
        return
    sio.leave_room(sid, gameIdStr)
    logger.info("Client %s LEFT room: %s", sid, gameIdStr)
    return


# Client connections. TODO: Use for auth cookies and stuff.
@sio.event  # pyre-ignore[56]
async def connect(sid: str, environ, auth) -> None:  # pyre-ignore[2]
    logger.info("Client %s CONNECTED.", sid)


@sio.event  # pyre-ignore[56]
async def disconnect(sid: str) -> None:
    logger.info("Client %s DISCONNECTED.", sid)


# pyre-ignore[11]
app: quart.app.Quart = quart_cors.cors(app, allow_origin="*")
asgi_app = socketio.ASGIApp(sio, app)  # pyre-ignore[5]
