from game import ra
from game import info

import copy
import flask
import flask_cors
import flask_socketio  # type: ignore
import flask_sqlalchemy
import git
import os
import uuid

from flask import abort, request
from flask_socketio import emit, join_room, leave_room
from sqlalchemy.ext import mutable


from typing import Dict, Union
from typing_extensions import NotRequired, TypedDict


app = flask.Flask(__name__)
flask_cors.CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = flask_sqlalchemy.SQLAlchemy(app)
socketio = flask_socketio.SocketIO(app)  # type: ignore


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


@app.route("/update_server", methods=["GET"])
def webhook() -> Message:
    abort_code = 418
    # Do initial validations on required headers
    if 'X-Github-Event' not in request.headers:
        abort(abort_code)
    if 'X-Github-Delivery' not in request.headers:
        abort(abort_code)
    if 'X-Hub-Signature' not in request.headers:
        abort(abort_code)
    if not request.is_json:
        abort(abort_code)
    if 'User-Agent' not in request.headers:
        abort(abort_code)
    ua = request.headers.get('User-Agent')
    if not ua or not ua.startswith('GitHub-Hookshot/'):
        abort(abort_code)

    event = request.headers.get('X-GitHub-Event')
    if event == "ping":
        return Message(message='Hi!')
    if event != "push":
        return Message(message="Wrong event type")

    payload = request.get_json()
    if payload is None:
        abort(abort_code)

    if payload['ref'] != 'refs/heads/master':
        return Message(message='Not master; ignoring')

    repo = git.Repo(os.path.dirname(os.path.realpath(__file__)))
    origin = repo.remotes.origin

    pull_info = origin.pull()

    if len(pull_info) == 0:
        return Message(message="Didn't pull any information from remote!")
    if pull_info[0].flags > 128:
        return Message(message="Didn't pull any information from remote!")

    commit_hash = pull_info[0].commit.hexsha
    return Message(message='Updated PythonAnywhere server to commit {commit_hash}')

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
    # Update all connected clients with the updated game.
    socketio.emit(
        'update', response, to=gameIdStr, include_self=False,
        skip_sid=request.sid)  # type: ignore

    # Update the initiator of the event.
    return response


# Clients can join and leave specific rooms to listen to the updates
# as the game progresses.
@socketio.on('join')  # type: ignore
def on_join(data: JoinLeaveRequest) -> None:
    gameIdStr = data.get('gameId')
    if not gameIdStr:
        return
    gameId = uuid.UUID(gameIdStr)
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return
    game = dbGame.data
    join_room(gameIdStr)


@socketio.on('leave')  # type: ignore
def on_leave(data: JoinLeaveRequest) -> None:
    gameIdStr = data.get('gameId')
    if not gameIdStr:
        return
    leave_room(gameIdStr)

