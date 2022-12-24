import quart.flask_patch  # pyre-ignore[21]: Manually patched.

import asyncio
import copy
import flask_sqlalchemy
import functools
import hashlib
import logging
import os
import quart  # pyre-ignore[21]
import quart_cors
import routes
import socketio  # pyre-ignore[21]
import uuid


from quart import request
from sqlalchemy.sql import expression


from typing import Awaitable, Callable, cast, Optional, TypeVar, Union
from typing_extensions import ParamSpec

logger: logging.Logger = logging.getLogger("uvicorn.info")


app = quart.Quart(__name__)  # pyre-ignore[5]
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:////tmp/game.db"
)
logger.info("Connected to %s", os.environ["DATABASE_URL"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
_DEBUG = os.environ.get("DEBUG", False)
_DISABLE_AUTH = os.environ.get("DISABLE_AUTH", True)


# For Database support.
db = flask_sqlalchemy.SQLAlchemy(app)


class Game(db.Model):  # pyre-ignore[11]
    """Database used to persist games across requests."""

    # We use the uuid.hex property, which is 32-char string.
    # pyre-ignore[11]
    id: db.Column = db.Column(db.String(32), primary_key=True)
    # This is a pickle-d version of the game so we can restore state.
    data: db.Column = db.Column(db.PickleType, nullable=False)


class User(db.Model):
    """Databse used to persist user accounts."""

    username: db.Column = db.Column(db.String, primary_key=True)

    # This is a hashed version using the given salt.
    password_hash: db.Column = db.Column(db.String)
    salt: db.Column = db.Column(db.String)

    def set_password(self, password: str) -> None:
        self.salt = os.urandom(16)
        self.password_hash = hashlib.sha256(
            password.encode() + self.salt.encode()
        ).hexdigest()

    def check_password(self, password: str) -> bool:
        new_hash = hashlib.sha256(password.encode() + self.salt.encode()).hexdigest()
        return new_hash == self.password_hash


# Creates the database and tables as specified by all db.Model classes.
async def setup() -> None:
    async with app.app_context():
        # db.drop_all()
        db.create_all()


try:
    asyncio.get_running_loop().create_task(setup())
except RuntimeError:  # "RuntimeError: There is no current event loop..."
    asyncio.run(setup())


# For websocket support.
sio = socketio.AsyncServer(  # pyre-ignore[5]
    cors_allowed_origins="*", async_mode="asgi"
)

T = TypeVar("T")
P = ParamSpec("P")


def login_required(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        # pyre-ignore[16]
        sid = (await request.json).get("socketId") if len(args) == 0 else args[0]
        errorMsg = routes.ErrorMessage("Not logged in!")
        if not sid or not isinstance(sid, str):
            sio.emit("logout", errorMsg, to=sid)
            return cast(T, errorMsg)
        # This is a sio event handlers.
        session = await sio.get_session(sid)
        if not session.get("loggedIn"):
            sio.emit("logout", routes.ErrorMessage("Not logged in!"), to=sid)
            return cast(T, errorMsg)
        return await func(*args, **kwargs)

    # When in debug mode, don't enforce login requirements.
    if _DISABLE_AUTH:
        return func
    return wrapper


@app.route("/", methods=["GET"])  # pyre-ignore[56]
async def hello_world() -> str:
    return "<p>Hello, World!</p>"


@app.route("/list", methods=["GET", "POST"])  # pyre-ignore[56]
@login_required
async def list() -> routes.ListGamesResponse:
    results = db.session.scalars(expression.select(Game)).all()
    return routes.list([(result.id, result.data) for result in results])


@app.route("/start", methods=["POST"])  # pyre-ignore[56]
@login_required
async def start() -> Union[routes.Message, routes.StartResponse]:
    if not (players := (await request.json).get("playerNames")) or len(players) < 2:
        return routes.WarningMessage(message="Cannot start game. Need player names.")

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
@login_required
async def delete() -> routes.Message:
    if not (gameIdStr := (await request.json).get("gameId")):
        return routes.ErrorMessage(message="Invalid request.")
    try:
        gameId = uuid.UUID(gameIdStr)
    except ValueError as err:
        return routes.ErrorMessage(message=str(err))
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return routes.WarningMessage(message=f"No game with id {gameId} found.")

    db.session.delete(dbGame)
    db.session.commit()
    return routes.SuccessMessage(message=f"Deleted game: {gameId}")


@app.route("/action", methods=["POST"])  # pyre-ignore[56]
@login_required
async def action() -> Union[routes.Message, routes.ActionResponse]:
    async def fetchGame(gameId: uuid.UUID) -> Optional[routes.RaGame]:
        if not (dbGame := db.session.get(Game, gameId.hex)):
            return None
        return dbGame.data

    async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
        if not (dbGame := db.session.get(Game, gameId.hex)):
            return False
        dbGame.data = copy.deepcopy(game)
        db.session.commit()
        return True

    json = await request.json
    gameIdStr, command, sid = (
        json.get("gameId"),
        json.get("command"),
        json.get("socketId"),
    )
    if (
        command
        and command.upper() == "LOAD"
        and (game := await fetchGame(uuid.UUID(gameIdStr)))
    ):
        if sid:
            sio.enter_room(sid, gameIdStr)
        return routes.ActionResponse(
            gameState=game.serialize(), gameAsStr=routes.get_game_repr(game)
        )
    if not sid:
        return routes.ErrorMessage(message="Cannot determine player state. Refresh?")

    command = routes.ActionRequest(gameId=gameIdStr, command=command)
    session = await sio.get_session(sid)
    response = await routes.action(
        command, session.get("playerIdx"), fetchGame, saveGame
    )

    # Update all connected clients with the updated game except client that
    # sent the update.
    await sio.emit("update", response, to=gameIdStr, skip_sid=sid)

    # Update the initiator of the event.
    return response


@sio.event  # pyre-ignore[56]
@login_required
async def act(sid: str, data: routes.ActionRequest) -> None:
    async def fetchGame(gameId: uuid.UUID) -> Optional[routes.RaGame]:
        async with app.app_context():
            if not (dbGame := db.session.get(Game, gameId.hex)):
                return None
        return dbGame.data

    async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
        async with app.app_context():
            if not (dbGame := db.session.get(Game, gameId.hex)):
                return False
            dbGame.data = copy.deepcopy(game)
            db.session.commit()
        return True

    if (
        (command := data.get("command"))
        and command.upper() == "LOAD"
        and (gameIdStr := data.get("gameId"))
        and (game := await fetchGame(uuid.UUID(gameIdStr)))
    ):
        sio.enter_room(sid, gameIdStr)
        response = routes.ActionResponse(
            gameState=game.serialize(), gameAsStr=routes.get_game_repr(game)
        )
    else:
        session = await sio.get_session(sid)
        response = await routes.action(
            data, session.get("playerIdx"), fetchGame, saveGame
        )
    await sio.emit("update", response, to=data.get("gameId"), skip_sid=sid)


@sio.event  # pyre-ignore[56]
async def login(sid: str, data: routes.LoginOrRegisterRequest) -> None:
    """SocketIO handlers for when a user attempts to login/register."""
    if not (username := data.get("username")):
        return
    if not (password := data.get("password")):
        return
    async with app.app_context():
        user = db.session.get(User, username)
        # This is a registration request.
        if not user:
            user = User(username=username)  # pyre-ignore[28]
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            await sio.emit(
                "login",
                routes.SuccessMessage(
                    message=f"{username} account created. Successfully logged in."
                ),
                to=sid,
            )
            return
    if not user.check_password(password):
        await sio.emit(
            "login", routes.WarningMessage(message=f"{username} cannot login."), to=sid
        )
        return
    async with sio.session(sid) as session:
        session["loggedIn"] = True
    await sio.emit(
        "login", routes.SuccessMessage(message=f"{username} logged in."), to=sid
    )


@sio.event  # pyre-ignore[56]
async def logout(sid: str) -> None:
    """SocketIO handler where the currently connected client is requesting to log out."""
    async with sio.session(sid) as session:
        session["loggedIn"] = False
    await sio.emit("logout", routes.SuccessMessage("Successfully logged out."), to=sid)


@sio.event  # pyre-ignore[56]
@login_required
async def join(sid: str, data: routes.JoinLeaveRequest) -> None:
    """SocketIO handler for joining a specific room to listen to game updates."""
    if not (gameIdStr := data.get("gameId")):
        return
    if not (name := data.get("name")):
        return
    gameId = uuid.UUID(gameIdStr)
    async with app.app_context():
        if not (dbGame := db.session.get(Game, gameId.hex)):
            return
        game = dbGame.data
        idxs = [
            i
            for i, (occupied, player) in enumerate(
                zip(game.player_in_game, game.player_names)
            )
            if not occupied and player.lower() == name.lower()
        ]
        if not idxs:
            if _DEBUG:
                logger.info("Client %s (%s) SPECTATING room: %s", sid, name, gameIdStr)
            await sio.emit("spectate", to=sid)
            sio.enter_room(sid, gameIdStr)
            return
        # Take first available index. Duplicate names are based on join order.
        playerIdx = idxs[0]
        game.player_in_game[playerIdx] = True
        dbGame.data = copy.deepcopy(game)
        db.session.commit()

    sio.enter_room(sid, gameIdStr)
    async with sio.session(sid) as session:
        session["gameId"] = gameIdStr
        session["playerIdx"] = playerIdx
        session["playerName"] = name
    if _DEBUG:
        logger.info("Client %s (%s) JOINED room: %s", sid, name, gameIdStr)
    return


async def _leaveGame(sid: str, gameIdStr: str, name: Optional[str] = None) -> None:
    session = await sio.get_session(sid)
    sio.leave_room(sid, gameIdStr)

    if (playerIdx := session.get("playerIdx")) is None:
        async with sio.session(sid) as session:
            session["gameId"] = None
        if _DEBUG:
            logger.info("Client %s (%s) LEFT SPECTATING room: %s", sid, name, gameIdStr)
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
        session["playerIdx"] = None
        session["playerName"] = None

    if _DEBUG:
        logger.info("Client %s (%s) LEFT room: %s", sid, name, gameIdStr)


@sio.event  # pyre-ignore[56]
@login_required
async def leave(sid: str, data: routes.JoinLeaveRequest) -> None:
    if gameIdStr := data.get("gameId"):
        await _leaveGame(sid, gameIdStr, data.get("name"))


# Client connections. TODO: Use for auth cookies and stuff.
@sio.event  # pyre-ignore[56]
async def connect(sid: str, environ, auth) -> None:  # pyre-ignore[2]
    if _DEBUG:
        logger.info("Client %s CONNECTED.", sid)


@sio.event  # pyre-ignore[56]
async def disconnect(sid: str) -> None:
    session = await sio.get_session(sid)
    for room in sio.rooms(sid):
        if room != sid:
            await _leaveGame(sid, room, session.get("name"))
    if _DEBUG:
        logger.info("Client %s DISCONNECTED.", sid)


# pyre-ignore[11]
app: quart.app.Quart = quart_cors.cors(app, allow_origin="*")
asgi_app = socketio.ASGIApp(sio, app)  # pyre-ignore[5]
