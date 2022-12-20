# from game import info as gi
# from game import state as gs
from game import state as gs
from game import ra

import argparse
from datetime import datetime

from typing import List

AI_PLAYER_NAME = 'AI_PLAYER'
OUTFILE_FOLDER_NAME: str = "move_histories"
DEFAULT_OUTFILE_PREFIX: str = "move_history"


def make_first_move_ai(game_state: gs.GameState) -> int:
    legal_actions = ra.get_possible_actions(game_state)
    assert legal_actions is not None, "legal actions is None, but shouldn't be"
    assert len(legal_actions) > 0, "no legal actions"
    return legal_actions[0]


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Ra Game Instance for a single-player game against an AI')

    # parser.add_argument('--num_players', '-n', type=int, default=2,
    #                     help='number of players in the game')

    parser.add_argument('--player1', '--p1', default="Player 1",
                        help="optional argument for player 1's name")
    # parser.add_argument('--player2', '--p2', default="Player 2",
    #                     help="optional argument for player 2's name")
    # parser.add_argument('--player3', '--p3', default="Player 3",
    #                     help="optional argument for player 3's name")
    # parser.add_argument('--player4', '--p4', default="Player 4",
    #                     help="optional argument for player 4's name")
    # parser.add_argument('--player5', '--p5', default="Player 5",
    #                     help="optional argument for player 5's name")

    parser.add_argument('--infile', '-i', default=None,
                        help='An optional argument to read game history'
                        ' from.')

    default_outfile_name = DEFAULT_OUTFILE_PREFIX + "_" + \
        datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + '.txt'
    parser.add_argument('--outfile', '-o', default=default_outfile_name,
                        help='An optional argument to write game history to.'
                        f' Is written to the {OUTFILE_FOLDER_NAME} folder.')
    return parser.parse_args()


if __name__ == '__main__':
    args: argparse.Namespace = get_args()
    player_names: List[str] = [
        args.player1,
        AI_PLAYER_NAME
    ]

    game = ra.RaGame(
        player_names,
        move_history_file=args.infile,
        outfile=args.outfile,
        ai_player_action_functions={
            AI_PLAYER_NAME: make_first_move_ai
        })
    game.start_game()
