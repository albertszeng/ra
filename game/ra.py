import argparse
import os
import random
from datetime import datetime
from typing import (
    Callable,
    Final,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

from game import info as gi
from game import scoring_utils
from game import state as gs

OUTFILE_FOLDER_NAME: str = "move_histories"
DEFAULT_OUTFILE_PREFIX: str = "move_history"


def parse_action(action: str) -> int:
    action_lower = action.lower()

    # try to parse action
    for a, a_options, a_desc in gi.action_option_lst:
        if action_lower in a_options:
            return a

    # return unrecognized action
    return -1


class SerializedRaGame(TypedDict):
    """
    This is data-only (non-functionality) structure that encapsulates the
    entire state of a RaGame for display purposes.
    """

    # The players and their respective play-order.
    playerNames: List[str]
    gameLog: List[Union[Tuple[str, Optional[int]], int]]
    gameState: gs.SerializedGameState
    unrealizedPoints: Mapping[str, int]
    auctionTileValues: Mapping[str, int]


# Get the possible actions for a gamestate
def get_possible_actions(game_state: gs.GameState) -> Optional[List[int]]:  # noqa: C901
    """Returns a list of legal actions."""
    if game_state.is_game_ended():
        return None

    legal_actions = []

    if game_state.is_auction_started():  # if it is an auction
        # find max auction sun
        auction_suns = game_state.get_auction_suns()
        max_auction_sun = float("-inf")
        if len([el for el in auction_suns if el is not None]) > 0:
            max_auction_sun = max([el for el in auction_suns if el is not None])

        # add a legal action for every player sun greater than the max
        # bid sun
        current_player_usable_sun = game_state.get_current_player_usable_sun()
        possible_bid_actions = [gi.BID_1, gi.BID_2, gi.BID_3, gi.BID_4]
        for i in range(len(current_player_usable_sun)):
            if current_player_usable_sun[i] > max_auction_sun:
                legal_actions.append(possible_bid_actions[i])

        # if current player is not the auction starter or auction was
        # forced or someone else has bid, then player can pass
        currPlayer = game_state.get_current_player()
        if (
            currPlayer != game_state.get_auction_start_player()
            or game_state.auction_was_forced()
            or game_state.get_num_auction_suns() > 0
        ):
            legal_actions.append(gi.BID_NOTHING)

    else:  # if it is not an auction
        # if disaster must be resolved
        if (
            game_state.get_num_mons_to_discard() > 0
            or game_state.get_num_civs_to_discard() > 0
        ):

            player = game_state.get_auction_winning_player()
            assert player is not None
            winning_player_collection = game_state.get_player_collection(player)

            # if there are civilizations to be discarded
            if game_state.get_num_civs_to_discard() > 0:
                possible_discards = [
                    gi.DISCARD_ASTR,
                    gi.DISCARD_AGR,
                    gi.DISCARD_WRI,
                    gi.DISCARD_REL,
                    gi.DISCARD_ART,
                ]
                # the number of civilization tiles
                for i in range(gi.NUM_CIVS):
                    if winning_player_collection[gi.STARTING_INDEX_OF_CIVS + i] > 0:
                        legal_actions.append(possible_discards[i])

            # if there are monuments to be discarded
            elif game_state.get_num_mons_to_discard() > 0:
                possible_discards = [
                    gi.DISCARD_FORT,
                    gi.DISCARD_OBEL,
                    gi.DISCARD_PAL,
                    gi.DISCARD_PYR,
                    gi.DISCARD_TEM,
                    gi.DISCARD_STAT,
                    gi.DISCARD_STE,
                    gi.DISCARD_SPH,
                ]
                # the number of civilization tiles
                for i in range(gi.NUM_MONUMENTS):
                    if (
                        winning_player_collection[gi.STARTING_INDEX_OF_MONUMENTS + i]
                        > 0
                    ):
                        legal_actions.append(possible_discards[i])

            # this should never be reached
            else:
                raise Exception(
                    "Error getting possible actions for disaster " "resolution"
                )

        # if no disaster to resolve
        else:
            # add start auction option
            legal_actions.append(gi.AUCTION)

            num_auction_tiles = game_state.get_num_auction_tiles()
            max_auction_tiles = game_state.get_max_auction_tiles()
            if num_auction_tiles < max_auction_tiles:
                # add draw option if auction tiles not full
                legal_actions.append(gi.DRAW)

                # if golden god exists, add god options for each auction
                # tile
                players = game_state.get_current_player_collection()
                if players[gi.INDEX_OF_GOD] > 0:
                    possible_takes = [
                        gi.GOD_1,
                        gi.GOD_2,
                        gi.GOD_3,
                        gi.GOD_4,
                        gi.GOD_5,
                        gi.GOD_6,
                        gi.GOD_7,
                        gi.GOD_8,
                    ]

                    auction_tiles = game_state.get_auction_tiles()
                    for i in range(num_auction_tiles):
                        if not gi.index_is_disaster(auction_tiles[i]):
                            legal_actions.append(possible_takes[i])

    return sorted(legal_actions)


def execute_action_internal(  # noqa: C901
    game_state: gs.GameState,
    action: int,
    legal_actions: Optional[Iterable[int]] = None,
    tile_to_draw: Optional[int] = None,
) -> Optional[int]:
    """
    Execute an action given it is valid for the provided game state.
    Assumes the action is made by the current player.

    Returns:
        The tile drawn if action is draw.
    """

    def execute_god(n: int) -> None:
        """Use god tile on the nth auction tile."""

        tile = game_state.remove_auction_tile(n)
        game_state.give_tiles_to_player(game_state.get_current_player(), [tile])
        game_state.remove_single_tiles_from_current_player([gi.INDEX_OF_GOD])
        game_state.advance_current_player()

    def end_round(game_state: gs.GameState) -> None:
        """Ends the round and transitions to the next one if necessary."""
        # clear auction tiles
        game_state.clear_auction_tiles()

        # clear auction suns and mark auction as over (in case it was started)
        game_state.end_auction()

        # reset num ras in current round
        game_state.reset_num_ras_this_round()

        # do round scoring each player
        scoring_utils.base_round_scoring(game_state.player_states)

        for player_state in game_state.player_states:
            # remove temporary tiles from each player
            player_state.remove_all_tiles_by_index(
                gi.list_of_temporary_collectible_indexes()
            )

            # reset usability of the suns
            player_state.make_all_suns_usable()

        if game_state.is_final_round():
            # if final round, do final scoring
            scoring_utils.final_round_scoring(game_state.player_states)

            # mark that the game has ended
            game_state.set_game_ended()

            return

        # reset passed players
        game_state.reset_active_players()

        # advance start player to the next player
        game_state.advance_current_player()

        # advance round number
        game_state.increase_round_number()

        return

    def mark_player_passed_if_no_disasters(auction_winning_player: int) -> None:
        """Mark a player passed and end round if no disasters."""

        # mark player passed if no disasters must be resolved
        if not game_state.disasters_must_be_resolved():
            if len(game_state.get_player_usable_sun(auction_winning_player)) == 0:
                game_state.mark_player_passed(auction_winning_player)

            # if all playesr passed, end the round
            if game_state.are_all_players_passed():
                end_round(game_state)

    def handle_auction_end() -> None:
        """
        Give auction tiles to the winning bidder or discard them if no
        winner assumes all players have bid already
        """
        auction_suns = game_state.get_auction_suns()
        max_sun = None
        if len([el for el in auction_suns if el is not None]) > 0:
            max_sun = max([el for el in auction_suns if el is not None])

        # if no suns were bid and the auction tiles are full, clear
        # the tiles
        if max_sun is None:
            if game_state.get_num_auction_tiles() == game_state.get_max_auction_tiles():
                game_state.clear_auction_tiles()

        # if a sun was bid, give auction tiles to the winner
        else:
            winning_player = auction_suns.index(max_sun)

            # swap out winning player's auctioned sun with the center sun
            game_state.exchange_sun(
                winning_player, max_sun, game_state.get_center_sun()
            )
            game_state.set_center_sun(max_sun)

            # give auction tiles to the winner
            auction_tiles = game_state.get_auction_tiles()
            game_state.clear_auction_tiles()
            game_state.give_tiles_to_player(
                winning_player,
                [tile for tile in auction_tiles if gi.index_is_collectible(tile)],
            )

            winning_player_collection = game_state.get_player_collection(winning_player)

            # resolve pharoah disasters
            num_phars_to_discard = gi.NUM_DISCARDS_PER_DISASTER * len(
                [tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_PHAR]
            )
            if num_phars_to_discard > 0:
                num_phars_owned = winning_player_collection[gi.INDEX_OF_PHAR]
                num_phars_to_discard = min(num_phars_to_discard, num_phars_owned)
                game_state.remove_single_tiles_from_player(
                    [gi.INDEX_OF_PHAR] * num_phars_to_discard, winning_player
                )

            # resolve nile disasters
            num_niles_to_discard = gi.NUM_DISCARDS_PER_DISASTER * len(
                [tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_NILE]
            )
            if num_niles_to_discard > 0:
                num_floods_owned = winning_player_collection[gi.INDEX_OF_FLOOD]
                num_niles_owned = winning_player_collection[gi.INDEX_OF_NILE]

                num_floods_to_discard = min(num_floods_owned, num_niles_to_discard)
                num_niles_to_discard = min(
                    num_niles_to_discard - num_floods_to_discard, num_niles_owned
                )

                game_state.remove_single_tiles_from_player(
                    [gi.INDEX_OF_FLOOD] * num_floods_to_discard
                    + [gi.INDEX_OF_NILE] * num_niles_to_discard,
                    winning_player,
                )

            # resolve civ disasters
            num_civs_to_discard = gi.NUM_DISCARDS_PER_DISASTER * len(
                [tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_CIV]
            )
            if num_civs_to_discard > 0:
                num_civs_owned = sum(
                    gi.get_civs_from_collection(winning_player_collection)
                )
                if num_civs_owned <= num_civs_to_discard:
                    game_state.remove_all_tiles_by_index_from_player(
                        range(
                            gi.STARTING_INDEX_OF_CIVS,
                            gi.STARTING_INDEX_OF_CIVS + gi.NUM_CIVS,
                        ),
                        winning_player,
                    )
                else:
                    game_state.set_num_civs_to_discard(num_civs_to_discard)
                    game_state.set_auction_winning_player(winning_player)

            # resolve monument disasters
            num_mons_to_discard = gi.NUM_DISCARDS_PER_DISASTER * len(
                [tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_MON]
            )
            if num_mons_to_discard > 0:
                num_mons_owned = sum(
                    gi.get_monuments_from_collection(winning_player_collection)
                )
                if num_mons_owned <= num_mons_to_discard:
                    game_state.remove_all_tiles_by_index_from_player(
                        range(
                            gi.STARTING_INDEX_OF_MONUMENTS,
                            gi.STARTING_INDEX_OF_MONUMENTS + gi.NUM_MONUMENTS,
                        ),
                        winning_player,
                    )
                else:
                    game_state.set_num_mons_to_discard(num_mons_to_discard)
                    game_state.set_auction_winning_player(winning_player)

            mark_player_passed_if_no_disasters(winning_player)

        # clear auction suns and mark auction as over
        game_state.end_auction()

        # if it's the final round and all playesr are passed
        if game_state.is_final_round() and game_state.are_all_players_passed():
            end_round(game_state)
        # else if no disasters to be resolved, advance current player
        elif not game_state.disasters_must_be_resolved():
            game_state.advance_current_player()
        # else, that means there IS a disaster to be resolved, so set current
        # player to auction winner to resolve
        else:
            game_state.set_current_player(game_state.get_auction_winning_player())

    def execute_bid(n: int) -> None:
        """Put the nth lowest sun up for auction."""
        sun_to_bid = game_state.get_current_player_usable_sun()[n]
        game_state.add_auction_sun(game_state.get_current_player(), sun_to_bid)

        if game_state.get_current_player() == game_state.get_auction_start_player():
            handle_auction_end()
        else:
            game_state.advance_current_player()

    def execute_civ_discard(index_to_discard: int, log: bool = True) -> None:
        """Executes single discard for resolving civ. disasters."""
        game_state.remove_single_tiles_from_player(
            [index_to_discard],
            game_state.get_auction_winning_player(),
            log=log,
        )
        game_state.decrement_num_civs_to_discard()
        mark_player_passed_if_no_disasters(game_state.get_auction_winning_player())

        # if no disasters to be resolved, resume play from after
        # auction starter
        if not game_state.disasters_must_be_resolved():
            game_state.set_current_player(game_state.get_auction_start_player())
            game_state.advance_current_player()

    def execute_monument_discard(index_to_discard: int, log: bool = True) -> None:
        """Executes a single discard for resolving monument disasters."""
        game_state.remove_single_tiles_from_player(
            [index_to_discard],
            game_state.get_auction_winning_player(),
            log=log,
        )
        game_state.decrement_num_mons_to_discard()
        mark_player_passed_if_no_disasters(game_state.get_auction_winning_player())

        # if no disasters to be resolved, resume play from after
        # auction starter
        if not game_state.disasters_must_be_resolved():
            game_state.set_current_player(game_state.get_auction_start_player())
            game_state.advance_current_player()

    if legal_actions is None:
        legal_actions = get_possible_actions(game_state)
        assert (
            legal_actions is not None
        ), "cannot execute action because no legal actions"

    if action not in legal_actions:
        raise Exception(
            f"Cannot execute non-legal action '{action}'. "
            f"Legal actions: '{legal_actions}'"
        )

    if action == gi.DRAW:
        tile = game_state.draw_tile(tile=tile_to_draw)
        assert tile is not None

        # if tile is ra, start auction (or end the round)
        if tile == gi.INDEX_OF_RA:
            game_state.increase_num_ras_this_round()

            # if this is the last ra, end the round
            if game_state.get_num_ras_per_round() == game_state.get_current_num_ras():
                end_round(game_state)
                return tile
            else:
                game_state.start_auction(True, game_state.get_current_player())
                game_state.advance_current_player()

        # otherwise, add tile to auction tiles
        else:
            game_state.add_tile_to_auction_tiles(tile)
            game_state.advance_current_player()

        return tile

    elif action == gi.AUCTION:
        was_forced = (
            game_state.get_num_auction_tiles() == game_state.get_max_auction_tiles()
        )
        game_state.start_auction(was_forced, game_state.get_current_player())
        game_state.advance_current_player()

    elif action == gi.GOD_1:
        execute_god(0)
    elif action == gi.GOD_2:
        execute_god(1)
    elif action == gi.GOD_3:
        execute_god(2)
    elif action == gi.GOD_4:
        execute_god(3)
    elif action == gi.GOD_5:
        execute_god(4)
    elif action == gi.GOD_6:
        execute_god(5)
    elif action == gi.GOD_7:
        execute_god(6)
    elif action == gi.GOD_8:
        execute_god(7)

    elif action == gi.BID_1:
        execute_bid(0)
    elif action == gi.BID_2:
        execute_bid(1)
    elif action == gi.BID_3:
        execute_bid(2)
    elif action == gi.BID_4:
        execute_bid(3)

    elif action == gi.BID_NOTHING:
        if game_state.get_current_player() == game_state.get_auction_start_player():
            handle_auction_end()
        else:
            game_state.advance_current_player()

    elif action == gi.DISCARD_ASTR:
        execute_civ_discard(gi.INDEX_OF_ASTR)
    elif action == gi.DISCARD_AGR:
        execute_civ_discard(gi.INDEX_OF_AGR)
    elif action == gi.DISCARD_WRI:
        execute_civ_discard(gi.INDEX_OF_WRI)
    elif action == gi.DISCARD_REL:
        execute_civ_discard(gi.INDEX_OF_REL)
    elif action == gi.DISCARD_ART:
        execute_civ_discard(gi.INDEX_OF_ART)
    elif action == gi.DISCARD_FORT:
        execute_monument_discard(gi.INDEX_OF_FORT)
    elif action == gi.DISCARD_OBEL:
        execute_monument_discard(gi.INDEX_OF_OBEL)
    elif action == gi.DISCARD_PAL:
        execute_monument_discard(gi.INDEX_OF_PAL)
    elif action == gi.DISCARD_PYR:
        execute_monument_discard(gi.INDEX_OF_PYR)
    elif action == gi.DISCARD_TEM:
        execute_monument_discard(gi.INDEX_OF_TEM)
    elif action == gi.DISCARD_STAT:
        execute_monument_discard(gi.INDEX_OF_STAT)
    elif action == gi.DISCARD_STE:
        execute_monument_discard(gi.INDEX_OF_STE)
    elif action == gi.DISCARD_SPH:
        execute_monument_discard(gi.INDEX_OF_SPH)


class RaGame:
    """
    Core logic for a game of Ra. Essentially just a class that allows the  game
    to be played.
    """

    num_players: int
    outfile: Optional[str]
    move_history_file: Optional[str]
    player_names: List[str]
    game_state: gs.GameState
    logged_moves: List[Union[Tuple[str, Optional[int]], int]]
    MAX_ACTION_ATTEMPTS: Final[int] = 10

    def __init__(
        self,
        player_names: List[str],
        randomize_play_order: bool = True,
        outfile: Optional[str] = None,
        move_history_file: Optional[str] = None,
        # dict mapping player-name to ai_function
        ai_player_action_functions: Optional[
            Mapping[str, Callable[[gs.GameState], int]]
        ] = None,
    ) -> None:
        self.num_players = len(player_names)
        # Initialize empty before loading history.
        self.logged_moves = []
        if not self.is_valid_num_players(self.num_players):
            raise ValueError("Invalid number of players")
        self.player_names = player_names

        # Verify AI action functions dict has valid player names
        self.ai_player_action_functions: Mapping[
            str, Callable[[gs.GameState], int]
        ] = {}
        if ai_player_action_functions is not None:
            self.ai_player_action_functions = ai_player_action_functions
        for player_name in self.ai_player_action_functions.keys():
            assertMsg = f"Player name '{player_name}' was provided in \
                'ai_player_action_functions', but not in 'player_names'"
            assert player_name in self.player_names, assertMsg

        self.outfile = f"{OUTFILE_FOLDER_NAME}/{outfile}" if outfile else None
        if self.outfile:
            if not os.path.exists(OUTFILE_FOLDER_NAME):
                os.makedirs(OUTFILE_FOLDER_NAME)
        self.move_history_file = move_history_file
        if self.move_history_file is not None:
            with open(self.move_history_file, "r") as f:
                self.player_names = [name.rstrip() for name in f.readline().split(" ")]
        elif randomize_play_order:
            # Only randomize play order if no move history provided
            random.shuffle(self.player_names)

        self.game_state = gs.GameState(self.player_names)

    def serialize(self) -> SerializedRaGame:
        return SerializedRaGame(
            playerNames=self.player_names,
            gameState=self.game_state.serialize(),
            gameLog=self.logged_moves,
            unrealizedPoints=scoring_utils.calculate_unrealized_points(
                self.game_state.player_states, self.game_state.is_final_round()
            ),
            auctionTileValues=scoring_utils.calculate_value_of_auction_tiles(
                self.game_state.get_auction_tiles(), self.game_state.player_states
            ),
        )

    def is_valid_num_players(self, num_players: int) -> bool:
        return num_players >= gi.MIN_NUM_PLAYERS and num_players <= gi.MAX_NUM_PLAYERS

    def write_player_names_to_outfile(self) -> None:
        """Write player names to the outfile, overwriting if necessary."""
        if not self.outfile:
            return

        with open(self.outfile, "w+") as outfile:
            # write the player names to the outfile
            outfile.write(f"{' '.join(self.player_names)}\n")

    def write_tile_draw_order_to_outfile(self) -> None:
        """Write the tile bag's draw order to the outfile. Appends to file."""
        if not self.outfile:
            return

        with open(self.outfile, "a+") as outfile:
            draw_order = self.game_state.get_tile_bag().get_draw_order()
            outfile.write(f"{' '.join([str(tile) for tile in draw_order])}\n")

    def write_pregame_info_to_outfile(self) -> None:
        """Writes player names and draw order to the outfile."""
        self.write_player_names_to_outfile()
        self.write_tile_draw_order_to_outfile()

    def get_action_prompt(self, legal_actions: List[int]) -> str:
        prompt = "User Action: "

        possible_actions_lst = [
            gi.action_option_lst[action][2] for action in legal_actions
        ]
        possible_actions_str = "\n    ".join(
            [f"{i}: {action}" for i, action in enumerate(possible_actions_lst)]
        )
        prompt = f"""Possible actions:
    {possible_actions_str}

        User Action: """

        return prompt

    # get an action from a human user
    def get_action_from_user(self, game_state: gs.GameState) -> int:
        legal_actions = get_possible_actions(game_state)
        assertMsg = "cannot get action from user because no legal actions"
        assert legal_actions is not None, assertMsg

        prompt = self.get_action_prompt(legal_actions)
        action = input(prompt)

        return parse_action(action)

    # Fetch the function that should make the current player's action
    def get_action_function(self) -> Callable[[gs.GameState], int]:
        # Use AI function if provided
        current_player_name = self.game_state.get_current_player_name()
        if current_player_name in self.ai_player_action_functions:
            return self.ai_player_action_functions[current_player_name]

        # If no AI function, ask user for input
        return self.get_action_from_user

    def get_action(
        self,
        legal_actions: List[int],
        action_making_func: Optional[Callable[[gs.GameState], int]] = None,
        log: bool = True,
    ) -> int:
        """
        Continually try to get an action until a legal action is given
        an action-making function can be given to get an action
        """
        for _i in range(RaGame.MAX_ACTION_ATTEMPTS):
            # get an action
            action_function = self.get_action_function()
            action = action_function(self.game_state)

            # return action if it is legal
            if action in legal_actions:
                return action
            else:
                if log:
                    print(f"Invalid action given: {action}\n")
        raise Exception(
            "Unable to get legal action after " f"{RaGame.MAX_ACTION_ATTEMPTS} attempts"
        )

    def execute_action(
        self,
        action: int,
        legal_actions: Optional[Iterable[int]] = None,
        tile_to_draw: Optional[int] = None,
    ) -> Optional[int]:
        """
        Execute an action for the current game state.
        """
        t = execute_action_internal(
            self.game_state, action, legal_actions, tile_to_draw
        )
        if action == gi.DRAW:
            self.logged_moves.append((gi.DRAW_OPTIONS[0], t))
            return t
        else:
            self.logged_moves.append(action)

    def play(self) -> None:
        """Play the game and log action history to the outfile."""

        def run() -> Iterator[Tuple[int, Optional[int]]]:
            while not self.game_state.is_game_ended():
                self.game_state.print_game_state()
                legal_actions = get_possible_actions(self.game_state)
                assert legal_actions is not None, "Game has not ended."
                action = self.get_action(legal_actions)
                print("executing action:", gi.ACTION_MAPPING[action])
                t = self.execute_action(action, legal_actions)
                yield action, t

            # Print player scores once game ends
            self.game_state.print_player_scores()
            return

        if not self.outfile:
            [_ for _ in run()]
            return

        with open(self.outfile, "a+") as outfile:
            for action, t in run():
                if action == gi.DRAW:
                    outfile.write(f"{gi.DRAW_OPTIONS[0]} {t}\n")
                else:
                    outfile.write(f"{action}\n")

    def load_actions(self, action_lst: Iterable[List[str]]) -> None:
        """
        Execute a list of actions. draw actions must have a specified tile
        to draw each action is a string lst of length 1 or 2.

        NOTE: Assumes that the tileBag draw order has already been set
        to the proper order, so it does NOT explicitly draw a tile from
        the bag.
        """
        self.write_pregame_info_to_outfile()

        def loader() -> Iterator[str]:
            for action in action_lst:
                legal_actions = get_possible_actions(self.game_state)
                # TODO(zeng): Maybe crashing is a bit harsh. Consider ignoring.
                assert legal_actions is not None

                # if action is not to draw
                if len(action) == 1:
                    self.execute_action(int(action[0]), legal_actions)
                    yield f"{action[0].rstrip()}\n"

                # if action is to draw
                elif len(action) == 2:
                    tile_to_be_drawn = int(action[1])
                    tile_actually_drawn = self.execute_action(
                        int(action[0]), legal_actions
                    )
                    assert (
                        tile_to_be_drawn == tile_actually_drawn
                    ), f"tile to be drawn {tile_to_be_drawn} does not match \
                    tile actually drawn {tile_actually_drawn}"
                    yield f"{gi.DRAW_OPTIONS[0]} {tile_actually_drawn}\n"

                # invalid action given
                else:
                    raise ValueError(f"Cannot load invalid action {action}")

        if not self.outfile:
            [_ for _ in loader()]
            return

        with open(self.outfile, "a+") as outfile:
            [outfile.write(line) for line in loader()]

    def load_actions_from_infile(self, infile: str) -> None:
        """Execute a list of actions from an infile.

        The format of the infile should be the same as is produced
        when playing.
        """
        with open(infile, "r") as f:
            file_lines = [action.split(" ") for action in f.readlines()]

            tile_bag_draw_order = file_lines[1]
            self.game_state.get_tile_bag()._set_draw_order(
                [int(tile) for tile in tile_bag_draw_order]
            )

            action_lst = file_lines[2:]
            self.load_actions(action_lst)

    def init_game(self) -> None:
        if self.move_history_file is not None:
            self.load_actions_from_infile(self.move_history_file)
        else:
            self.write_pregame_info_to_outfile()

    def start_game(self) -> None:
        """Function to call to start the game.

        It is only valid if the game has not been played yet.
        """
        self.init_game()
        self.play()

    def print_player_scores(self) -> None:
        self.game_state.print_player_scores()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ra Game Instance")

    parser.add_argument(
        "--num_players", "-n", type=int, default=2, help="number of players in the game"
    )

    parser.add_argument(
        "--player1",
        "--p1",
        default="Player_1",
        help="optional argument for player 1's name",
    )
    parser.add_argument(
        "--player2",
        "--p2",
        default="Player_2",
        help="optional argument for player 2's name",
    )
    parser.add_argument(
        "--player3",
        "--p3",
        default="Player_3",
        help="optional argument for player 3's name",
    )
    parser.add_argument(
        "--player4",
        "--p4",
        default="Player_4",
        help="optional argument for player 4's name",
    )
    parser.add_argument(
        "--player5",
        "--p5",
        default="Player_5",
        help="optional argument for player 5's name",
    )

    parser.add_argument(
        "--infile",
        "-i",
        default=None,
        help="An optional argument to read game history" " from.",
    )

    default_outfile_name = (
        DEFAULT_OUTFILE_PREFIX
        + "_"
        + datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        + ".txt"
    )
    parser.add_argument(
        "--outfile",
        "-o",
        default=default_outfile_name,
        help="An optional argument to write game history to."
        f" Is written to the {OUTFILE_FOLDER_NAME} folder.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args: argparse.Namespace = get_args()
    player_names: List[str] = [
        args.player1,
        args.player2,
        args.player3,
        args.player4,
        args.player5,
    ][: args.num_players]

    game = RaGame(player_names, move_history_file=args.infile, outfile=args.outfile)
    game.start_game()
