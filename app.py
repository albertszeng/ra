import quart.flask_patch  # pyre-ignore[21]: Manually patched.

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
from sqlalchemy.sql import expression


from typing import Union, Optional

logger: logging.Logger = logging.getLogger("uvicorn.info")


app = quart.Quart(__name__)  # pyre-ignore[5]
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:////tmp/game.db')
logger.info('Connected to %s', os.environ['DATABASE_URL'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# For Database support.
db = flask_sqlalchemy.SQLAlchemy(app)


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
        # db.drop_all()
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
    results = db.session.scalars(expression.select(Game)).all()
    return routes.list([(result.id, result.data) for result in results])


@app.route("/start", methods=["POST"])  # pyre-ignore[56]
async def start() -> Union[routes.Message, routes.StartResponse]:
    if (not (players := (await request.json).get("playerNames"))
            or len(players) < 2):
        return routes.WarningMessage(
            message='Cannot start game. Need player names.')

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
        return routes.ErrorMessage(message='Invalid request.')
    try:
        gameId = uuid.UUID(gameIdStr)
    except ValueError as err:
        return routes.ErrorMessage(message=str(err))
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return routes.WarningMessage(
            message=f'No game with id {gameId} found.')

    db.session.delete(dbGame)
    db.session.commit()
    return routes.SuccessMessage(message=f'Deleted game: {gameId}')


@app.route("/action", methods=["POST"])  # pyre-ignore[56]
async def action() -> Union[routes.Message, routes.ActResponse]:
    if not (gameIdStr := (await request.json).get('gameId')):
        return routes.WarningMessage(
            message=f'Cannot act on non-existing game: {gameIdStr}')
    gameId = uuid.UUID(gameIdStr)
    action = (await request.json).get("command")
    if not action:
        return routes.ErrorMessage(message='No action')

    if not (dbGame := db.session.get(Game, gameId.hex)):
        return routes.WarningMessage(
            message=f'No active game with id: {gameId}')
    game = dbGame.data
    sid = (await request.json).get('socketId')
    if action.upper() == "LOAD":
        if sid:
            sio.enter_room(sid, gameIdStr)
        return routes.ActResponse(
            gameState=game.serialize(), gameAsStr=routes.get_game_repr(game))
    if not sid:
        return routes.ErrorMessage(
            message='Cannot determine player state. Refresh?')
    session = await sio.get_session(sid)
    if (playerIdx := session.get('playerIdx')) is None:
        return routes.InfoMessage(
            message=f'{sid} is in spectator mode. Join an open game.')

    response = routes.action(game, playerIdx, action)
    dbGame.data = copy.deepcopy(game)
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
    if not (gameIdStr := data.get('gameId')):
        return
    if not (name := data.get('name')):
        return
    gameId = uuid.UUID(gameIdStr)
    async with app.app_context():
        if not (dbGame := db.session.get(Game, gameId.hex)):
            return
        game = dbGame.data
        idxs = [i for i, (occupied, player) in enumerate(
            zip(game.player_in_game, game.player_names))
            if not occupied and player.lower() == name.lower()]
        if not idxs:
            logger.info("Client %s (%s) SPECTATING room: %s",
                        sid, name, gameIdStr)
            await sio.emit('spectate', to=sid)
            sio.enter_room(sid, gameIdStr)
            return
        # Take first available index. Duplicate names are based on join order.
        playerIdx = idxs[0]
        game.player_in_game[playerIdx] = True
        dbGame.data = copy.deepcopy(game)
        db.session.commit()

    sio.enter_room(sid, gameIdStr)
    async with sio.session(sid) as session:
        session['gameId'] = gameIdStr
        session['playerIdx'] = playerIdx
        session['playerName'] = name
    logger.info("Client %s (%s) JOINED room: %s", sid, name, gameIdStr)
    return


async def _leaveGame(
        sid: str, gameIdStr: str, name: Optional[str] = None) -> None:
    session = await sio.get_session(sid)
    sio.leave_room(sid, gameIdStr)

    if (playerIdx := session.get('playerIdx')) is None:
        async with sio.session(sid) as session:
            session['gameId'] = None
        logger.info("Client %s (%s) LEFT SPECTATING room: %s",
                    sid, name, gameIdStr)
        return

    gameId = uuid.UUID(gameIdStr)
    async with app.app_context():
        if not (dbGame := db.session.get(Game, gameId.hex)):
            return
        game = dbGame.data
        game.player_in_game[playerIdx] = False
        dbGame.data = copy.deepcopy(game)
        db.session.commit()

    async with sio.session(sid) as session:
        session['playerIdx'] = None
        session['playerName'] = None

    logger.info("Client %s (%s) LEFT room: %s", sid, name, gameIdStr)


@sio.event  # pyre-ignore[56]
async def leave(sid: str, data: routes.JoinLeaveRequest) -> None:
    if (gameIdStr := data.get('gameId')):
        await _leaveGame(sid, gameIdStr, data.get('name'))


# Client connections. TODO: Use for auth cookies and stuff.
@sio.event  # pyre-ignore[56]
async def connect(sid: str, environ, auth) -> None:  # pyre-ignore[2]
    logger.info("Client %s CONNECTED.", sid)


@sio.event  # pyre-ignore[56]
async def disconnect(sid: str) -> None:
    session = await sio.get_session(sid)
    for room in sio.rooms(sid):
        if room != sid:
            await _leaveGame(sid, room, session.get('name'))
    logger.info("Client %s DISCONNECTED.", sid)


# pyre-ignore[11]
app: quart.app.Quart = quart_cors.cors(app, allow_origin="*")
asgi_app = socketio.ASGIApp(sio, app)  # pyre-ignore[5]
