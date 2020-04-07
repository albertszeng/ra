import argparse
import numpy as np
import random
import game_info as gi
import game_state as gs

DEFAULT_OUTFILE = "move_history.txt"


class RaGame():
    def __init__(self, player_names, randomize_play_order = True, outfile = "history.txt", move_history_file = None):
        self.num_players = len(player_names)
        if not self.is_valid_num_players(self.num_players):
            print("Invalid number of players. Cannot create game instance...")
            raise ValueError("Invalid number of players")

        self.outfile = outfile
        self.move_history_file = move_history_file
        self.player_names = player_names

        if self.move_history_file is not None:
            with open(self.move_history_file, "r") as f:
                self.player_names = [name.rstrip() for name in f.readline().split(" ")]
        elif randomize_play_order:
            random.shuffle(self.player_names)

        self.game_state = gs.GameState(self.player_names)

        self.MAX_ACTION_ATTEMPTS = 10  # max num times we try to get an action


    def is_valid_num_players(self, num_players):
        return num_players >= gi.MIN_NUM_PLAYERS and num_players <= gi.MAX_NUM_PLAYERS


    # write player names to the outfile, overwriting if necessary
    def write_player_names_to_outfile(self):
        with open(self.outfile, "w+") as outfile:
            # write the player names to the outfile
            outfile.write(f"{' '.join(self.player_names)}\n")


    # gives points to each player based on their tiles
    def base_round_scoring(self, player_states):
        def least_and_most_num_pharoahs(player_states):
            least_so_far = float("inf")
            most_so_far = float("-inf")
            for player_state in player_states:
                least_so_far = min(least_so_far, player_state.collection[gi.INDEX_OF_PHAR])
                most_so_far = max(most_so_far, player_state.collection[gi.INDEX_OF_PHAR])
            return least_so_far, most_so_far

        def num_distinct_civs(player_state):
            collection_of_civs = gi.get_civs_from_collection(player_state.collection)
            return len([n for n in collection_of_civs if n > 0])

        for player_state in player_states:
            # golden gods
            player_state.add_points(player_state.collection[gi.INDEX_OF_GOD] * gi.POINTS_PER_GOD)

            # gold
            player_state.add_points(player_state.collection[gi.INDEX_OF_GOLD] * gi.POINTS_PER_GOLD)

            # pharoahs
            least_num_pharoahs, most_num_pharoahs = least_and_most_num_pharoahs(player_states)
            if player_state.collection[gi.INDEX_OF_PHAR] == least_num_pharoahs:
                player_state.add_points(gi.POINTS_FOR_LEAST_PHAR)
            if player_state.collection[gi.INDEX_OF_PHAR] == most_num_pharoahs:
                player_state.add_points(gi.POINTS_FOR_MOST_PHAR)

            # niles and floods
            if player_state.collection[gi.INDEX_OF_FLOOD] > 0:
                player_state.add_points(
                    player_state.collection[gi.INDEX_OF_NILE] + player_state.collection[gi.INDEX_OF_FLOOD]
                )

            # civilizations
            player_state.add_points(gi.POINTS_FOR_CIVS[num_distinct_civs(player_state)])
                

    # gives points to each player based on final round scoring
    def final_round_scoring(self, player_states):
        def sum_suns(player_state):
            return sum(player_state.get_all_sun())

        def least_and_most_suns(player_states):
            least_so_far = float("inf")
            most_so_far = float("-inf")
            for player_state in player_states:
                least_so_far = min(least_so_far, sum_suns(player_state))
                most_so_far = max(most_so_far, sum_suns(player_state))
            return least_so_far, most_so_far

        def monument_points(player_state):
            monument_points = 0
            # monument copies
            monument_collection = gi.get_monuments_from_collection(player_state.collection)
            for amount in monument_collection:
                monument_points += gi.POINTS_FOR_MON_DEPTH[amount]

            # distinct monuments
            num_distinct = len([n for n in monument_collection if n > 0])
            monument_points += gi.POINTS_FOR_MON_BREADTH[num_distinct]
            
            return monument_points

        for player_state in player_states:
            # monuments
            player_state.add_points(monument_points(player_state))

            # suns
            least_suns, most_suns = least_and_most_suns(player_states)
            if sum_suns(player_state) == least_suns:
                player_state.add_points(gi.POINTS_FOR_LEAST_SUN)
            if sum_suns(player_state) == most_suns:
                player_state.add_points(gi.POINTS_FOR_MOST_SUN)


    # ends the round and transitions to the next one if necessary
    def end_round(self):
        # clear auction tiles
        self.game_state.clear_auction_tiles()

        # clear auction suns and mark auction as over (in case it was started)
        self.game_state.end_auction()

        # reset num ras in current round
        self.game_state.reset_num_ras_this_round()

        # do round scoring each player
        self.base_round_scoring(self.game_state.player_states)

        for player_state in self.game_state.player_states:
            # remove temporary tiles from each player
            player_state.remove_all_tiles_by_index(
                gi.list_of_temporary_collectible_indexes()
            )

            # reset usability of the suns
            player_state.make_all_suns_usable()

        if self.game_state.is_final_round():
            # if final round, do final scoring
            self.final_round_scoring(self.game_state.player_states)

            # mark that the game has ended
            self.game_state.set_game_ended()

            # if game ended, show results
            self.game_state.print_player_scores()

            return

        # reset passed players
        self.game_state.reset_active_players()

        # advance start player to the next player
        self.game_state.advance_current_player()

        # advance round number
        self.game_state.increase_round_number()

        return


    # returns a list of legal actions
    def get_possible_actions(self):
        if self.game_state.is_game_ended():
            return None

        legal_actions = []

        if self.game_state.is_auction_started():  # if it is an auction
            # find max auction sun
            auction_suns = self.game_state.get_auction_suns()
            max_auction_sun = float("-inf")
            if len([el for el in auction_suns if el is not None]) > 0:
                max_auction_sun = max([el for el in auction_suns if el is not None])

            # add a legal action for every player sun greater than the max bid sun
            current_player_usable_sun = self.game_state.get_current_player_usable_sun()
            possible_bid_actions = [gi.BID_1, gi.BID_2, gi.BID_3, gi.BID_4]
            for i in range(len(current_player_usable_sun)):
                if current_player_usable_sun[i] > max_auction_sun:
                    legal_actions.append(possible_bid_actions[i])

            # if current player is not the auction starter or auction was forced
            # or someone else has bid, then player can pass
            if (self.game_state.get_current_player() != self.game_state.get_auction_start_player() or 
                    self.game_state.auction_was_forced() or 
                    self.game_state.get_num_auction_suns() > 0):
                legal_actions.append(gi.BID_NOTHING)
        
        else:  # if it is not an auction
            # if disaster must be resolved
            if (self.game_state.get_num_mons_to_discard() > 0 or 
                    self.game_state.get_num_civs_to_discard() > 0):
                
                winning_player_collection = self.game_state.get_player_collection(
                    self.game_state.get_auction_winning_player()
                )

                # if there are civilizations to be discarded
                if self.game_state.get_num_civs_to_discard() > 0:  
                    possible_discards = [
                        gi.DISCARD_ASTR,
                        gi.DISCARD_AGR,
                        gi.DISCARD_WRI,
                        gi.DISCARD_REL,
                        gi.DISCARD_ART
                    ]
                    for i in range(gi.NUM_CIVS):  # the number of civilization tiles
                        if winning_player_collection[gi.STARTING_INDEX_OF_CIVS + i] > 0:
                            legal_actions.append(possible_discards[i])
                
                # if there are monuments to be discarded
                elif self.game_state.get_num_mons_to_discard() > 0:  
                    possible_discards = [
                        gi.DISCARD_FORT,
                        gi.DISCARD_OBEL,
                        gi.DISCARD_PAL,
                        gi.DISCARD_PYR,
                        gi.DISCARD_TEM,
                        gi.DISCARD_STAT,
                        gi.DISCARD_STE,
                        gi.DISCARD_SPH
                    ]
                    for i in range(gi.NUM_MONUMENTS):  # the number of civilization tiles
                        if winning_player_collection[gi.STARTING_INDEX_OF_MONUMENTS + i] > 0:
                            legal_actions.append(possible_discards[i])

                # this should never be reached
                else:
                    raise Exception("Error getting possible actions for disaster resolution")

            # if no disaster to resolve
            else:  
                # add start auction option
                legal_actions.append(gi.AUCTION)

                if self.game_state.get_num_auction_tiles() < self.game_state.get_max_auction_tiles():
                    # add draw option if auction tiles not full
                    legal_actions.append(gi.DRAW)

                    # if golden god exists, add god options for each auction tile
                    if self.game_state.get_current_player_collection()[gi.INDEX_OF_GOD] > 0:
                        possible_takes = [
                            gi.GOD_1, 
                            gi.GOD_2, 
                            gi.GOD_3, 
                            gi.GOD_4, 
                            gi.GOD_5, 
                            gi.GOD_6, 
                            gi.GOD_7, 
                            gi.GOD_8
                        ]

                        auction_tiles = self.game_state.get_auction_tiles()
                        for i in range(self.game_state.get_num_auction_tiles()):
                            if not gi.index_is_disaster(auction_tiles[i]):
                                legal_actions.append(possible_takes[i])
                    
        return sorted(legal_actions)


    # get an action from a human user
    def get_action_from_user(self, legal_actions, helpful_prompt = True):
        def parse_action(action : str):
            action_lower = action.lower()

            # try to parse action
            for a, a_options, a_desc in gi.action_option_lst:
                if action_lower in a_options:
                    return a

            # return unrecognized action
            return action_lower

        if legal_actions is None:
            legal_actions = self.get_possible_actions()

        prompt = "User Action: "
        if helpful_prompt:
            possible_actions_lst = [
                gi.action_option_lst[action][2] for action in legal_actions
            ]
            possible_actions_str = "\n\t".join(possible_actions_lst)
            prompt = f"Possible actions:\n\t{possible_actions_str}\n\nUser Action: "

        action = input(prompt)

        return parse_action(action)
        

    # continually try to get an action until a legal action is given
    # an action-making function can be given to get an action
    def get_action(self, legal_actions, action_making_func = None, log = True):
        for _i in range(self.MAX_ACTION_ATTEMPTS):
            # get an action
            action = None
            if action_making_func is not None:  # AI makes action
                action = action_making_func(self.game_state)
            else:  # human makes action
                action = self.get_action_from_user(legal_actions)

            # return action if it is legal
            if action in legal_actions:
                return action
            else:
                if log:
                    print(f"Invalid action given: {action}\n")
        raise Exception(f"Unable to get legal action after {self.MAX_ACTION_ATTEMPTS} attempts")


    # execute an action given it is valid for the current game state
    # assumes the action is made by the current player
    # returns the tile drawn if action is draw
    def execute_action(self, action, legal_actions, tile_to_draw = None):
        # use god tile on the nth auction tile 
        def execute_god(n):
            tile = self.game_state.remove_auction_tile(n)
            self.game_state.give_tiles_to_player(self.game_state.get_current_player(), [tile])
            self.game_state.remove_single_tiles_from_current_player([gi.INDEX_OF_GOD])
            self.game_state.advance_current_player()

        # mark a player passed and end round if no disasters need to be resolved
        def mark_player_passed_if_no_disasters(auction_winning_player):
            # mark player passed if no disasters must be resolved
            if not self.game_state.disasters_must_be_resolved():
                if len(self.game_state.get_player_usable_sun(auction_winning_player)) == 0:
                    self.game_state.mark_player_passed(auction_winning_player)

                # if all playesr passed, end the round
                if self.game_state.are_all_players_passed():
                    self.end_round()

        # give auction tiles to the winning bidder or discard them if no winner
        # assumes all players have bid already
        def handle_auction_end():
            auction_suns = self.game_state.get_auction_suns()
            max_sun = None
            if len([el for el in auction_suns if el is not None]) > 0:
                max_sun = max([el for el in auction_suns if el is not None])

            # if no suns were bid and the auction tiles are full, clear the tiles
            if max_sun is None:
                if self.game_state.get_num_auction_tiles() == self.game_state.get_max_auction_tiles():
                    self.game_state.clear_auction_tiles()

            # if a sun was bid, give auction tiles to the winner
            else:
                winning_player = auction_suns.index(max_sun)

                # swap out winning player's auctioned sun with the center sun
                self.game_state.exchange_sun(
                    winning_player, 
                    max_sun,
                    self.game_state.get_center_sun()
                )
                self.game_state.set_center_sun(max_sun)

                # give auction tiles to the winner
                auction_tiles = self.game_state.get_auction_tiles()
                self.game_state.clear_auction_tiles()
                self.game_state.give_tiles_to_player(
                    winning_player,
                    [tile for tile in auction_tiles if gi.index_is_collectible(tile)]
                )

                winning_player_collection = self.game_state.get_player_collection(winning_player)

                # resolve pharoah disasters
                num_phars_to_discard = gi.NUM_DISCARDS_PER_DISASTER \
                    * len([tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_PHAR])
                if num_phars_to_discard > 0:
                    num_phars_owned = winning_player_collection[gi.INDEX_OF_PHAR]
                    num_phars_to_discard = min(num_phars_to_discard, num_phars_owned)
                    self.game_state.remove_single_tiles_from_player(
                        [gi.INDEX_OF_PHAR] * num_phars_to_discard,
                        winning_player
                    )

                # resolve nile disasters
                num_niles_to_discard = gi.NUM_DISCARDS_PER_DISASTER \
                    * len([tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_NILE])
                if num_niles_to_discard > 0:
                    num_floods_owned = winning_player_collection[gi.INDEX_OF_FLOOD]
                    num_niles_owned = winning_player_collection[gi.INDEX_OF_NILE]

                    num_floods_to_discard = min(num_floods_owned, num_niles_to_discard)
                    num_niles_to_discard = min(num_niles_to_discard - num_floods_to_discard, num_niles_owned)

                    self.game_state.remove_single_tiles_from_player(
                        [gi.INDEX_OF_FLOOD] * num_floods_to_discard + [gi.INDEX_OF_NILE] * num_niles_to_discard,
                        winning_player
                    )

                # resolve civ disasters
                num_civs_to_discard = gi.NUM_DISCARDS_PER_DISASTER \
                    * len([tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_CIV])
                if num_civs_to_discard > 0:
                    num_civs_owned = sum(gi.get_civs_from_collection(winning_player_collection))
                    if num_civs_owned <= num_civs_to_discard:
                        self.game_state.remove_all_tiles_by_index_from_player(
                            range(gi.STARTING_INDEX_OF_CIVS, gi.STARTING_INDEX_OF_CIVS + gi.NUM_CIVS),
                            winning_player
                        )
                    else:
                        self.game_state.set_num_civs_to_discard(num_civs_to_discard)
                        self.game_state.set_auction_winning_player(winning_player)

                # resolve monument disasters
                num_mons_to_discard = gi.NUM_DISCARDS_PER_DISASTER \
                    * len([tile for tile in auction_tiles if tile == gi.INDEX_OF_DIS_MON])
                if num_mons_to_discard > 0:
                    num_mons_owned = sum(gi.get_monuments_from_collection(winning_player_collection))
                    if num_mons_owned <= num_mons_to_discard:
                        self.game_state.remove_all_tiles_by_index_from_player(
                            range(gi.STARTING_INDEX_OF_MONUMENTS, gi.STARTING_INDEX_OF_MONUMENTS + gi.NUM_MONS),
                            winning_player
                        )
                    else:
                        self.game_state.set_num_mons_to_discard(num_mons_to_discard)
                        self.game_state.set_auction_winning_player(winning_player)

                mark_player_passed_if_no_disasters(winning_player)
                
            # clear auction suns and mark auction as over
            self.game_state.end_auction()

            # if no disasters to be resolved, advance current player
            if not self.game_state.disasters_must_be_resolved():
                self.game_state.advance_current_player()
            else: # otherwise, set current player to auction winner to resolve
                self.game_state.set_current_player(self.game_state.get_auction_winning_player())

        # put the nth lowest sun up for auction
        def execute_bid(n):
            sun_to_bid = self.game_state.get_current_player_usable_sun()[n]
            self.game_state.add_auction_sun(self.game_state.get_current_player(), sun_to_bid)
            
            if self.game_state.get_current_player() == self.game_state.get_auction_start_player():
                handle_auction_end()
            else:
                self.game_state.advance_current_player() 

        # executes a single discard for resolving civilization disasters
        def execute_civ_discard(index_to_discard, log = True):
            self.game_state.remove_single_tiles_from_player(
                [index_to_discard], 
                self.game_state.get_auction_winning_player(),
                log = log
            )
            self.game_state.decrement_num_civs_to_discard()
            mark_player_passed_if_no_disasters(self.game_state.get_auction_winning_player())

            # if no disasters to be resolved, resume play from after auction starter
            if not self.game_state.disasters_must_be_resolved():
                self.game_state.set_current_player(
                    self.game_state.get_auction_start_player()
                )
                self.game_state.advance_current_player()

        # executes a single discard for resolving monument disasters
        def execute_monument_discard(index_to_discard, log = True):
            self.game_state.remove_single_tiles_from_player(
                [index_to_discard],
                self.game_state.get_auction_winning_player(), 
                log = log
            )
            self.game_state.decrement_num_mons_to_discard()
            mark_player_passed_if_no_disasters(self.game_state.get_auction_winning_player())

            # if no disasters to be resolved, resume play from after auction starter
            if not self.game_state.disasters_must_be_resolved():
                self.game_state.set_current_player(
                    self.game_state.get_auction_start_player()
                )
                self.game_state.advance_current_player()

        if action not in legal_actions:
            raise Exception(
                f"Cannot execute non-legal action '{action}'. Legal actions: '{legal_actions}'"
            )

        if action == gi.DRAW:
            tile = self.game_state.draw_tile(tile = tile_to_draw)

            # if tile is ra, start auction (or end the round)
            if tile == gi.INDEX_OF_RA:
                self.game_state.increase_num_ras_this_round()

                # if this is the last ra, end the round
                if self.game_state.get_num_ras_per_round() == self.game_state.get_current_num_ras():
                    self.end_round()
                    return tile
                else:
                    self.game_state.start_auction(True, self.game_state.get_current_player())

            # otherwise, add tile to auction tiles
            else:
                self.game_state.add_tile_to_auction_tiles(tile)

            self.game_state.advance_current_player()

            return tile

        elif action == gi.AUCTION:
            was_forced = (
                self.game_state.get_num_auction_tiles() == 
                self.game_state.get_max_auction_tiles()
            )
            self.game_state.start_auction(was_forced, self.game_state.get_current_player())
            self.game_state.advance_current_player()

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
            if self.game_state.get_current_player() == self.game_state.get_auction_start_player():
                handle_auction_end()
            else:
                self.game_state.advance_current_player() 

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


    # play the game and log action history to the outfile
    def play(self):
        with open(self.outfile, "a+") as outfile:
            while not self.game_state.is_game_ended():
                self.game_state.print_game_state()
                legal_actions = self.get_possible_actions()
                action = self.get_action(legal_actions)
                t = self.execute_action(action, legal_actions)

                if action == gi.DRAW:
                    outfile.write(f"{gi.DRAW_OPTIONS[0]} {t}\n")
                else:
                    outfile.write(f"{action}\n")


    # execute a list of actions. draw actions must have a specified tile to draw
    # each action is a string lst of length 1 or 2
    def load_actions(self, action_lst):
        self.write_player_names_to_outfile()

        with open(self.outfile, "a+") as outfile:
            for action in action_lst:
                legal_actions = self.get_possible_actions()

                # if action is not to draw
                if len(action) == 1:
                    self.execute_action(int(action[0]), legal_actions)
                    outfile.write(f"{action[0].rstrip()}\n")

                # if action is to draw
                elif len(action) == 2:
                    t = self.execute_action(
                        int(action[0]), legal_actions, tile_to_draw = int(action[1])
                    )
                    outfile.write(f"{gi.DRAW_OPTIONS[0]} {t}\n")

                # invalid action given
                else:
                    raise ValueError(f"Cannot load invalid action {action}")


    # execute a list of actions from an infile
    # the format of the infile should be the same as is produced when playing
    def load_actions_from_infile(self, infile):
        with open(infile, "r") as f:
            action_lst = [action.split(" ") for action in f.readlines()][1:]
        self.load_actions(action_lst)


    # function to call to start the game
    # is only valid if the game has not been played yet
    def start_game(self):
        if self.move_history_file is not None:
            self.load_actions_from_infile(self.move_history_file)
        else:
            self.write_player_names_to_outfile()

        self.play()


    def print_player_scores(self):
        self.game_state.print_player_scores()


def get_args():
    parser = argparse.ArgumentParser(description='Ra Game Instance')
    
    parser.add_argument('--num_players', '-n', type=int, default=2,
                        help='number of players in the game')

    parser.add_argument('--player1', '--p1', default="Player 1",
                        help="optional argument for player 1's name")
    parser.add_argument('--player2', '--p2', default="Player 2",
                        help="optional argument for player 2's name")
    parser.add_argument('--player3', '--p3', default="Player 3",
                        help="optional argument for player 3's name")
    parser.add_argument('--player4', '--p4', default="Player 4",
                        help="optional argument for player 4's name")
    parser.add_argument('--player5', '--p5', default="Player 5",
                        help="optional argument for player 5's name")
    
    parser.add_argument('--infile', '-i', default=None,
                        help='An optional argument to read game history from.')
    parser.add_argument('--outfile', '-o', default=DEFAULT_OUTFILE,
                        help='An optional argument to write game history to.')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    player_names = [
        args.player1, 
        args.player2, 
        args.player3, 
        args.player4, 
        args.player5
    ][:args.num_players]
    
    game = RaGame(
        player_names,
        move_history_file = args.infile,
        outfile = args.outfile)
    game.start_game()
