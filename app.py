import quart.flask_patch  # pyre-ignore[21]: Manually patched. # isort: skip

import asyncio
import base64
import copy
import functools
import hashlib
import logging
import os
import uuid
from typing import Awaitable, Callable, Optional, Tuple, TypeVar, Union, cast

import flask_sqlalchemy
import jwt
import quart  # pyre-ignore[21]
import quart_cors
import socketio  # pyre-ignore[21]
from quart import request
from sqlalchemy.sql import expression
from typing_extensions import ParamSpec

from backend import config, routes, util

logger: logging.Logger = logging.getLogger("uvicorn.info")


app = quart.Quart(__name__)  # pyre-ignore[5]
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:////tmp/game.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
logger.info("Connected to %s", os.environ["DATABASE_URL"])

_C: config.Config = config.get()
logger.info(f"Configuration: {_C}")

# For Database support.
db = flask_sqlalchemy.SQLAlchemy(app)


class Game(db.Model):  # pyre-ignore[11]
    """Database used to persist games across requests."""

    # We use the uuid.hex property, which is 32-char string.
    # pyre-ignore[11]
    id: db.Column = db.Column(db.String(32), primary_key=True)

    # Visibility for the game. Public games are listed to everyone.
    # Private games must be joined with the gameId.
    visibility: db.Column = db.Column(db.Enum(routes.Visibility), nullable=False)

    # This is a pickle-d version of the game so we can restore state.
    data: db.Column = db.Column(db.PickleType, nullable=False)


class User(db.Model):
    """Databse used to persist user accounts."""

    username: db.Column = db.Column(db.String, primary_key=True)

    # This is a hashed version using the given salt.
    password_hash: db.Column = db.Column(db.String)
    salt: db.Column = db.Column(db.String)

    def set_password(self, password: str) -> None:
        self.salt = base64.b64encode(os.urandom(16)).decode()
        self.password_hash = hashlib.sha256(
            password.encode() + self.salt.encode()
        ).hexdigest()

    def check_password(self, password: str) -> bool:
        salt = self.salt if isinstance(self.salt, bytes) else self.salt.encode()
        new_hash = hashlib.sha256(password.encode() + salt).hexdigest()
        return new_hash == self.password_hash


# Creates the database and tables as specified by all db.Model classes.
async def setup() -> None:
    async with app.app_context():
        if _C.RESET_DATABASE:
            logger.info("DROPPING TABLES")
            db.drop_all()
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


async def _join_room(
    sid: str, data: routes.JoinSessionSuccess
) -> routes.JoinSessionSuccess:
    gameIdStr, playerName, playerIdx = (
        data["gameId"],
        data["playerName"],
        data.get("playerIdx"),
    )
    if playerIdx is None:
        if _C.DEBUG:
            logger.info(
                "Client %s (%s) SPECTATING room: %s", sid, playerName, gameIdStr
            )
        await sio.emit("spectate", True, room=sid)
        sio.enter_room(sid, gameIdStr)
        return data

    sio.enter_room(sid, gameIdStr)
    async with sio.session(sid) as session:
        session["gameId"] = gameIdStr
        session["playerIdx"] = playerIdx
        session["playerName"] = playerName
    await sio.emit("spectate", False, room=sid)
    if _C.DEBUG:
        logger.info("Client %s (%s) JOINED room: %s", sid, playerName, gameIdStr)
    return data


async def _leave_room(sid: str, gameIdStr: str, name: Optional[str] = None) -> None:
    session = await sio.get_session(sid)
    sio.leave_room(sid, gameIdStr)

    if (playerIdx := session.get("playerIdx")) is None:
        async with sio.session(sid) as session:
            session["gameId"] = None
        if _C.DEBUG:
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

    if _C.DEBUG:
        logger.info("Client %s (%s) LEFT room: %s", sid, name, gameIdStr)


def login_required(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    @functools.wraps(func)
    async def login_fn(*args: P.args, **kwargs: P.kwargs) -> T:
        # pyre-ignore[16]
        sid = (await request.json).get("socketId") if len(args) == 0 else args[0]
        errorMsg = routes.ErrorMessage("Not logged in!")
        if not sid or not isinstance(sid, str):
            await sio.emit("logout", errorMsg, room=sid)
            return cast(T, errorMsg)
        session = await sio.get_session(sid)
        if not session.get("loggedIn") or not session.get("username"):
            await sio.emit("logout", errorMsg, room=sid)
            return cast(T, errorMsg)
        return await func(session["username"], *args, **kwargs)

    @functools.wraps(login_fn)
    async def logger_fn(*args: P.args, **kwargs: P.kwargs) -> T:
        if _C.DEBUG:
            logger.info("%s: Inputs on login: %s, %s", func.__name__, args, kwargs)
        ret = await login_fn(*args, **kwargs)
        if _C.DEBUG:
            logger.info("%s: Outputs: %s", func.__name__, ret)
        return ret

    return logger_fn


@app.route("/", methods=["GET"])  # pyre-ignore[56]
async def hello_world() -> str:
    return "<p>Hello, World!</p>"


@sio.event  # pyre-ignore[56]
@login_required
async def list_games(username: str, sid: str) -> routes.ListGamesResponse:
    async with app.app_context():
        results = db.session.scalars(expression.select(Game)).all()
    response = routes.list(
        username,
        [(uuid.UUID(result.id), result.data, result.visibility) for result in results],
    )
    await sio.emit("list_games", response, room=sid)
    return response


@sio.event  # pyre-ignore[56]
@login_required
async def start_game(
    username: str, sid: str, data: routes.StartRequest
) -> Tuple[routes.Message, Optional[routes.ListGamesResponse]]:
    async def commitGame(
        gameId: uuid.UUID, game: routes.RaGame, visibility: routes.Visibility
    ) -> None:
        async with app.app_context():
            # Add game to database.
            dbGame = Game(  # pyre-ignore[28]
                id=gameId.hex, data=game, visibility=visibility
            )
            db.session.add(dbGame)
            db.session.commit()

    msg, lstResponse = await routes.start(data, username, commitGame=commitGame)
    await sio.emit("update", msg, room=sid)
    if lstResponse:
        # TODO(luis): Don't do this for private.
        await sio.emit("list_games", lstResponse)
    return msg, lstResponse


@sio.event  # pyre-ignore[56]
@login_required
async def delete(
    username: str, sid: str, data: routes.DeleteRequest
) -> Tuple[routes.Message, Optional[routes.ListGamesResponse]]:
    async def fetchGame(gameId: uuid.UUID) -> Optional[routes.RaGame]:
        async with app.app_context():
            if not (dbGame := db.session.get(Game, gameId.hex)):
                return None
            return dbGame.data

    async def persistDelete(gameId: uuid.UUID) -> bool:
        async with app.app_context():
            if not (dbGame := db.session.get(Game, gameId.hex)):
                return False
            db.session.delete(dbGame)
            db.session.commit()
        return True

    if not (gameIdStr := data.get("gameId")):
        return routes.ErrorMessage(message="Must provide a gameId with request."), None

    msg, lstResponse = await routes.delete(
        gameIdStr, username, fetchGame=fetchGame, persistDelete=persistDelete
    )
    # Update game room as well as sid.
    await sio.emit("update", msg, to=gameIdStr)
    await sio.emit("delete", msg, to=sid)
    if lstResponse:
        await sio.emit("list_games", lstResponse)
    return msg, lstResponse


@sio.event  # pyre-ignore[56]
@login_required
async def act(
    username: str, sid: str, data: routes.ActionRequest
) -> Union[routes.Message, routes.ActionResponse, routes.StartResponse]:
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

    if not (gameIdStr := data.get("gameId")):
        return routes.ErrorMessage(message="Must provide a gameId with request.")
    if (
        (command := data.get("command"))
        and command.upper() == "LOAD"
        and (game := await fetchGame(uuid.UUID(gameIdStr)))
    ):
        if not game.initialized():
            return routes.WarningMessage(f"Cannot load incomplete game: {gameIdStr}.")

        async def fetchLocal(
            gameId: uuid.UUID, _game: routes.RaGame = game
        ) -> routes.RaGame:
            # Uses default param evaluation to capture the 'game' variable.
            assert _game is not None
            return _game

        resp = await routes.join_game(
            username,
            request=routes.JoinLeaveRequest(gameId=gameIdStr),
            fetchGame=fetchLocal,
            saveGame=saveGame,
        )
        if "message" in resp:
            await sio.emit("update", resp, room=sid)
            return cast(routes.Message, resp)
        resp = await _join_room(sid, cast(routes.JoinSessionSuccess, resp))
        response = routes.StartResponse(
            gameState=game.serialize(),
            gameAsStr=routes.get_game_repr(game),
            action=command.upper(),
            username=username,
            gameId=resp["gameId"],
        )
    else:
        session = await sio.get_session(sid)
        response = await routes.action(
            data, session.get("playerIdx"), username, fetchGame, saveGame
        )
    await sio.emit("update", response, room=gameIdStr)
    return response


@sio.event  # pyre-ignore[56]
@login_required
async def add_player(
    username: str, sid: str, data: routes.AddPlayerRequest
) -> Union[routes.Message, routes.ListGamesResponse]:
    async def fetchGame(
        gameId: uuid.UUID,
    ) -> Optional[Tuple[routes.RaGame, routes.Visibility]]:
        async with app.app_context():
            if not (dbGame := db.session.get(Game, gameId.hex)):
                return None
            return dbGame.data, dbGame.visibility

    async def saveGame(gameId: uuid.UUID, game: routes.RaGame) -> bool:
        async with app.app_context():
            if not (dbGame := db.session.get(Game, gameId.hex)):
                return False
            dbGame.data = copy.deepcopy(game)
            db.session.commit()
            return True

    response = await routes.add_player(
        username, data.gameId, fetchGame=fetchGame, saveGame=saveGame
    )
    if "message" in response:
        await sio.emit("update", response, to=sid)
        return response
    # TODO: respect visibility settings. Currently update is sent to all connected clients.
    await sio.emit("list_games", response)
    return response


@sio.event  # pyre-ignore[56]
@login_required
async def join(
    username: str, sid: str, data: routes.JoinLeaveRequest
) -> Union[routes.Message, routes.JoinSessionSuccess]:
    """SocketIO handler for joining a specific room to listen to game updates."""

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

    resp = await routes.join_game(
        username, request=data, fetchGame=fetchGame, saveGame=saveGame
    )
    if "message" in resp:
        await sio.emit("update", resp, room=sid)
        return resp
    return await _join_room(sid, cast(routes.JoinSessionSuccess, resp))


@sio.event  # pyre-ignore[56]
async def login(sid: str, data: routes.LoginOrRegisterRequest) -> None:
    """SocketIO handlers for when a user attempts to login/register."""
    username, password, oldToken = (
        data.get("username"),
        data.get("password"),
        data.get("token"),
    )

    if util.use_token(data) and (
        response := routes.authenticate_token(oldToken, _C.SECRET_KEY)
    ):
        async with sio.session(sid) as session:
            session["loggedIn"] = True
            session["username"] = response["username"]
        await sio.emit("login", response, room=sid)
        return
    # Must have set username and password.
    if not (username and password):
        return

    # Authenticate with data provided.
    payload = {"username": username, "exp": routes.gen_exp()}
    token = jwt.encode(payload, _C.SECRET_KEY, algorithm="HS256")

    successMessage = f"{username} is now logged in!"
    async with app.app_context():
        user = db.session.get(User, username)
        # Register the user first.
        if not user:
            user = User(username=username)  # pyre-ignore[28]
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            successMessage = f"New account created. {successMessage}"

        if not user.check_password(password):
            response = routes.WarningMessage(message=f"{username} cannot login.")
            await sio.emit("login", response, room=sid)
            return
    # Successful login at this point.
    async with sio.session(sid) as session:
        session["loggedIn"] = True
        session["username"] = username
    response = routes.LoginResponse(
        token=token,
        username=username,
        message=successMessage,
        level="success",
    )
    await sio.emit("login", response, room=sid)


@sio.event  # pyre-ignore[56]
async def logout(sid: str) -> routes.Message:
    """SocketIO handler where the client is requesting to log out."""
    for room in sio.rooms(sid):
        if room != sid:
            await _leave_room(sid, room, (await sio.get_session(sid)).get("username"))
    async with sio.session(sid) as session:
        session["loggedIn"] = False
        session["username"] = None
    response = routes.SuccessMessage("Successfully logged out.")
    await sio.emit("logout", response, room=sid)
    return response


@sio.event  # pyre-ignore[56]
async def leave(sid: str, data: routes.JoinLeaveRequest) -> None:
    session = await sio.get_session(sid)
    if gameIdStr := data.get("gameId"):
        await _leave_room(sid, gameIdStr, session.get("username"))


# Client connections. TODO: Use for auth cookies and stuff.
@sio.event  # pyre-ignore[56]
async def connect(sid: str, environ, auth) -> None:  # pyre-ignore[2]
    if _C.DEBUG:
        logger.info("Client %s CONNECTED.", sid)


@sio.event  # pyre-ignore[56]
async def disconnect(sid: str) -> None:
    session = await sio.get_session(sid)
    for room in sio.rooms(sid):
        if room != sid:
            await _leave_room(sid, room, session.get("username"))
    if _C.DEBUG:
        logger.info("Client %s DISCONNECTED.", sid)


# pyre-ignore[11]
app: quart.app.Quart = quart_cors.cors(app, allow_origin="*")
asgi_app = socketio.ASGIApp(sio, app)  # pyre-ignore[5]
