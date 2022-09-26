from .. import ra
from .. import game_info

import copy
import flask
import flask_cors
import flask_sqlalchemy
import uuid

from flask import request
from sqlalchemy.ext import mutable


from typing import Dict


app = flask.Flask(__name__)
flask_cors.CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = flask_sqlalchemy.SQLAlchemy(app)


class RaGame(mutable.Mutable, ra.RaGame):
    """Required so database can update on changes to state."""

    def __getstate__(self):
        d = self.__dict__.copy()
        d.pop('_parents', None)
        return d


class Game(db.Model):
    """Database used to persist games across requests. """
    # We use the uuid.hex property, which is 32-char string.
    id = db.Column(db.String(32), primary_key=True)

    # This is a pickle-d version of the game so we can restore state.
    data = db.Column(db.PickleType, nullable=False)


# Creates the database and tables as specified by all db.Model classes.
db.create_all()


def get_game_repr(game: ra.RaGame) -> str:
    legal_actions = game.get_possible_actions()
    prompt = game.get_action_prompt(legal_actions, helpful_prompt=True)
    return f"{game.game_state}\n\n{prompt}"


@app.route("/", methods=["GET"])
def hello_world() -> str:
    return "<p>Hello, World!</p>"


@app.route("/start", methods=["POST"])
def start():
    gameId = uuid.uuid4()
    if not (players := request.json.get("player_names")) or len(players) < 2:
        return {'message': 'Cannot start game. Need player names.'}

    game = ra.RaGame(
        player_names=players,
        outfile=f"{gameId}.txt"
    )
    game.init_game()

    # Add game to database.
    dbGame = Game(id=gameId.hex, data=game)
    db.session.add(dbGame)
    db.session.commit()

    return {
        'gameId': gameId,
        'gameState': get_game_repr(game),
    }


@app.route("/delete", methods=["POST"])
def delete():
    if not (gameId := request.json.get('gameId')):
        return {'messsage': 'Invalid request.'}

    gameId = uuid.UUID(gameId)
    if not (dbGame := db.session.get(Game, gameId.hex)):
        return {'messsage': f'No game with id {gameId} found.'}

    db.session.delete(dbGame)
    db.session.commit()
    return {
        'message': f'Deleted game: {gameId}',
    }


@app.route("/action", methods=["POST"])
def action():
    _SERVER_ACTIONS = ['LOAD']
    if not (gameId := request.json.get('gameId')):
        return {'message': f'Cannot act on non-existing game: {gameId}'}
    gameId = uuid.UUID(gameId)
    if not (action := request.json.get("command")):
        return {'message': 'No action'}


    if action not in _SERVER_ACTIONS:
        action = ra.parse_action(action)
        if isinstance(action, str):
            return {'message': f'Unrecognized action: {action}'}

    if not (dbGame := db.session.get(Game, gameId.hex)):
        return {'message': f'No active game with id: {gameId}'}
    game = dbGame.data
    if game.game_state.is_game_ended() or action == 'LOAD':
        return {
            'gameState': get_game_repr(game),
        }

    legal_actions = game.get_possible_actions()
    if not legal_actions:
        return {'message': 'Internal Error: No valid actions. '}
    if action not in legal_actions:
        return {'message': f'Only legal actions are: {legal_actions}'}
    t = game.execute_action(action, legal_actions)
    dbGame.data = copy.copy(game)
    db.session.commit()

    with open(game.outfile, "a+") as outfile:
        if action == game_info.DRAW:
            outfile.write(f"{game_info.DRAW_OPTIONS[0]} {t}\n")
        else:
            outfile.write(f"{action}\n")

    return {
        'gameState': get_game_repr(game),
    }
