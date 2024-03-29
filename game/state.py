import logging
import random
import textwrap
from typing import Dict, Iterable, List, Optional, Sequence, TypedDict, cast

from game import info as gi

# Gamestate class and helper classes


class TileBag:
    """Holds all tiles currently available for draw."""

    __slots__ = ("bag", "num_tiles_left", "draw_order", "_draw_order_hash")

    # keeps track of how many of each tile are left
    bag: List[int]
    # total number of tiles left
    num_tiles_left: int
    # the order that tiles will be drawn, unless a specific tile is requested
    # to be drawn
    draw_order: List[int]
    _draw_order_hash: int

    def __init__(self, draw_order: Optional[List[int]] = None) -> None:
        if draw_order is None:
            draw_order = []
            for i, tile in enumerate(gi.TILE_INFO):
                draw_order += [i] * gi.tile_starting_num(tile)
            random.shuffle(draw_order)

        self._set_draw_order(draw_order)

    @classmethod
    def shallow(cls) -> "TileBag":
        """Returns a deep copy with some non-used values missing."""
        return cls.__new__(cls)

    def _set_draw_order(self, draw_order: List[int]) -> None:
        """
        Set the draw order of the tile bag (and consequently, the bag contents too).
        """
        self.draw_order = draw_order
        self.num_tiles_left = len(draw_order)
        self.bag = [0] * gi.NUM_TILE_TYPES
        for tile_index in draw_order:
            self.bag[tile_index] += 1

        self._draw_order_hash = hash(tuple(draw_order))

    def __key(self) -> tuple[int, int]:
        return (self._draw_order_hash, self.num_tiles_left)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: "TileBag") -> bool:
        if isinstance(other, TileBag):
            return self.__key() == other.__key()
        return NotImplemented

    def draw_tile(self, tile: Optional[int] = None, log: bool = False) -> Optional[int]:
        """Remove a "random" tile for the bag. The tile draw order is randomly
        determined when the TileBag class is instantiated. If a specific tile is
        to be drawn, it will take a random occurrence of it from the bag.

        Args:
            tile - if specified, remove the tile at this index.
            log - Enable aggressive logging.

        Returns:
            The index of the removed tile.
        """
        if self.num_tiles_left < 1:
            if log:
                raise Exception("Bag is empty. Unable to draw tile...")
            return None

        # if no specific tile specified, draw the next one in the draw order
        if tile is None:
            return self.draw_tile_from_index(0)

        # if a tile is specified to be drawn, draw it if possible
        if self.bag[tile] <= 0:
            raise ValueError(f"Bag does not contain tile {tile}")

        occurrence_to_be_drawn = random.randint(1, self.bag[tile])
        self.remove_nth_tile_from_draw_order(tile, occurrence_to_be_drawn)
        return tile

    def get_bag_contents(self) -> Sequence[int]:
        return self.bag

    def get_num_tiles_left(self) -> int:
        return self.num_tiles_left

    def get_draw_order(self) -> Sequence[int]:
        """
        Return the order of tiles that will be drawn.
        """
        return self.draw_order

    def set_next_tile_to_be_drawn(self, tile: int) -> int:
        """
        Sets "tile" as the next tile to be drawn. Returns what the next draw
        would have been otherwise.

        Internally, this swaps the next tile to be drawn with the first occurence
        of "tile" in the draw order.
        """
        assert (
            tile in self.draw_order
        ), f"Cannot set {tile} to be next draw because it is not in the tile bag"

        # If next draw is equal to tile, then just put it back
        if self.draw_order[0] == tile:
            return tile

        next_draw = self.draw_order.pop(0)
        first_occurrence_of_tile = self.draw_order.index(tile)
        self.draw_order.remove(tile)
        self.draw_order.insert(first_occurrence_of_tile, next_draw)
        self.draw_order.insert(0, tile)
        return next_draw

    def print_contents_of_bag(self) -> None:
        print(self)

    def __str__(self) -> str:
        val = "Bag Contents:\n"
        for i in range(len(self.bag)):
            val += f"{gi.index_to_tile_name(i)}: {self.bag[i]} remaining "
            val += f"({gi.index_to_starting_num(i)} initially)\n"
        return val

    def draw_tile_from_index(self, i: int) -> int:
        """
        Draw the tile at index i.
        """
        assert (
            i < self.num_tiles_left
        ), f"Cannot draw tile {i} from draw order because there aren't that \
        many tiles left."
        assert i >= 0, "Cannot draw negative tile from tile bag."
        assert (
            self.num_tiles_left > 0
        ), "Cannot draw tile from tile bag because there are no tiles left. "

        tile_drawn = self.draw_order[-self.num_tiles_left + i]
        self.num_tiles_left -= 1
        self.bag[tile_drawn] -= 1
        return tile_drawn

    def remove_nth_tile_from_draw_order(
        self, tile_index: int, nth_occurrence: int
    ) -> int:
        """
        Removes the nth occurrence of tile "tile_index" from the tile bag's draw order.
        Throws an exception if there are not that many occurrences found.

        nth_occurence is 1-indexed.
        """
        assert (
            nth_occurrence > 0
        ), f"Cannot remove the occurrence {nth_occurrence}. Must be > 0."

        occurrences_found = 0
        for i in range(self.num_tiles_left):
            if self.draw_order[i] == tile_index:
                occurrences_found += 1
                if occurrences_found == nth_occurrence:
                    return self.draw_tile_from_index(i)

        raise Exception(
            f"Could not remove the {nth_occurrence} of tile index {tile_index} \
            from tile bag"
        )


class SerializedPlayerState(TypedDict):
    """A data-only representation of the current player state."""

    # The tiles the player currently has in his collection.
    collection: List[gi.TileTypeInfo]
    # The current point total of the player.
    points: int
    # The full name of the player.
    playerName: str
    # The list of sun the player can bid.
    usableSun: List[int]
    # The List of sun the player has previously bid.
    unusableSun: List[int]


class PlayerState:
    __slots__ = (
        "collection",
        "points",
        "player_name",
        "player_idx",
        "usable_sun",
        "unusable_sun",
    )

    collection: List[int]
    points: int
    player_name: str
    player_idx: int
    usable_sun: List[int]
    unusable_sun: List[int]

    def __init__(
        self,
        player_name: str,
        player_idx: int,
        starting_sun: List[int],
        starting_points: int = gi.STARTING_PLAYER_POINTS,
    ) -> None:
        self.collection = [0] * gi.NUM_COLLECTIBLE_TILE_TYPES
        self.points = starting_points
        self.player_name = player_name
        self.player_idx = player_idx
        self.usable_sun = starting_sun[:]
        self.usable_sun.sort()
        self.unusable_sun = []

    @classmethod
    def shallow(cls) -> "PlayerState":
        return cls.__new__(cls)

    def __key(self) -> tuple[int, ...]:
        return (
            hash(tuple(self.collection)),
            self.points,
            hash(tuple(self.usable_sun)),
            hash(tuple(self.unusable_sun)),
        )

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: "PlayerState") -> bool:
        if isinstance(other, PlayerState):
            return self.__key() == other.__key()
        return NotImplemented

    def serialize(self) -> SerializedPlayerState:
        return SerializedPlayerState(
            playerName=self.player_name,
            points=self.points,
            usableSun=self.usable_sun,
            unusableSun=self.unusable_sun,
            collection=[
                gi.index_to_tile(idx)
                for idx, count in enumerate(self.collection)
                for _ in range(count)
            ],
        )

    def add_tiles(self, lst_of_indexes: Iterable[int]) -> None:
        """Add a list of tile indexes to the player's collection"""
        for index in lst_of_indexes:
            self.collection[index] += 1

    def remove_single_tiles_by_index(
        self, lst_of_indexes: Iterable[int], log: bool = False
    ) -> None:
        """Remove a list of tile indexes from the player's collection."""
        for index in lst_of_indexes:
            if self.collection[index] > 0:
                if log:
                    logging.info(
                        f"Removing a single tile \
                        {gi.index_to_tile_name(index)} from player \
                        {self.player_name}"
                    )
                self.collection[index] -= 1
            else:
                if log:
                    logging.info(
                        f"Player {self.player_name} does not have tile "
                        f"{gi.index_to_tile_name(index)}"
                    )

    def remove_all_tiles_by_index(
        self, lst_of_indexes: Iterable[int], log: bool = False
    ) -> None:
        """Remove all tiles whose indexes are in lst_of_indexes."""
        for index in lst_of_indexes:
            if log:
                logging.info(
                    f"Clearing all tile {gi.index_to_tile_name(index)} "
                    f"from player {self.player_name}"
                )
            self.collection[index] = 0

    def exchange_sun(self, sun_to_give: int, sun_to_receive: int) -> None:
        """Give away a sun and receive another sun back."""
        self.usable_sun.remove(sun_to_give)
        self.unusable_sun.append(sun_to_receive)
        self.unusable_sun.sort()

    def make_all_suns_usable(self) -> None:
        self.usable_sun += self.unusable_sun
        self.unusable_sun = []
        self.usable_sun.sort()

    def add_points(self, points_to_add: int) -> None:
        """Add a specified number of points to player (can be negative)."""
        self.points += points_to_add

    def get_player_points(self) -> int:
        return self.points

    def get_player_collection(self) -> Sequence[int]:
        return self.collection

    def get_player_name(self) -> str:
        return self.player_name

    def get_player_idx(self) -> int:
        return self.player_idx

    def get_usable_sun(self) -> Sequence[int]:
        return self.usable_sun

    def get_unusable_sun(self) -> Sequence[int]:
        return self.unusable_sun

    def get_all_sun(self) -> List[int]:
        return self.usable_sun + self.unusable_sun

    def collections_as_str(self, verbose: bool = False) -> str:
        val = f"Tiles of {self.player_name}:\n"
        for i in range(len(self.collection)):
            if self.collection[i] > 0:
                val += f"{gi.index_to_tile_name(i)}: {self.collection[i]} \
                collected\n"
        return val

    def sun_as_str(self) -> str:
        return textwrap.dedent(
            f"""
            Sun of {self.player_name}
            Usable Sun: {self.usable_sun}
            Unusable Sun: {self.unusable_sun}
            """
        )

    def __str__(self) -> str:
        return self.player_state_as_str()

    def player_state_as_str(
        self, include_name: bool = True, verbose: bool = False
    ) -> str:
        val = f"Player: {self.player_name}\n" if include_name else ""
        val += f"{self.sun_as_str()}\n"
        val += f"{self.collections_as_str(verbose)}\n"
        val += f"Points: {self.points}\n"
        return val

    def print_player_state(
        self, print_name: bool = True, verbose: bool = False
    ) -> None:
        print(self.player_state_as_str(print_name, verbose))


class SerializedGameState(TypedDict):
    """Fully summarizes in a data-only format the current GameState."""

    # Total number of rounds to play.
    totalRounds: int
    # Total number of Ra tiles per round.
    numRasPerRound: int
    # Total number of active players.
    numPlayers: int
    # maximum number of tiles up for auction at once
    maxAuctionTiles: int

    # The current round.
    currentRound: int
    # If true, the player[i] is active.
    activePlayers: List[bool]
    # The number of Ra tiles revealed so far.
    numRasThisRound: int
    # The value of the sun tile in the center.
    centerSun: int
    # The tiles currently up for auction.
    auctionTiles: List[gi.TileTypeInfo]
    # For each player i, how much sun have they bid if any.
    auctionSuns: List[Optional[int]]
    # Whether or not an action has started.
    auctionStarted: bool
    # The index of the player that started the auction, if any.
    auctionStartPlayer: Optional[int]
    # The index of the current player.
    currentPlayer: int
    # The index of the player that won the auction, if any.
    auctionWinningPlayer: Optional[int]

    # The serialized player states.
    playerStates: List[SerializedPlayerState]

    # True if the game is over.
    gameEnded: bool


class GameState:
    __slots__ = (
        "total_rounds",
        "num_ras_per_round",
        "num_players",
        "max_auction_tiles",
        "tile_bag",
        "current_round",
        "active_players",
        "num_ras_this_round",
        "center_sun",
        "auction_tiles",
        "auction_suns",
        "auction_forced",
        "auction_started",
        "auction_start_player",
        "current_player",
        "num_mons_to_discard",
        "num_civs_to_discard",
        "auction_winning_player",
        "player_states",
        "player_names",
        "game_ended",
    )
    total_rounds: int
    num_ras_per_round: int
    num_players: int
    max_auction_tiles: int

    # current game state variables
    tile_bag: TileBag
    current_round: int
    active_players: List[bool]
    num_ras_this_round: int
    center_sun: int
    auction_tiles: List[int]
    # what suns players have bid
    auction_suns: List[Optional[int]]
    auction_started: bool
    auction_forced: bool
    auction_start_player: Optional[int]
    current_player: int
    num_mons_to_discard: int
    num_civs_to_discard: int
    auction_winning_player: Optional[int]

    # player states
    player_states: List[PlayerState]
    player_names: List[str]

    game_ended: bool

    def __init__(self, player_names: List[str]) -> None:
        num_players = len(player_names)
        if num_players > gi.MAX_NUM_PLAYERS or num_players < gi.MIN_NUM_PLAYERS:
            raise Exception(
                f"Invalid game state. Cannot have {num_players} \
                players"
            )
        assert len(player_names) == len(
            set(player_names)
        ), "Cannot have duplicate player names"

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
        # what suns players have bid
        self.auction_suns = cast(List[Optional[int]], [None] * self.num_players)
        self.auction_started = False
        self.auction_forced = False
        self.auction_start_player = None  # player that started the auction
        self.current_player = 0
        self.num_mons_to_discard = 0
        self.num_civs_to_discard = 0
        # used only for resolving disasters
        self.auction_winning_player = None

        # player states
        self.player_states = []
        starting_sun_sets = gi.STARTING_SUN[num_players]
        tmp_sets = starting_sun_sets[1:]
        random.shuffle(tmp_sets)
        starting_sun_sets[1:] = tmp_sets
        for idx in range(num_players):
            self.player_states.append(
                PlayerState(player_names[idx], idx, starting_sun_sets[idx])
            )
        self.player_names = [
            player_state.get_player_name() for player_state in self.player_states
        ]

        self.game_ended = False

    @classmethod
    def shallow(cls) -> "GameState":
        return cls.__new__(cls)

    def __key(
        self,
    ) -> tuple[int, ...]:
        return (
            self.total_rounds,
            self.num_ras_this_round,
            self.num_players,
            self.max_auction_tiles,
            hash(self.tile_bag),
            self.current_round,
            hash(tuple(self.active_players)),
            self.center_sun,
            hash(tuple(sorted(self.auction_tiles))),
            hash(tuple(self.auction_suns)),
            hash(self.auction_started),
            hash(self.auction_forced),
            hash(self.auction_start_player),
            self.current_player,
            self.num_mons_to_discard,
            self.num_civs_to_discard,
            hash(self.auction_winning_player),
            hash(tuple(hash(player) for player in self.player_states)),
            hash(self.game_ended),
        )

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: "GameState") -> bool:
        if isinstance(other, GameState):
            return self.__key() == other.__key()
        return NotImplemented

    def serialize(self) -> SerializedGameState:
        return SerializedGameState(
            totalRounds=self.total_rounds,
            numRasPerRound=self.num_ras_per_round,
            numPlayers=self.num_players,
            maxAuctionTiles=self.max_auction_tiles,
            currentRound=self.current_round,
            activePlayers=self.active_players,
            numRasThisRound=self.num_ras_this_round,
            centerSun=self.center_sun,
            auctionTiles=[gi.index_to_tile(idx) for idx in self.auction_tiles],
            auctionSuns=self.auction_suns,
            auctionStarted=self.auction_started,
            auctionStartPlayer=self.auction_start_player,
            currentPlayer=self.current_player,
            auctionWinningPlayer=self.auction_winning_player,
            playerStates=[state.serialize() for state in self.player_states],
            gameEnded=self.game_ended,
        )

    def increase_round_number(self) -> None:
        """Increase the round number by 1 if it's not the last round."""
        if self.current_round >= self.total_rounds:
            raise Exception(
                f"Cannot advance round beyond \
                {self.current_round}"
            )
        self.current_round += 1

    def draw_tile(self, tile: Optional[int] = None, log: bool = False) -> Optional[int]:
        """Draw a tile from the game bag and return the tile index."""
        return self.tile_bag.draw_tile(tile=tile, log=log)

    def increase_num_ras_this_round(self) -> None:
        """Increase the number of ras drawn this round by 1 if valid."""
        if self.num_ras_this_round >= self.num_ras_per_round:
            raise Exception(
                f"Cannot increase num ras \
                beyond {self.num_ras_this_round}"
            )
        self.num_ras_this_round += 1

    def reset_num_ras_this_round(self) -> None:
        """Reset the number of ras drawn this round to 0."""
        self.num_ras_this_round = 0

    def add_tile_to_auction_tiles(self, tile_index: int) -> int:
        """Add a tile to the list of auction tiles.

        Return: the number of auction tiles
        """
        if len(self.auction_tiles) >= self.max_auction_tiles:
            raise Exception(
                f"There are already {len(self.auction_tiles)} \
                auction tiles. Cannot add another."
            )
        self.auction_tiles.append(tile_index)
        return len(self.auction_tiles)

    def remove_auction_tile(self, tile_position_index: int) -> int:
        """Remove an auction tile and return tile_index that was removed."""
        if tile_position_index >= len(self.auction_tiles):
            raise Exception(
                f"Cannot remove tile position index {tile_position_index}. "
                + f"There are only {len(self.auction_tiles)} auction tiles."
            )

        return self.auction_tiles.pop(tile_position_index)

    def clear_auction_tiles(self) -> None:
        """Throw away all tiles up for auction."""
        self.auction_tiles = []

    def give_tiles_to_player(self, player_index: int, tile_list: Iterable[int]) -> None:
        """Give tiles to a player."""
        self.player_states[player_index].add_tiles(tile_list)

    def remove_single_tiles_from_current_player(
        self, tile_indexes: Iterable[int], log: bool = False
    ) -> None:
        """Remove a list of tiles from the current player."""
        self.player_states[self.current_player].remove_single_tiles_by_index(
            tile_indexes, log=log
        )

    def remove_single_tiles_from_player(
        self, tile_indexes: Iterable[int], player_index: int, log: bool = False
    ) -> None:
        """Remove a list of tiles from the specified player."""
        self.player_states[player_index].remove_single_tiles_by_index(
            tile_indexes, log=log
        )

    def remove_all_tiles_by_index_from_current_player(
        self, tile_indexes: Iterable[int], log: bool = False
    ) -> None:
        """Remove all tiles in the list of indexes from the current player."""
        self.player_states[self.current_player].remove_all_tiles_by_index(
            tile_indexes, log=log
        )

    def remove_all_tiles_by_index_from_player(
        self, tile_indexes: Iterable[int], player_index: int, log: bool = False
    ) -> None:
        """Remove all tiles in the list of indexes from the current player."""
        self.player_states[player_index].remove_all_tiles_by_index(
            tile_indexes, log=log
        )

    def set_auction_winning_player(self, winning_player: int) -> None:
        """Set who won an auction and must now resolve disasters."""
        self.auction_winning_player = winning_player

    def clear_auction_winning_player(self) -> None:
        """Remove the auction winning player."""
        self.auction_winning_player = None

    def set_current_player(self, new_player_index: int) -> None:
        """Change the current player to a specifc player."""
        if new_player_index < 0 or new_player_index >= self.num_players:
            raise Exception("Invalid player given to set_current_player")
        self.current_player = new_player_index

    def mark_player_passed(self, player_index: int) -> None:
        """Mark that a player has no more usable sun."""
        self.active_players[player_index] = False

    def reset_active_players(self) -> None:
        """Mark all players active."""
        for i in range(len(self.active_players)):
            self.active_players[i] = True

    def advance_current_player(self, skip_passed_players: bool = True) -> None:
        """Increases self.current_player to the next player."""
        if skip_passed_players:
            nextPlayer = self.get_next_active_player()
            assert nextPlayer is not None
            self.set_current_player(nextPlayer)
        else:
            self.set_current_player((self.current_player + 1) % self.num_players)

    def set_auction_start_player(self, player: int) -> None:
        """Mark that someone has started an auction."""
        self.auction_start_player = player

    # # removes who has started the auction
    # (generally after the auction is done)
    # def remove_auction_start_player(self):
    #     self.auction_start_player = None

    def start_auction(self, forced: bool, start_player: int) -> None:
        """Mark that an auction has started."""
        self.auction_started = True
        self.auction_forced = forced
        self.auction_start_player = start_player

    def add_auction_sun(self, player: int, sun: int) -> None:
        """Mark a player's bid."""
        if not self.auction_started:
            raise Exception("Cannot add auction sun if auction not started")

        if self.auction_suns[player] is not None:
            raise Exception(
                f"Player {player} already has bid {self.auction_suns[player]}"
            )
        self.auction_suns[player] = sun

    def clear_auction_suns(self) -> None:
        self.auction_suns = cast(List[Optional[int]], [None] * self.num_players)

    def end_auction(self) -> None:
        """End the auction and clear the suns that were bid."""
        self.clear_auction_suns()
        self.auction_started = False

    def exchange_sun(self, player: int, auctioned_sun: int, center_sun: int) -> None:
        """Take auctioned_sun from player and give center_sun in exchange."""
        self.player_states[player].exchange_sun(auctioned_sun, center_sun)

    def set_center_sun(self, new_sun: int) -> None:
        self.center_sun = new_sun

    def add_points_for_player(self, player: int, points: int) -> None:
        """Add points for a player (points can be negative)."""
        self.player_states[player].add_points(points)

    def set_num_civs_to_discard(self, num_to_discard: int) -> None:
        """Set how many civilizations must be discarded due to a disaster."""
        self.num_civs_to_discard = num_to_discard

    def set_num_mons_to_discard(self, num_to_discard: int) -> None:
        """Set how many monuments must be discarded due to a disaster."""
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

    # checking functions

    def is_final_round(self) -> bool:
        return self.current_round == self.total_rounds

    def is_player_active(self, player_index: int) -> bool:
        return self.active_players[player_index]

    def are_all_players_passed(self) -> bool:
        return not any(self.active_players)

    def current_player_has_god(self) -> bool:
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

    # getter functions

    # get the next player who still has sun

    def get_next_active_player(self) -> Optional[int]:
        for i in range(1, self.num_players + 1):
            curr_player_to_check = (self.current_player + i) % self.num_players
            if self.active_players[curr_player_to_check]:
                return curr_player_to_check
        return None
        # raise Exception("Could not get next active player")

    def get_total_rounds(self) -> int:
        return self.total_rounds

    def get_current_round(self) -> int:
        return self.current_round

    def get_num_players(self) -> int:
        return self.num_players

    def get_tile_bag(self) -> TileBag:
        return self.tile_bag  # does this need to be deep copied?

    def get_num_tiles_left(self) -> int:
        return self.tile_bag.get_num_tiles_left()

    def get_tile_bag_contents(self) -> Sequence[int]:
        return self.tile_bag.get_bag_contents()

    def get_current_num_ras(self) -> int:
        return self.num_ras_this_round

    def get_num_ras_per_round(self) -> int:
        return self.num_ras_per_round

    # def get_current_player_state(self):
    #   return copy.deepcopy(self.player_states[self.current_player])

    # def get_player_states(self):
    #   return self.player_states  # does this need to be deep copied?

    def get_current_player_collection(self) -> Sequence[int]:
        return self.player_states[self.current_player].get_player_collection()

    def get_player_collection(self, player_index: int) -> Sequence[int]:
        return self.player_states[player_index].get_player_collection()

    def get_max_auction_tiles(self) -> int:
        return self.max_auction_tiles

    def get_auction_tiles(self) -> Sequence[int]:
        return self.auction_tiles

    def get_num_auction_tiles(self) -> int:
        return len(self.auction_tiles)

    def get_center_sun(self) -> int:
        return self.center_sun

    def get_auction_suns(self) -> Sequence[Optional[int]]:
        return self.auction_suns

    def get_num_auction_suns(self) -> int:
        return sum([1 for sun in self.auction_suns if sun is not None])

    def get_current_player(self) -> int:
        return self.current_player

    def get_player_names(self) -> Sequence[str]:
        return self.player_names

    def get_current_player_name(self) -> str:
        return self.player_names[self.current_player]

    def get_current_player_usable_sun(self) -> Sequence[int]:
        return self.player_states[self.current_player].get_usable_sun()

    def get_player_usable_sun(self, player_index: int) -> Sequence[int]:
        return self.player_states[player_index].get_usable_sun()

    def get_auction_start_player(self) -> int:
        if self.auction_start_player is None:
            raise ValueError("No auction run.")
        return self.auction_start_player

    def get_num_mons_to_discard(self) -> int:
        return self.num_mons_to_discard

    def get_num_civs_to_discard(self) -> int:
        return self.num_civs_to_discard

    def get_auction_winning_player(self) -> int:
        if self.auction_winning_player is None:
            raise ValueError("No auction run.")
        return self.auction_winning_player

    def get_all_player_points(self) -> Dict[str, int]:
        return {
            player_state.get_player_name(): player_state.get_player_points()
            for player_state in self.player_states
        }

    # logging functions

    def print_tile_bag(self) -> None:
        self.tile_bag.print_contents_of_bag()

    def print_player_scores(self, verbose: bool = False) -> None:
        print(self.player_states_as_str(verbose))

    def player_scores_as_str(self) -> str:
        val = "Scores: \n"
        for state in self.player_states:
            val += f"    {state.get_player_name()}:     \
                {state.get_player_points()} points\n"
        return val

    def player_states_as_str(self, verbose: bool = False) -> str:
        val = ""
        for state in self.player_states:
            val += f"{state.player_state_as_str(verbose=verbose)}\n"
        return val

    def auction_tiles_as_str(self) -> str:
        val = "Auction Tiles: \n"
        for tile_index in self.auction_tiles:
            val += f"    {gi.index_to_tile_name(tile_index)}\n"
        return val

    def __str__(self) -> str:
        val = "-------------------------------------------------\n"

        val += f"{self.player_states_as_str()}\n"

        val += f"Round: {self.current_round}\n"
        val += f"Num Ras This Round: {self.num_ras_this_round}\n"
        val += f"Center Sun: {self.center_sun}\n"
        val += f"{self.player_scores_as_str()}\n"
        val += f"{self.auction_tiles_as_str()}\n"
        if self.is_auction_started():
            val += f"Auctioned Suns: {self.auction_suns}\n"

        val += "\nPlayer To Move: " f"{self.player_names[self.current_player]}\n"

        return val

    def print_game_state(self) -> None:
        print(self)


# gs = GameState(2)
# for _i in range(5):
#   tile_index = gs.draw_tile()
#   print(gi.index_to_tile_name(tile_index))
#   if gi.index_is_collectible(tile_index):
#       gs.add_tile_to_auction_tiles(tile_index)
# gs.print_auction_tiles()

# gs.print_player_state(0)
# gs.player_wins_auction(0, 3)
# gs.print_player_state(0)
