from game import ra
from game import info

import copy
import flask
import flask_cors
import flask_sqlalchemy
import os
import uuid

from flask import request
from sqlalchemy.ext import mutable


from typing import Dict, TypedDict, Union


app = flask.Flask(__name__)
flask_cors.CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
db.create_all()


def get_game_repr(game: ra.RaGame) -> str:
    legal_actions = game.get_possible_actions()
    val = str(game.game_state)
    if not legal_actions:
        return val
    prompt = game.get_action_prompt(legal_actions, helpful_prompt=True)
    return f"{val}\n\n{prompt}"


@app.route("/", methods=["GET"])
def hello_world() -> str:
    return "<p>Hello, World!</p>"


class Message(TypedDict):
    message: str


class ActResponse(TypedDict):
    gameAsStr: str
    gameState: ra.SerializedRaGame


class StartResponse(ActResponse):
    gameId: uuid.UUID


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
    if not (gameId := request.json.get('gameId')):
        return Message(message='Invalid request.')

    gameId = uuid.UUID(gameId)
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return Message(message=f'No game with id {gameId} found.')

    db.session.delete(dbGame)
    db.session.commit()
    return Message(message=f'Deleted game: {gameId}')


@app.route("/action", methods=["POST"])
def action() -> Union[Message, ActResponse]:
    _SERVER_ACTIONS = ['LOAD']
    if not (gameId := request.json.get('gameId')):
        return Message(message=f'Cannot act on non-existing game: {gameId}')
    gameId = uuid.UUID(gameId)
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

    return ActResponse(
        gameState=game.serialize(), gameAsStr=get_game_repr(game))
