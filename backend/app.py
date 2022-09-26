from typing import Dict
from .. import ra


import flask
from flask import request
from flask_cors import CORS
import uuid


app = flask.Flask(__name__)
CORS(app)


# All currently running games.
_GAMES: Dict[str, ra.RaGame] = {}


@app.route("/", methods=["GET"])
def hello_world() -> str:
    return "<p>Hello, World!</p>"


@app.route("/start", methods=["POST"])
def start():
    gameId = uuid.uuid4()
    if not (players := request.json.get("player_names")):
        return {'message': 'Cannot start game. Need player names.'}

    game = ra.RaGame(
        player_names=data["player_names"],
        outfile=f"./games/{gameId}/history.txt"
    )
    game.init_game()
    _GAMES[gameId] = game

    return {
        'gameId': gameId,
        'gameState': str(game.game_state),
    }


@app.route("/delete", methods=["POST"])
def delete():
    if not (gameId := request.json.get('gameId')):
        return {'messsage': 'No game with id {gameId} found.'}

    del _GAMES[gameId]

    return {
        'message': f'Deleted game: {gameId}',
    }


@app.route("/action", methods=["POST"])
def action():
    if not (gameId := requests.json.get('gameId')):
        return {'message' : f'Cannot act on non-existing game: {gameId}'}

    if not (action := request.json.get("command")):
        return { 'message': 'No action' }
    action = ra.parse_action(action)
    if isinstance(action, str):
        return { 'message' : f'Unrecognized action: {action}' }

    game = _GAMES[gameId]
    if game.game_state.is_game_ended():
        return { 'message' : f'Game {gameId} has ended. '}
    
    
    legal_actions = game.get_possible_actions()
    if not legal_actions:
        return { 'message': 'Internal Error: No valid actions. '}
    t = game.execute_action(action, legal_actions)
    with open(game.outfile, "a+") as outfile:
        if action == gi.DRAW:
            outfile.write(f"{gi.DRAW_OPTIONS[0]} {t}\n")
        else:
            outfile.write(f"{action}\n")
    
    return {
        'data': request.json.get("command"),
        'gameState': str(game.game_state),
    }
