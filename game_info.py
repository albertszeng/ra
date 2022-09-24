from enum import Enum


### Game Constants

# most and least players allowed
MAX_NUM_PLAYERS = 5
MIN_NUM_PLAYERS = 2

# the sun that starts in the middle
STARTING_CENTER_SUN = 1

# (players in game: starting sun sets)
# assert that the first move goes to the player with the first set in each list
STARTING_SUN = {2: [[2, 5, 6, 9], [3, 4, 7, 8]],
            3: [[2, 5, 8, 13], [3, 6, 9, 12], [4, 7, 10, 11]],
            4: [[2, 6, 13], [3, 7, 12], [4, 8, 11], [5, 9, 10]],
            5: [[2, 7, 16], [3, 8, 15], [4, 9, 14], [5, 10, 13], [6, 11, 12]]}

# num of players: number of ra tiles per round
NUM_RAS_PER_ROUND = {2: 6, 3: 8, 4: 9, 6: 10}

# number of points each player starts with
STARTING_PLAYER_POINTS = 10

# number of rounds in the game
NUM_ROUNDS = 3

# maximum number of tiles up for auction at once
MAX_AUCTION_TILES = 8

# number of tiles to discard per disaster
NUM_DISCARDS_PER_DISASTER = 2


### Definitions of each tile type

class TileTypeInfo():
    def __init__(self, name, startingNum, toKeep, tileType):
        self.name = name
        self.startingNum = startingNum  # how many start in the bag
        self.toKeep = toKeep  # how many start in the bag
        self.tileType = tileType  # whether it's a collectible, disaster, etc.

class TileType(Enum):
    COLLECTIBLE = 1
    DISASTER = 2
    RA = 3


GOD = TileTypeInfo("Golden God", 8, False, TileType.COLLECTIBLE)
GOLD = TileTypeInfo("Gold", 5, False, TileType.COLLECTIBLE)

PHAR = TileTypeInfo("Pharaoh", 25, True, TileType.COLLECTIBLE)

NILE = TileTypeInfo("Nile", 25, True, TileType.COLLECTIBLE)
FLOOD = TileTypeInfo("Flood", 12, False, TileType.COLLECTIBLE)

CIV_ASTR = TileTypeInfo("Civilization -- Astronomy", 5, False, TileType.COLLECTIBLE)
CIV_AGR = TileTypeInfo("Civilization -- Agriculture", 5, False, TileType.COLLECTIBLE)
CIV_WRI = TileTypeInfo("Civilization -- Writing", 5, False, TileType.COLLECTIBLE)
CIV_REL = TileTypeInfo("Civilization -- Religion", 5, False, TileType.COLLECTIBLE)
CIV_ART = TileTypeInfo("Civilization -- Art", 5, False, TileType.COLLECTIBLE)

MON_FORT = TileTypeInfo("Monument -- Fortress", 5, True, TileType.COLLECTIBLE)
MON_OBEL = TileTypeInfo("Monument -- Obelisk", 5, True, TileType.COLLECTIBLE)
MON_PAL = TileTypeInfo("Monument -- Palace", 5, True, TileType.COLLECTIBLE)
MON_PYR = TileTypeInfo("Monument -- Pyramid", 5, True, TileType.COLLECTIBLE)
MON_TEM = TileTypeInfo("Monument -- Temple", 5, True, TileType.COLLECTIBLE)
MON_STAT = TileTypeInfo("Monument -- Statue", 5, True, TileType.COLLECTIBLE)
MON_STE = TileTypeInfo("Monument -- Step Pyramid", 5, True, TileType.COLLECTIBLE)
MON_SPH = TileTypeInfo("Monument -- Sphinx", 5, True, TileType.COLLECTIBLE)

DIS_PHAR = TileTypeInfo("Disaster -- Funeral", 2, False, TileType.DISASTER)
DIS_NILE = TileTypeInfo("Disaster -- Drought", 2, False, TileType.DISASTER)
DIS_CIV = TileTypeInfo("Disaster -- War", 4, False, TileType.DISASTER)
DIS_MON = TileTypeInfo("Disaster -- Earthquake", 2, False, TileType.DISASTER)

RA = TileTypeInfo("Ra", 30, False, TileType.RA)


# a list of all tile types
# An index corresponds to the tile in this list
# WARNING: changing this list changes everything below within this section
TILE_INFO = [GOD, GOLD, PHAR, NILE, FLOOD, CIV_ASTR, CIV_AGR, \
            CIV_WRI, CIV_REL, CIV_ART, MON_FORT, MON_OBEL, MON_PAL, \
            MON_PYR, MON_TEM, MON_STAT, MON_STE, MON_SPH, DIS_PHAR, \
            DIS_NILE, DIS_CIV, DIS_MON, RA]


NUM_TILE_TYPES = len(TILE_INFO)  # total number of tiles types in the game

STARTING_NUM_TILES = 0  # total number of tiles that start in the bag
for tile in TILE_INFO:
    STARTING_NUM_TILES += tile.startingNum

NUM_AUCTIONABLE_TILE_TYPES = 0
for tile in TILE_INFO:
    if tile.tileType != TileType.RA:
        NUM_AUCTIONABLE_TILE_TYPES += 1

NUM_COLLECTIBLE_TILE_TYPES = 0  # the number of tiles players can collect
for tile in TILE_INFO:
    if tile.tileType == TileType.COLLECTIBLE:
        NUM_COLLECTIBLE_TILE_TYPES += 1

INDEX_OF_GOD = 0
INDEX_OF_GOLD = 1
INDEX_OF_PHAR = 2
INDEX_OF_NILE = 3
INDEX_OF_FLOOD = 4
INDEX_OF_ASTR = 5
INDEX_OF_AGR = 6
INDEX_OF_WRI = 7
INDEX_OF_REL = 8
INDEX_OF_ART = 9
INDEX_OF_FORT = 10
INDEX_OF_OBEL = 11
INDEX_OF_PAL = 12
INDEX_OF_PYR = 13
INDEX_OF_TEM = 14
INDEX_OF_STAT = 15
INDEX_OF_STE = 16
INDEX_OF_SPH = 17
INDEX_OF_DIS_PHAR = 18
INDEX_OF_DIS_NILE = 19
INDEX_OF_DIS_CIV = 20
INDEX_OF_DIS_MON = 21
INDEX_OF_RA = 22

NUM_CIVS = 5
STARTING_INDEX_OF_CIVS = 5

NUM_MONUMENTS = 8
STARTING_INDEX_OF_MONUMENTS = 10

NUM_DISASTERS = 4
STARTING_INDEX_OF_DISASTERS = 18


### Helper functions for getting tile info

def tile_starting_num(tile):
    return tile.startingNum

def tile_name(tile):
    return tile.name

# given an index of TILE_INFO, give the TileTypeInfo
def index_to_tile(index):
    assert(index >= 0 and index <= 23)
    return TILE_INFO[index]

# given an index of TILE_INFO, give the tilename of that tile type
def index_to_tile_name(index):
    return tile_name(index_to_tile(index))

# given an index of TILE_INFO, give the tile starting num of that tile type
def index_to_starting_num(index):
    return tile_starting_num(index_to_tile(index))

# return whether the tile of an index is a collectible type
def index_is_collectible(index):
    return index_to_tile(index).tileType == TileType.COLLECTIBLE

def index_is_disaster(index):
    return index_to_tile(index).tileType == TileType.DISASTER

def index_is_ra(index):
    return index_to_tile(index).tileType == TileType.RA

def list_of_temporary_collectible_indexes():
    temp_collectibles = []
    for i in range(NUM_TILE_TYPES):
        curr_tile = TILE_INFO[i]
        if curr_tile.tileType == TileType.COLLECTIBLE and not curr_tile.toKeep:
            temp_collectibles.append(i)
    return temp_collectibles

def get_civs_from_collection(collection):
    return collection[STARTING_INDEX_OF_CIVS:(STARTING_INDEX_OF_CIVS + NUM_CIVS)]

def get_monuments_from_collection(collection):
    return collection[STARTING_INDEX_OF_MONUMENTS:(STARTING_INDEX_OF_MONUMENTS + NUM_MONUMENTS)]


### Action definitions

DRAW = 0  # draw a tile from the bag
AUCTION = 1  # start an auction
GOD_1 = 2  # use a golden god to take the 1st auction tile
GOD_2 = 3  # use a golden god to take the 2nd auction tile
GOD_3 = 4  # use a golden god to take the 3rd auction tile
GOD_4 = 5
GOD_5 = 6
GOD_6 = 7
GOD_7 = 8
GOD_8 = 9
BID_1 = 10  # bid the lowest value sun
BID_2 = 11  # bid the second lowest value sun
BID_3 = 12  # bid the third lowest value sun
BID_4 = 13  # bid the fourth lowest value sun
BID_NOTHING = 14  # bid nothing
DISCARD_ASTR = 15  # discard astronomy civ
DISCARD_AGR = 16  # discard agriculture civ
DISCARD_WRI = 17  # discard writing civ
DISCARD_REL = 18  # discard religion civ
DISCARD_ART = 19  # discard art civ
DISCARD_FORT = 20  # discard fortress monument
DISCARD_OBEL = 21  # discard obelisk monument
DISCARD_PAL = 22  # discard palace monument
DISCARD_PYR = 23  # discard pyramid monument
DISCARD_TEM = 24  # discard temple monument
DISCARD_STAT = 25  # discard statue monument
DISCARD_STE = 26  # discard step pyramid monument
DISCARD_SPH = 27  # discard sphinx monument


# Valid user inputs for each Action
DRAW_OPTIONS = ["0", "draw", "d"]
AUCTION_OPTIONS = ["1", "auction", "a"]
GOD_1_OPTIONS = ["2", "god 1", "g1", "g 1", "god1"]
GOD_2_OPTIONS = ["3", "god 2", "g2", "g 2", "god2"]
GOD_3_OPTIONS = ["4", "god 3", "g3", "g 3", "god3"]
GOD_4_OPTIONS = ["5", "god 4", "g4", "g 4", "god4"]
GOD_5_OPTIONS = ["6", "god 5", "g5", "g 5", "god5"]
GOD_6_OPTIONS = ["7", "god 6", "g6", "g 6", "god6"]
GOD_7_OPTIONS = ["8", "god 7", "g7", "g 7", "god7"]
GOD_8_OPTIONS = ["9", "god 8", "g8", "g 8", "god8"]
BID_1_OPTIONS = ["10", "bid lowest", "b1", "b 1", "bid1", "bid 1"]
BID_2_OPTIONS = ["11", "bid second lowest", "b2", "b 2", "bid2", "bid 2"]
BID_3_OPTIONS = ["12", "bid third lowest", "b3", "b 3", "bid3", "bid 3"]
BID_4_OPTIONS = ["13", "bid fourth lowest", "b4", "b 4", "bid4", "bid 4"]
BID_NOTHING_OPTIONS = ["14", "b0", "b 0", "bid0", "bid 0", "bid nothing", "pass", "p"]
DISCARD_ASTR_OPTIONS = ["15", "discard astronomy", "astronomy", "astr"]
DISCARD_AGR_OPTIONS = ["16", "discard agriculture", "agriculture", "agr"]
DISCARD_WRI_OPTIONS = ["17", "discard writing", "writing", "wri"]
DISCARD_REL_OPTIONS = ["18", "discard religion", "religion", "rel"]
DISCARD_ART_OPTIONS = ["19", "discard art", "art"]
DISCARD_FORT_OPTIONS = ["20", "discard fort", "fort"]
DISCARD_OBEL_OPTIONS = ["21", "discard obelisk", "obelisk", "obel"]
DISCARD_PAL_OPTIONS = ["22", "discard palace", "palace", "pal"]
DISCARD_PYR_OPTIONS = ["23", "discard pyramid", "pyramid", "pyr"]
DISCARD_TEM_OPTIONS = ["24", "discard temple", "temple", "tem"]
DISCARD_STAT_OPTIONS = ["25", "discard statue", "statue", "sta"]
DISCARD_STE_OPTIONS = ["26", "discard step pyramid", "step pyramid", "ste"]
DISCARD_SPH_OPTIONS = ["27", "discard sphinx", "sphinx", "sph"]


# Description Text for Each Option
DRAW_DESC = "Draw a Tile"
AUCTION_DESC = "Start an Auction"
GOD_1_DESC = "Golden God -- Take the 1st auction tile"
GOD_2_DESC = "Golden God -- Take the 2nd auction tile"
GOD_3_DESC = "Golden God -- Take the 3rd auction tile"
GOD_4_DESC = "Golden God -- Take the 4th auction tile"
GOD_5_DESC = "Golden God -- Take the 5th auction tile"
GOD_6_DESC = "Golden God -- Take the 6th auction tile"
GOD_7_DESC = "Golden God -- Take the 7th auction tile"
GOD_8_DESC = "Golden God -- Take the 8th auction tile"
BID_1_DESC = "Bid your lowest tile"
BID_2_DESC = "Bid your second lowest tile"
BID_3_DESC = "Bid your third lowest tile"
BID_4_DESC = "Bid your fourth lowest tile"
BID_NOTHING_DESC = "Pass without bidding"
DISCARD_ASTR_DESC = "Discard the ASTRONOMY civilization tile"
DISCARD_AGR_DESC = "Discard the AGRICULTURE civilization tile"
DISCARD_WRI_DESC = "Discard the WRITING civilization tile"
DISCARD_REL_DESC = "Discard the RELIGION civilization tile"
DISCARD_ART_DESC = "Discard the ART civilization tile"
DISCARD_FORT_DESC = "Discard the FORT monument tile"
DISCARD_OBEL_DESC = "Discard the OBELISK monument tile"
DISCARD_PAL_DESC = "Discard the PALACE monument tile"
DISCARD_PYR_DESC = "Discard the PYRAMID monument tile"
DISCARD_TEM_DESC = "Discard the TEMPLE monument tile"
DISCARD_STAT_DESC = "Discard the STATUE monument tile"
DISCARD_STE_DESC = "Discard the STEP PYRAMID monument tile"
DISCARD_SPH_DESC = "Discard the SPHINX monument tile"



action_option_lst = [
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
    (DISCARD_SPH, DISCARD_SPH_OPTIONS, DISCARD_SPH_DESC)
]

# sanity check to make sure no options overlap
for i in range(len(action_option_lst)):
    options_1 = action_option_lst[i][1]
    for j in range(i + 1, len(action_option_lst)):
        options_2 = action_option_lst[j][1]
        if set(options_1) & set(options_2):
            raise Exception(f"Options are overlapping: {options_1} and {options_2}")



### Scoring

POINTS_PER_GOD = 2
POINTS_PER_GOLD = 3
POINTS_FOR_LEAST_PHAR = -2
POINTS_FOR_MOST_PHAR = 5
POINTS_PER_NILE = 1
POINTS_PER_FLOOD = 1
POINTS_FOR_CIVS = [-5, 0, 0, 5, 10, 15]
POINTS_FOR_MON_DEPTH = [0, 0, 0, 5, 10, 15]
POINTS_FOR_MON_BREADTH = [0, 1, 2, 3, 4, 5, 6, 10, 15]
POINTS_FOR_LEAST_SUN = -5
POINTS_FOR_MOST_SUN = 5
