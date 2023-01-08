import enum
from typing import Dict, List, Mapping, Sequence, Tuple, TypedDict

# Game Constants

# most and least players allowed
MAX_NUM_PLAYERS: int = 5
MIN_NUM_PLAYERS: int = 2

# the sun that starts in the middle
STARTING_CENTER_SUN: int = 1

# (players in game: starting sun sets)
# assert that the first move goes to the player with the first set in each list
STARTING_SUN: Dict[int, List[List[int]]] = {
    2: [[2, 5, 6, 9], [3, 4, 7, 8]],
    3: [[2, 5, 8, 13], [3, 6, 9, 12], [4, 7, 10, 11]],
    4: [[2, 6, 13], [3, 7, 12], [4, 8, 11], [5, 9, 10]],
    5: [[2, 7, 16], [3, 8, 15], [4, 9, 14], [5, 10, 13], [6, 11, 12]],
}

# num of players: number of ra tiles per round
NUM_RAS_PER_ROUND: Dict[int, int] = {2: 6, 3: 8, 4: 9, 5: 10}

# number of points each player starts with
STARTING_PLAYER_POINTS: int = 10

# number of rounds in the game
NUM_ROUNDS: int = 3

# maximum number of tiles up for auction at once
MAX_AUCTION_TILES: int = 8

# number of tiles to discard per disaster
NUM_DISCARDS_PER_DISASTER: int = 2

# Indexes of each tile type in the tile bag's list
INDEX_OF_GOD: int = 0
INDEX_OF_GOLD: int = 1
INDEX_OF_PHAR: int = 2
INDEX_OF_NILE: int = 3
INDEX_OF_FLOOD: int = 4
INDEX_OF_ASTR: int = 5
INDEX_OF_AGR: int = 6
INDEX_OF_WRI: int = 7
INDEX_OF_REL: int = 8
INDEX_OF_ART: int = 9
INDEX_OF_FORT: int = 10
INDEX_OF_OBEL: int = 11
INDEX_OF_PAL: int = 12
INDEX_OF_PYR: int = 13
INDEX_OF_TEM: int = 14
INDEX_OF_STAT: int = 15
INDEX_OF_STE: int = 16
INDEX_OF_SPH: int = 17
INDEX_OF_DIS_PHAR: int = 18
INDEX_OF_DIS_NILE: int = 19
INDEX_OF_DIS_CIV: int = 20
INDEX_OF_DIS_MON: int = 21
INDEX_OF_RA: int = 22

# Definitions of each tile type


@enum.unique
class TileType(str, enum.Enum):
    COLLECTIBLE = "COLLECTIBLE"
    DISASTER = "DISASTER"
    RA = "RA"


class TileTypeInfo(TypedDict):
    name: str
    # how many start in the bag
    startingNum: int
    # how many start in the bag
    toKeep: bool
    # whether it's a collectible, disaster, etc.
    tileType: TileType
    # the index of the tile in the tile bag's list
    index: int


GOD = TileTypeInfo(
    name="Golden God",
    startingNum=8,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_GOD,
)
GOLD = TileTypeInfo(
    name="Gold",
    startingNum=5,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_GOLD,
)

PHAR = TileTypeInfo(
    name="Pharaoh",
    startingNum=25,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_PHAR,
)

NILE = TileTypeInfo(
    name="Nile",
    startingNum=25,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_NILE,
)
FLOOD = TileTypeInfo(
    name="Flood",
    startingNum=12,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_FLOOD,
)

CIV_ASTR = TileTypeInfo(
    name="Civilization -- Astronomy",
    startingNum=5,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_ASTR,
)
CIV_AGR = TileTypeInfo(
    name="Civilization -- Agriculture",
    startingNum=5,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_AGR,
)
CIV_WRI = TileTypeInfo(
    name="Civilization -- Writing",
    startingNum=5,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_WRI,
)
CIV_REL = TileTypeInfo(
    name="Civilization -- Religion",
    startingNum=5,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_REL,
)
CIV_ART = TileTypeInfo(
    name="Civilization -- Art",
    startingNum=5,
    toKeep=False,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_ART,
)

MON_FORT = TileTypeInfo(
    name="Monument -- Fortress",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_FORT,
)
MON_OBEL = TileTypeInfo(
    name="Monument -- Obelisk",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_OBEL,
)
MON_PAL = TileTypeInfo(
    name="Monument -- Palace",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_PAL,
)
MON_PYR = TileTypeInfo(
    name="Monument -- Pyramid",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_PYR,
)
MON_TEM = TileTypeInfo(
    name="Monument -- Temple",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_TEM,
)
MON_STAT = TileTypeInfo(
    name="Monument -- Statue",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_STAT,
)
MON_STE = TileTypeInfo(
    name="Monument -- Step Pyramid",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_STE,
)
MON_SPH = TileTypeInfo(
    name="Monument -- Sphinx",
    startingNum=5,
    toKeep=True,
    tileType=TileType.COLLECTIBLE,
    index=INDEX_OF_SPH,
)

DIS_PHAR = TileTypeInfo(
    name="Disaster -- Funeral",
    startingNum=2,
    toKeep=False,
    tileType=TileType.DISASTER,
    index=INDEX_OF_DIS_PHAR,
)
DIS_NILE = TileTypeInfo(
    name="Disaster -- Drought",
    startingNum=2,
    toKeep=False,
    tileType=TileType.DISASTER,
    index=INDEX_OF_DIS_NILE,
)
DIS_CIV = TileTypeInfo(
    name="Disaster -- War",
    startingNum=4,
    toKeep=False,
    tileType=TileType.DISASTER,
    index=INDEX_OF_DIS_CIV,
)
DIS_MON = TileTypeInfo(
    name="Disaster -- Earthquake",
    startingNum=2,
    toKeep=False,
    tileType=TileType.DISASTER,
    index=INDEX_OF_DIS_MON,
)

RA = TileTypeInfo(
    name="Ra", startingNum=30, toKeep=False, tileType=TileType.RA, index=INDEX_OF_RA
)


# a list of all tile types
# An index corresponds to the tile in this list
# WARNING: changing this list changes everything below within this section
TILE_INFO: List[TileTypeInfo] = [
    GOD,
    GOLD,
    PHAR,
    NILE,
    FLOOD,
    CIV_ASTR,
    CIV_AGR,
    CIV_WRI,
    CIV_REL,
    CIV_ART,
    MON_FORT,
    MON_OBEL,
    MON_PAL,
    MON_PYR,
    MON_TEM,
    MON_STAT,
    MON_STE,
    MON_SPH,
    DIS_PHAR,
    DIS_NILE,
    DIS_CIV,
    DIS_MON,
    RA,
]


NUM_TILE_TYPES: int = len(TILE_INFO)  # total number of tiles types in the game

STARTING_NUM_TILES: int = 0  # total number of tiles that start in the bag
for tile in TILE_INFO:
    STARTING_NUM_TILES += tile["startingNum"]

NUM_AUCTIONABLE_TILE_TYPES: int = 0
for tile in TILE_INFO:
    if tile["tileType"] != TileType.RA:
        NUM_AUCTIONABLE_TILE_TYPES += 1

NUM_COLLECTIBLE_TILE_TYPES: int = 0  # the number of tiles players can collect
for tile in TILE_INFO:
    if tile["tileType"] == TileType.COLLECTIBLE:
        NUM_COLLECTIBLE_TILE_TYPES += 1

NUM_CIVS: int = 5
STARTING_INDEX_OF_CIVS: int = 5

NUM_MONUMENTS: int = 8
STARTING_INDEX_OF_MONUMENTS: int = 10

NUM_DISASTERS: int = 4
STARTING_INDEX_OF_DISASTERS: int = 18


def tile_starting_num(tile: TileTypeInfo) -> int:
    """Given a tile, return how many we start with."""
    return tile["startingNum"]


def tile_name(tile: TileTypeInfo) -> str:
    """Given a tile, return its name."""
    return tile["name"]


def index_to_tile(index: int) -> TileTypeInfo:
    """Given an index of TILE_INFO, give the TileTypeInfo."""
    assert index >= 0 and index <= 23
    return TILE_INFO[index]


def index_to_tile_name(index: int) -> str:
    """Given an index of TILE_INFO, give the tilename of that tile type."""
    return tile_name(index_to_tile(index))


def index_to_starting_num(index: int) -> int:
    """Given an index of TILE_INFO, give tile starting num of that type."""
    return tile_starting_num(index_to_tile(index))


def index_is_collectible(index: int) -> bool:
    """Return whether the tile of an index is a collectible type."""
    return index_to_tile(index)["tileType"] == TileType.COLLECTIBLE


def index_is_disaster(index: int) -> bool:
    return index_to_tile(index)["tileType"] == TileType.DISASTER


def index_is_ra(index: int) -> bool:
    return index_to_tile(index)["tileType"] == TileType.RA


def list_of_temporary_collectible_indexes() -> List[int]:
    temp_collectibles = []
    for i in range(NUM_TILE_TYPES):
        curr_tile = TILE_INFO[i]
        if curr_tile["tileType"] == TileType.COLLECTIBLE and not curr_tile["toKeep"]:
            temp_collectibles.append(i)
    return temp_collectibles


def get_civs_from_collection(collection: Sequence[int]) -> Sequence[int]:
    return collection[STARTING_INDEX_OF_CIVS : (STARTING_INDEX_OF_CIVS + NUM_CIVS)]


def get_monuments_from_collection(collection: Sequence[int]) -> Sequence[int]:
    return collection[
        STARTING_INDEX_OF_MONUMENTS : (STARTING_INDEX_OF_MONUMENTS + NUM_MONUMENTS)
    ]


# Action definitions

DRAW: int = 0  # draw a tile from the bag
AUCTION: int = 1  # start an auction
GOD_1: int = 2  # use a golden god to take the 1st auction tile
GOD_2: int = 3  # use a golden god to take the 2nd auction tile
GOD_3: int = 4  # use a golden god to take the 3rd auction tile
GOD_4: int = 5
GOD_5: int = 6
GOD_6: int = 7
GOD_7: int = 8
GOD_8: int = 9
BID_1: int = 10  # bid the lowest value sun
BID_2: int = 11  # bid the second lowest value sun
BID_3: int = 12  # bid the third lowest value sun
BID_4: int = 13  # bid the fourth lowest value sun
BID_NOTHING: int = 14  # bid nothing
DISCARD_ASTR: int = 15  # discard astronomy civ
DISCARD_AGR: int = 16  # discard agriculture civ
DISCARD_WRI: int = 17  # discard writing civ
DISCARD_REL: int = 18  # discard religion civ
DISCARD_ART: int = 19  # discard art civ
DISCARD_FORT: int = 20  # discard fortress monument
DISCARD_OBEL: int = 21  # discard obelisk monument
DISCARD_PAL: int = 22  # discard palace monument
DISCARD_PYR: int = 23  # discard pyramid monument
DISCARD_TEM: int = 24  # discard temple monument
DISCARD_STAT: int = 25  # discard statue monument
DISCARD_STE: int = 26  # discard step pyramid monument
DISCARD_SPH: int = 27  # discard sphinx monument

ACTION_MAPPING: Mapping[int, str] = {
    DRAW: "draw",
    AUCTION: "auction",
    GOD_1: "golden_god_1",
    GOD_2: "golden_god_2",
    GOD_3: "golden_god_3",
    GOD_4: "golden_god_4",
    GOD_5: "golden_god_5",
    GOD_6: "golden_god_6",
    GOD_7: "golden_god_7",
    GOD_8: "golden_god_8",
    BID_1: "bid_lowest_sun",
    BID_2: "bid_second_lowest_sun",
    BID_3: "bid_third_lowest_sun",
    BID_4: "bid_fourth_lowest_sun",
    BID_NOTHING: "bid_nothing",
    DISCARD_ASTR: "discard_astronomy_civ",
    DISCARD_AGR: "discard_agriculture_civ",
    DISCARD_WRI: "discard_writing_civ",
    DISCARD_REL: "discard_religion_civ",
    DISCARD_ART: "discard_art_civ",
    DISCARD_FORT: "discard_fortress_monument",
    DISCARD_OBEL: "discard_obelisk_monument",
    DISCARD_PAL: "discard_palace_monument",
    DISCARD_PYR: "discard_pyramid_monument",
    DISCARD_TEM: "discard_temple_monument",
    DISCARD_STAT: "discard_statue_monument",
    DISCARD_STE: "discard_step_pyramid_monument",
    DISCARD_SPH: "discard_sphynx_monument",
}


# Valid user inputs for each Action
DRAW_OPTIONS: List[str] = ["0", "draw", "d"]
AUCTION_OPTIONS: List[str] = ["1", "auction", "a"]
GOD_1_OPTIONS: List[str] = ["2", "god 1", "g1", "g 1", "god1"]
GOD_2_OPTIONS: List[str] = ["3", "god 2", "g2", "g 2", "god2"]
GOD_3_OPTIONS: List[str] = ["4", "god 3", "g3", "g 3", "god3"]
GOD_4_OPTIONS: List[str] = ["5", "god 4", "g4", "g 4", "god4"]
GOD_5_OPTIONS: List[str] = ["6", "god 5", "g5", "g 5", "god5"]
GOD_6_OPTIONS: List[str] = ["7", "god 6", "g6", "g 6", "god6"]
GOD_7_OPTIONS: List[str] = ["8", "god 7", "g7", "g 7", "god7"]
GOD_8_OPTIONS: List[str] = ["9", "god 8", "g8", "g 8", "god8"]
BID_1_OPTIONS: List[str] = ["10", "bid lowest", "b1", "b 1", "bid1", "bid 1"]
BID_2_OPTIONS: List[str] = ["11", "bid second lowest", "b2", "b 2", "bid2", "bid 2"]
BID_3_OPTIONS: List[str] = ["12", "bid third lowest", "b3", "b 3", "bid3", "bid 3"]
BID_4_OPTIONS: List[str] = ["13", "bid fourth lowest", "b4", "b 4", "bid4", "bid 4"]
BID_NOTHING_OPTIONS: List[str] = [
    "14",
    "b0",
    "b 0",
    "bid0",
    "bid 0",
    "bid nothing",
    "pass",
    "p",
]
DISCARD_ASTR_OPTIONS: List[str] = ["15", "discard astronomy", "astronomy", "astr"]
DISCARD_AGR_OPTIONS: List[str] = ["16", "discard agriculture", "agriculture", "agr"]
DISCARD_WRI_OPTIONS: List[str] = ["17", "discard writing", "writing", "wri"]
DISCARD_REL_OPTIONS: List[str] = ["18", "discard religion", "religion", "rel"]
DISCARD_ART_OPTIONS: List[str] = ["19", "discard art", "art"]
DISCARD_FORT_OPTIONS: List[str] = ["20", "discard fortress", "for"]
DISCARD_OBEL_OPTIONS: List[str] = ["21", "discard obelisk", "obelisk", "obel"]
DISCARD_PAL_OPTIONS: List[str] = ["22", "discard palace", "palace", "pal"]
DISCARD_PYR_OPTIONS: List[str] = ["23", "discard pyramid", "pyramid", "pyr"]
DISCARD_TEM_OPTIONS: List[str] = ["24", "discard temple", "temple", "tem"]
DISCARD_STAT_OPTIONS: List[str] = ["25", "discard statue", "statue", "sta"]
DISCARD_STE_OPTIONS: List[str] = ["26", "discard step pyramid", "step pyramid", "ste"]
DISCARD_SPH_OPTIONS: List[str] = ["27", "discard sphinx", "sphinx", "sph"]


# Description Text for Each Option
DRAW_DESC: str = "Draw a Tile"
AUCTION_DESC: str = "Start an Auction"
GOD_1_DESC: str = "Golden God -- Take the 1st auction tile"
GOD_2_DESC: str = "Golden God -- Take the 2nd auction tile"
GOD_3_DESC: str = "Golden God -- Take the 3rd auction tile"
GOD_4_DESC: str = "Golden God -- Take the 4th auction tile"
GOD_5_DESC: str = "Golden God -- Take the 5th auction tile"
GOD_6_DESC: str = "Golden God -- Take the 6th auction tile"
GOD_7_DESC: str = "Golden God -- Take the 7th auction tile"
GOD_8_DESC: str = "Golden God -- Take the 8th auction tile"
BID_1_DESC: str = "Bid your lowest tile"
BID_2_DESC: str = "Bid your second lowest tile"
BID_3_DESC: str = "Bid your third lowest tile"
BID_4_DESC: str = "Bid your fourth lowest tile"
BID_NOTHING_DESC: str = "Pass without bidding"
DISCARD_ASTR_DESC: str = "Discard the ASTRONOMY civilization tile"
DISCARD_AGR_DESC: str = "Discard the AGRICULTURE civilization tile"
DISCARD_WRI_DESC: str = "Discard the WRITING civilization tile"
DISCARD_REL_DESC: str = "Discard the RELIGION civilization tile"
DISCARD_ART_DESC: str = "Discard the ART civilization tile"
DISCARD_FORT_DESC: str = "Discard the FORT monument tile"
DISCARD_OBEL_DESC: str = "Discard the OBELISK monument tile"
DISCARD_PAL_DESC: str = "Discard the PALACE monument tile"
DISCARD_PYR_DESC: str = "Discard the PYRAMID monument tile"
DISCARD_TEM_DESC: str = "Discard the TEMPLE monument tile"
DISCARD_STAT_DESC: str = "Discard the STATUE monument tile"
DISCARD_STE_DESC: str = "Discard the STEP PYRAMID monument tile"
DISCARD_SPH_DESC: str = "Discard the SPHINX monument tile"


action_option_lst: List[Tuple[int, List[str], str]] = [
    (DRAW, DRAW_OPTIONS, DRAW_DESC),
    (AUCTION, AUCTION_OPTIONS, AUCTION_DESC),
    (GOD_1, GOD_1_OPTIONS, GOD_1_DESC),
    (GOD_2, GOD_2_OPTIONS, GOD_2_DESC),
    (GOD_3, GOD_3_OPTIONS, GOD_3_DESC),
    (GOD_4, GOD_4_OPTIONS, GOD_4_DESC),
    (GOD_5, GOD_5_OPTIONS, GOD_5_DESC),
    (GOD_6, GOD_6_OPTIONS, GOD_6_DESC),
    (GOD_7, GOD_7_OPTIONS, GOD_7_DESC),
    (GOD_8, GOD_8_OPTIONS, GOD_8_DESC),
    (BID_1, BID_1_OPTIONS, BID_1_DESC),
    (BID_2, BID_2_OPTIONS, BID_2_DESC),
    (BID_3, BID_3_OPTIONS, BID_3_DESC),
    (BID_4, BID_4_OPTIONS, BID_4_DESC),
    (BID_NOTHING, BID_NOTHING_OPTIONS, BID_NOTHING_DESC),
    (DISCARD_ASTR, DISCARD_ASTR_OPTIONS, DISCARD_ASTR_DESC),
    (DISCARD_AGR, DISCARD_AGR_OPTIONS, DISCARD_AGR_DESC),
    (DISCARD_WRI, DISCARD_WRI_OPTIONS, DISCARD_WRI_DESC),
    (DISCARD_REL, DISCARD_REL_OPTIONS, DISCARD_REL_DESC),
    (DISCARD_ART, DISCARD_ART_OPTIONS, DISCARD_ART_DESC),
    (DISCARD_FORT, DISCARD_FORT_OPTIONS, DISCARD_FORT_DESC),
    (DISCARD_OBEL, DISCARD_OBEL_OPTIONS, DISCARD_OBEL_DESC),
    (DISCARD_PAL, DISCARD_PAL_OPTIONS, DISCARD_PAL_DESC),
    (DISCARD_PYR, DISCARD_PYR_OPTIONS, DISCARD_PYR_DESC),
    (DISCARD_TEM, DISCARD_TEM_OPTIONS, DISCARD_TEM_DESC),
    (DISCARD_STAT, DISCARD_STAT_OPTIONS, DISCARD_STAT_DESC),
    (DISCARD_STE, DISCARD_STE_OPTIONS, DISCARD_STE_DESC),
    (DISCARD_SPH, DISCARD_SPH_OPTIONS, DISCARD_SPH_DESC),
]


def action_description(action: int) -> str:
    return action_option_lst[action][2]


# sanity check to make sure no options overlap
for i in range(len(action_option_lst)):
    options_1 = action_option_lst[i][1]
    for j in range(i + 1, len(action_option_lst)):
        options_2 = action_option_lst[j][1]
        if set(options_1) & set(options_2):
            raise Exception(f"Options are overlapping: {options_1} and {options_2}")


# Scoring

POINTS_PER_GOD: int = 2
POINTS_PER_GOLD: int = 3
POINTS_FOR_LEAST_PHAR: int = -2
POINTS_FOR_MOST_PHAR: int = 5
POINTS_PER_NILE: int = 1
POINTS_PER_FLOOD: int = 1
POINTS_FOR_CIVS: List[int] = [-5, 0, 0, 5, 10, 15]
POINTS_FOR_MON_DEPTH: List[int] = [0, 0, 0, 5, 10, 15]
POINTS_FOR_MON_BREADTH: List[int] = [0, 1, 2, 3, 4, 5, 6, 10, 15]
POINTS_FOR_LEAST_SUN: int = -5
POINTS_FOR_MOST_SUN: int = 5
