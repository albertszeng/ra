from game import ra
from game import info

import copy
import flask
import flask_cors
import flask_socketio  # pyre-ignore[21]
import flask_sqlalchemy
import os
import uuid

from asgiref import wsgi
from flask import abort, request
from flask_socketio import join_room, leave_room
from sqlalchemy.ext import mutable
from sqlalchemy.sql import expression


from typing import Dict, List, Union
from typing_extensions import NotRequired, TypedDict


app = flask.Flask(__name__)
flask_cors.CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = flask_sqlalchemy.SQLAlchemy(app)
# pyre-ignore[5]
socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*")


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
with app.app_context():
    db.create_all()


def get_game_repr(game: ra.RaGame) -> str:
    legal_actions = game.get_possible_actions()
    val = str(game.game_state)
    if not legal_actions:
        return val
    prompt = game.get_action_prompt(legal_actions, helpful_prompt=True)
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


@app.route("/", methods=["GET"])
def hello_world() -> str:
    return "<p>Hello, World!</p>"


class ListGamesResponse(TypedDict):
    total: int
    gameIds: List[uuid.UUID]


@app.route("/list", methods=["GET", "POST"])
def list() -> ListGamesResponse:
    """Lists all available games in the database."""
    results = db.session.scalars(expression.select(Game.id)).all()
    return ListGamesResponse(
        total=len(results),
        gameIds=[uuid.UUID(gameIdStr) for gameIdStr in results])


@app.route("/start", methods=["POST"])
def start() -> Union[Message, StartResponse]:
    gameId = uuid.uuid4()
    if not (players := request.json.get("playerNames")) or len(players) < 2:
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


@app.route("/delete", methods=["POST"])
def delete() -> Message:
    if not (gameIdStr := request.json.get('gameId')):
        return Message(message='Invalid request.')

    gameId = uuid.UUID(gameIdStr)
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return Message(message=f'No game with id {gameId} found.')

    socketio.close_room(gameId)
    db.session.delete(dbGame)
    db.session.commit()
    return Message(message=f'Deleted game: {gameId}')


@app.route("/action", methods=["POST"])
def action() -> Union[Message, ActResponse]:
    _SERVER_ACTIONS = ['LOAD']
    if not (gameIdStr := request.json.get('gameId')):
        return Message(message=f'Cannot act on non-existing game: {gameIdStr}')
    gameId = uuid.UUID(gameIdStr)
    action = request.json.get("command")
    if not action:
        return Message(message='No action')

    if action not in _SERVER_ACTIONS:
        action = ra.parse_action(action)
        if isinstance(action, str):
            return Message(message=f'Unrecognized action: {action}')

    if not (dbGame := db.session.get(Game, gameId.hex)):
        return Message(message=f'No active game with id: {gameId}')
    game = dbGame.data
    if game.game_state.is_game_ended() or action == 'LOAD':
        return ActResponse(
            gameState=game.serialize(), gameAsStr=get_game_repr(game))

    legal_actions = game.get_possible_actions()
    if not legal_actions:
        return Message(message='Internal Error: No valid actions. ')
    if action not in legal_actions:
        return Message(message=f'Only legal actions are: {legal_actions}')
    t = game.execute_action(action, legal_actions)
    dbGame.data = copy.copy(game)
    db.session.commit()

    with open(game.outfile, "a+") as outfile:
        if action == info.DRAW:
            outfile.write(f"{info.DRAW_OPTIONS[0]} {t}\n")
        else:
            outfile.write(f"{action}\n")

    response = ActResponse(
        gameState=game.serialize(), gameAsStr=get_game_repr(game))
    # Update all connected clients with the updated game except client that
    # sent the update.
    socketio.emit(
        'update', response, to=gameIdStr,
        skip_sid=request.json.get('socketId'))

    # Update the initiator of the event.
    return response


# Clients can join and leave specific rooms to listen to the updates
# as the game progresses.
@socketio.on('join')  # pyre-ignore[56]
def on_join(data: JoinLeaveRequest) -> None:
    gameIdStr = data.get('gameId')
    if not gameIdStr:
        return
    gameId = uuid.UUID(gameIdStr)
    if not db.session.get(Game, gameId.hex):
        return
    print(f'Client: {request.sid} joined room: {gameIdStr}')  # pyre-ignore[16]
    join_room(gameIdStr)


@socketio.on('leave')  # pyre-ignore[56]
def on_leave(data: JoinLeaveRequest) -> None:
    gameIdStr = data.get('gameId')
    if not gameIdStr:
        return
    leave_room(gameIdStr)

asgi_app = wsgi.WsgiToAsgi(app)
