import copy
import random
import game_info as gi
from typing import Optional, Sized


### Gamestate class and helper classes 

class TileBag():
    def __init__(self) -> None:
        # keeps track of how many of each tile are left
        self.bag = [gi.tile_starting_num(tile) for tile in gi.TILE_INFO]

        # total number of tiles left
        self.num_tiles_left = gi.STARTING_NUM_TILES	

    # remove a random tile from self.bag and return its index
    # optionally specify what tile to draw
    def draw_tile(self, tile: Optional[int] = None, log: bool = True) -> Optional[int]:
        if self.num_tiles_left < 1:
            if log:
                raise Exception("Bag is empty. Unable to draw tile...")
            return None

        # if no specific tile specified, draw a random one
        if tile is None:
            tile_num = random.randint(1, self.num_tiles_left)
            for i in range(len(self.bag)):
                if tile_num <= self.bag[i]:
                    self.bag[i] -= 1
                    self.num_tiles_left -= 1
                    return i
                else:
                    tile_num -= self.bag[i]

            raise Exception("Error: could not draw random tile from bag...")

        # if a tile is specified to be drawn, draw it if possible
        else:
            if self.bag[tile] <= 0:
                raise ValueError(f"Bag does not contain tile {tile}")
            else:
                self.bag[tile] -= 1
                self.num_tiles_left -= 1
                return tile


    ### getter functions

    def get_bag_contents(self):
        return self.bag[:]

    def get_num_tiles_left(self):
        return self.num_tiles_left

    ### logging functions

    def print_contents_of_bag(self) -> None:
        print("Bag Contents:")
        for i in range(len(self.bag)):
            print(f"{gi.index_to_tile_name(i)}: {self.bag[i]} remaining "
                  f"({gi.index_to_starting_num(i)} initially)")


class PlayerState():
    def __init__(self, player_name, starting_sun, starting_points: int = gi.STARTING_PLAYER_POINTS) -> None:
        self.collection = [0] * gi.NUM_COLLECTIBLE_TILE_TYPES
        self.points = starting_points
        self.player_name = player_name
        self.usable_sun = starting_sun[:]
        self.usable_sun.sort()
        self.unusable_sun = []

    # add a list of tile indexes to the player's collection
    def add_tiles(self, lst_of_indexes) -> None:
        for index in lst_of_indexes:
            self.collection[index] += 1

    # remove a list of tile indexes from the player's collection
    def remove_single_tiles_by_index(self, lst_of_indexes, log: bool = True) -> None:
        for index in lst_of_indexes:
            if self.collection[index] > 0:
                if log:
                    print(f"Removing a single tile {gi.index_to_tile_name(index)} "
                          f"from player {self.player_name}")
                self.collection[index] -= 1
            else:
                if log:
                    print(f"Player {self.player_name} does not have tile "
                          f"{gi.index_to_tile_name(index)}")

    # remove all tiles whose indexes are in lst_of_indexes
    def remove_all_tiles_by_index(self, lst_of_indexes, log: bool = True) -> None:
        for index in lst_of_indexes:
            if log:
                print(f"Clearing all tile {gi.index_to_tile_name(index)} "
                      f"from player {self.player_name}")
            self.collection[index] = 0

    # give away a sun and receive another sun back
    def exchange_sun(self, sun_to_give, sun_to_receive) -> None:
        self.usable_sun.remove(sun_to_give)
        self.unusable_sun.append(sun_to_receive)
        self.unusable_sun.sort()

    def make_all_suns_usable(self) -> None:
        self.usable_sun += self.unusable_sun
        self.unusable_sun = []
        self.usable_sun.sort()

    # add a specified number of points for the player (can be negative)
    def add_points(self, points_to_add: int) -> None:
        self.points += points_to_add

    ### getter functions

    def get_player_points(self) -> int:
        return self.points

    def get_player_collection(self):
        return self.collection[:]

    def get_player_name(self):
        return self.player_name

    def get_usable_sun(self):
        return self.usable_sun[:]

    def get_unusable_sun(self):
        return self.unusable_sun[:]

    def get_all_sun(self):
        return self.usable_sun + self.unusable_sun

    ### logging functions

    def print_collection(self, verbose: bool = False) -> None:
        print(f"Tiles of {self.player_name}:")
        for i in range(len(self.collection)):
            if self.collection[i] > 0:
                print(f"{gi.index_to_tile_name(i)}: {self.collection[i]} collected")

    def print_usable_sun(self) -> None:
        print(f"Usable Sun: {self.usable_sun}")

    def print_unusable_sun(self) -> None:
        print(f"Unusable Sun: {self.unusable_sun}")

    def print_all_sun(self) -> None:
        print(f"Sun of {self.player_name}")
        self.print_usable_sun()
        self.print_unusable_sun()

    def print_player_state(self, print_name: bool = True, verbose: bool = False) -> None:
        if print_name:
            print("Player:", self.player_name)
        self.print_all_sun()
        self.print_collection(verbose = verbose)
        print("Points:", self.points)


class GameState():
    def __init__(self, player_names: Sized) -> None:
        num_players = len(player_names)
        if num_players > gi.MAX_NUM_PLAYERS or num_players < gi.MIN_NUM_PLAYERS:
            raise Exception(f"Invalid game state. Cannot have {num_players} players")

        # constant game state variables
        self.total_rounds = gi.NUM_ROUNDS
        self.num_ras_per_round = gi.NUM_RAS_PER_ROUND[num_players]
        self.num_players = num_players
        self.max_auction_tiles = gi.MAX_AUCTION_TILES
        
        # current game state variables
        self.tile_bag = TileBag()
        self.current_round = 1
        self.active_players = [True] * self.num_players  # players with sun still
        self.num_ras_this_round = 0
        self.center_sun = gi.STARTING_CENTER_SUN
        self.auction_tiles = []
        self.auction_suns = [None] * self.num_players  # what suns players have bid
        self.auction_started = False
        self.auction_forced = False
        self.auction_start_player = None  # player that started the auction
        self.current_player = 0 
        self.num_mons_to_discard = 0
        self.num_civs_to_discard = 0
        self.auction_winning_player = None  # used only for resolving disasters
        
        # player states
        self.player_states = []
        starting_sun_sets = gi.STARTING_SUN[num_players][:]
        tmp_sets = starting_sun_sets[1:]
        random.shuffle(tmp_sets)
        starting_sun_sets[1:] = tmp_sets
        for i in range(num_players):
            self.player_states.append(
                PlayerState(player_names[i], starting_sun_sets[i])
            )
        self.player_names = [player_state.get_player_name() for player_state in self.player_states]

        self.game_ended = False

    ### variable manipulation function

    # increase the round number by 1 if it's not the last round
    def increase_round_number(self) -> None:
        if self.current_round < self.total_rounds:
            self.current_round += 1
        else:
            raise Exception(f"Cannot advance round beyond {self.current_round}")

    # draw a tile from the game bag and return the tile index
    def draw_tile(self, tile: Optional[int] = None, log: bool = True) -> Optional[int]:
        return self.tile_bag.draw_tile(tile = tile, log = log)

    # increase the number of ras drawn this round by 1 if valid
    def increase_num_ras_this_round(self) -> None:
        if self.num_ras_this_round < self.num_ras_per_round:
            self.num_ras_this_round += 1
        else:
            raise Exception(f"Cannot increase num ras beyond {self.num_ras_this_round}")

    # reset the number of ras drawn this round to 0
    def reset_num_ras_this_round(self) -> None:
        self.num_ras_this_round = 0

    # add a tile to the list of auction tiles. return the number of auction tiles
    def add_tile_to_auction_tiles(self, tile_index) -> int:
        if len(self.auction_tiles) < self.max_auction_tiles:
            self.auction_tiles.append(tile_index)
            return len(self.auction_tiles)
        else:
            raise Exception(f"There are already {len(self.auction_tiles)} auction tiles. "
                            f"Cannot add another.")

    # remove an auction tile and return the tile_index that was removed
    def remove_auction_tile(self, tile_position_index):
        if tile_position_index >= len(self.auction_tiles):
            raise Exception(
                f"cannot remove tile position index {tile_position_index}. " +
                f"There are only {len(self.auction_tiles)} auction tiles."
            )

        return self.auction_tiles.pop(tile_position_index)

    # throw away all tiles up for auction
    def clear_auction_tiles(self) -> None:
        self.auction_tiles = []

    # give tiles to a player
    def give_tiles_to_player(self, player_index, tile_list) -> None:
        self.player_states[player_index].add_tiles(tile_list)

    # remove a list of tiles from the current player
    def remove_single_tiles_from_current_player(self, tile_indexes, log: bool = True) -> None:
        self.player_states[self.current_player].remove_single_tiles_by_index(
            tile_indexes, 
            log = log
        )

    # remove a list of tiles from the specified player
    def remove_single_tiles_from_player(self, tile_indexes, player_index, log: bool = True) -> None:
        self.player_states[player_index].remove_single_tiles_by_index(
            tile_indexes, 
            log = log
        )

    # remove all tiles in the list of indexes from the current player
    def remove_all_tiles_by_index_from_current_player(self, tile_indexes, log: bool = True) -> None:
        self.player_states[self.current_player].remove_all_tiles_by_index(
            tile_indexes,
            log = log
        )

    # remove all tiles in the list of indexes from the current player
    def remove_all_tiles_by_index_from_player(self, tile_indexes, player_index, log: bool = True) -> None:
        self.player_states[player_index].remove_all_tiles_by_index(
            tile_indexes,
            log = log
        )

    # set who won an auction and must now resolve disasters
    def set_auction_winning_player(self, winning_player) -> None:
        self.auction_winning_player = winning_player

    # remove the auction winning player
    def clear_auction_winning_player(self) -> None:
        self.auction_winning_player = None

    # change the current player to a specifc player
    def set_current_player(self, new_player_index: int) -> None:
        if new_player_index < 0 or new_player_index >= self.num_players:
            raise Exception("Invalid player given to set_current_player")
        self.current_player = new_player_index

    # mark that a player has no more usable sun
    def mark_player_passed(self, player_index) -> None:
        self.active_players[player_index] = False

    # mark all players active
    def reset_active_players(self) -> None:
        for i in range(len(self.active_players)):
            self.active_players[i] = True

    # increases self.current_player to the next player
    def advance_current_player(self, skip_passed_players: bool = True) -> None:
        if skip_passed_players:
            self.set_current_player(self.get_next_active_player())
        else:
            self.set_current_player((self.current_player + 1) % self.num_players)

    # mark that someone has started an auction
    def set_auction_start_player(self, player) -> None:
        self.auction_start_player = player

    # # removes who has started the auction (generally after the auction is done)
    # def remove_auction_start_player(self):
    #     self.auction_start_player = None

    # mark that an auction has started
    def start_auction(self, forced: bool, start_player) -> None:
        self.auction_started = True
        self.auction_forced = forced
        self.auction_start_player = start_player

    # mark a player's bid
    def add_auction_sun(self, player, sun) -> None:
        if not self.auction_started:
            raise Exception("Cannot add auction sun if auction not started")

        if self.auction_suns[player] is not None:
            raise Exception(
                f"Player {player} already has bid {self.auction_suns[player]}"
            )
        self.auction_suns[player] = sun

    def clear_auction_suns(self) -> None:
        self.auction_suns = [None] * self.num_players

    # end the auction and clear the suns that were bid
    def end_auction(self) -> None:
        self.clear_auction_suns()
        self.auction_started = False

    # take auctioned_sun from player and give the center_sun in exchange
    def exchange_sun(self, player, auctioned_sun, center_sun) -> None:
        self.player_states[player].exchange_sun(auctioned_sun, center_sun)

    def set_center_sun(self, new_sun) -> None:
        self.center_sun = new_sun

    # add points for a player (points can be negative)
    def add_points_for_player(self, player, points) -> None:
        self.player_states[player].add_points(points)

    # set how many civilizations must be discarded due to a disaster
    def set_num_civs_to_discard(self, num_to_discard: int) -> None:
        self.num_civs_to_discard = num_to_discard

    # set how many monuments must be discarded due to a disaster
    def set_num_mons_to_discard(self, num_to_discard: int) -> None:
        self.num_mons_to_discard = num_to_discard
    
    def decrement_num_civs_to_discard(self) -> None:
        self.num_civs_to_discard -= 1
        if self.num_civs_to_discard < 0:
            raise Exception("num_civs_to_discard cannot be negative")
        
    def decrement_num_mons_to_discard(self) -> None:
        self.num_mons_to_discard -= 1
        if self.num_mons_to_discard < 0:
            raise Exception("num_mons_to_discard cannot be negative")

    def set_game_ended(self) -> None:
        self.game_ended = True


    ### checking functions

    def is_final_round(self) -> bool:
        return self.current_round == self.total_rounds

    def is_player_active(self, player_index):
        return self.active_players[player_index]

    def are_all_players_passed(self) -> bool:
        return not any(self.active_players)

    def current_player_has_god(self):
        curr_player_state = self.player_states[self.current_player]
        player_collection = curr_player_state.get_player_collection()
        return player_collection[gi.INDEX_OF_GOD] > 0

    def is_auction_started(self) -> bool:
        return self.auction_started

    def auction_was_forced(self) -> bool:
        return self.auction_forced

    def is_game_ended(self) -> bool:
        return self.game_ended

    def disasters_must_be_resolved(self) -> bool:
        return self.num_mons_to_discard > 0 or self.num_civs_to_discard > 0


    ### getter functions

    # get the next player who still has sun
    def get_next_active_player(self) -> Optional[int]:
        for i in range(1, self.num_players + 1):
            curr_player_to_check = (self.current_player + i) % self.num_players
            if self.active_players[curr_player_to_check]:
                return curr_player_to_check
        return None
        # raise Exception("Could not get next active player")

    def get_total_rounds(self):
        return self.total_rounds

    def get_current_round(self) -> int:
        return self.current_round

    def get_num_players(self):
        return self.num_players

    def get_tile_bag(self) -> TileBag:
        return self.tile_bag  # does this need to be deep copied?

    def get_num_tiles_left(self):
        return self.tile_bag.get_num_tiles_left()

    def get_tile_bag_contents(self):
        return self.tile_bag.get_bag_contents()

    def get_current_num_ras(self) -> int:
        return self.num_ras_this_round

    def get_num_ras_per_round(self):
        return self.num_ras_per_round

    # def get_current_player_state(self):
    # 	return copy.deepcopy(self.player_states[self.current_player])

    # def get_player_states(self):
    # 	return self.player_states  # does this need to be deep copied?

    def get_current_player_collection(self):
        return self.player_states[self.current_player].get_player_collection()

    def get_player_collection(self, player_index):
        return self.player_states[player_index].get_player_collection()

    def get_max_auction_tiles(self):
        return self.max_auction_tiles

    def get_auction_tiles(self):
        return self.auction_tiles[:]

    def get_num_auction_tiles(self) -> int:
        return len(self.auction_tiles)

    def get_center_sun(self):
        return self.center_sun

    def get_auction_suns(self):
        return self.auction_suns[:]

    def get_num_auction_suns(self) -> int:
        return sum([1 for sun in self.auction_suns if sun is not None])

    def get_current_player(self) -> int:
        return self.current_player

    def get_current_player_usable_sun(self):
        return self.player_states[self.current_player].get_usable_sun()

    def get_player_usable_sun(self, player_index):
        return self.player_states[player_index].get_usable_sun()

    def get_auction_start_player(self):
        return self.auction_start_player

    def get_num_mons_to_discard(self) -> int:
        return self.num_mons_to_discard

    def get_num_civs_to_discard(self) -> int:
        return self.num_civs_to_discard

    def get_auction_winning_player(self):
        return self.auction_winning_player


    ### logging functions

    def print_tile_bag(self) -> None:
        self.tile_bag.print_contents_of_bag()

    def print_player_scores(self) -> None:
        print("Scores:")
        for state in self.player_states:
            print(f"\t{state.get_player_name()}: {state.get_player_points()} points")

    def print_player_state(self, player_index) -> None:
        self.player_states[player_index].print_player_state()

    def print_player_states(self, verbose: bool = False) -> None:
        for state in self.player_states:
            state.print_player_state(verbose = verbose)
            print("")

    def print_auction_tiles(self) -> None:
        print("Auction Tiles:")
        for tile_index in self.auction_tiles:
            print("\t", gi.index_to_tile_name(tile_index))

    def print_game_state(self) -> None:
        print("-------------------------------------------------")

        self.print_player_states()

        print("")

        print("Round:", self.current_round)
        print("Num Ras This Round:", self.num_ras_this_round)
        print("Center Sun:", self.center_sun)
        self.print_player_scores()
        self.print_auction_tiles()
        if self.is_auction_started():
            print("Auctioned Suns:", self.auction_suns)

        print("\nPlayer To Move:", self.player_names[self.current_player], "\n")


# gs = GameState(2)
# for _i in range(5):
# 	tile_index = gs.draw_tile()
# 	print(gi.index_to_tile_name(tile_index))
# 	if gi.index_is_collectible(tile_index):
# 		gs.add_tile_to_auction_tiles(tile_index)
# gs.print_auction_tiles()

# gs.print_player_state(0)
# gs.player_wins_auction(0, 3)
# gs.print_player_state(0)

