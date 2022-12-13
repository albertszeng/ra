import quart.flask_patch  # pyre-ignore[21]: Manually patched.

from game import ra

import asyncio
import copy
import flask_sqlalchemy
import logging
import os
import quart  # pyre-ignore[21]
import quart_cors
import routes
import socketio  # pyre-ignore[21]
import uuid


from quart import request
from sqlalchemy.ext import mutable
from sqlalchemy.sql import expression


from typing import Dict, Union

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


# For websocket support.
sio = socketio.AsyncServer(  # pyre-ignore[5]
    cors_allowed_origins="*", async_mode='asgi')


@app.route("/", methods=["GET"])  # pyre-ignore[56]
async def hello_world() -> str:
    return "<p>Hello, World!</p>"


@app.route("/list", methods=["GET", "POST"])  # pyre-ignore[56]
async def list() -> routes.ListGamesResponse:
    results = db.session.scalars(expression.select(Game.id)).all()
    return routes.list(results)


@app.route("/start", methods=["POST"])  # pyre-ignore[56]
async def start() -> Union[routes.Message, routes.StartResponse]:
    if (not (players := (await request.json).get("playerNames"))
            or len(players) < 2):
        return routes.Message(message='Cannot start game. Need player names.')

    gameId = uuid.uuid4()
    response = routes.start(gameId, players)
    if isinstance(response, dict):
        return response
    game, startResponse = response

    # Add game to database.
    dbGame = Game(id=gameId.hex, data=game)  # pyre-ignore[28]
    db.session.add(dbGame)
    db.session.commit()

    return startResponse


@app.route("/delete", methods=["POST"])  # pyre-ignore[56]
async def delete() -> routes.Message:
    if not (gameIdStr := (await request.json).get('gameId')):
        return routes.Message(message='Invalid request.')

    gameId = uuid.UUID(gameIdStr)
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return routes.Message(message=f'No game with id {gameId} found.')

    db.session.delete(dbGame)
    db.session.commit()
    return routes.Message(message=f'Deleted game: {gameId}')


@app.route("/action", methods=["POST"])  # pyre-ignore[56]
async def action() -> Union[routes.Message, routes.ActResponse]:
    if not (gameIdStr := (await request.json).get('gameId')):
        return routes.Message(
            message=f'Cannot act on non-existing game: {gameIdStr}')
    gameId = uuid.UUID(gameIdStr)
    action = (await request.json).get("command")
    if not action:
        return routes.Message(message='No action')

    if not (dbGame := db.session.get(Game, gameId.hex)):
        return routes.Message(message=f'No active game with id: {gameId}')
    game = dbGame.data
    sid = (await request.json).get('socketId')

    response = routes.action(game, action)
    if action == 'LOAD':
        sio.enter_room(sid, gameIdStr)
        return response

    dbGame.data = copy.copy(game)
    db.session.commit()

    # Update all connected clients with the updated game except client that
    # sent the update.
    await sio.emit('update', response, to=gameIdStr, skip_sid=sid)

    # Update the initiator of the event.
    return response


# Clients can join and leave specific rooms to listen to the updates
# as the game progresses.
@sio.event  # pyre-ignore[56]
async def join(sid: str, data: routes.JoinLeaveRequest) -> None:
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
async def leave(sid: str, data: routes.JoinLeaveRequest) -> None:
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
