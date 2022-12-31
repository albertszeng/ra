const DefaultPlayer: Player = {
  collection: [],
  points: 0,
  playerName: '',
  usableSun: [],
  unusableSun: [],
};
type Tile = {
  // This is used to fetch the corresponding file for display purposes.
  // This means file names should match the backend names.
  name: string;
  tileType: 'COLLECTIBLE' | 'DISASTER' | 'RA';
  // How many start in the bag
  startingNum: number;
  // Whether we should keep or not.
  toKeep: boolean;
};
function getTileShortName(name: string): string {
  const pieces = name.split(' -- ');
  return pieces[pieces.length - 1];
}
// These tiles have special actions associated with them.
type TileAction = 'SWAP' | string;
function getTileAction({ name }: Tile): TileAction | null {
  // Currently based on the name.
  const upper = name.toUpperCase();
  if (upper.includes('MONUMENT')) {
    return `DISCARD ${getTileShortName(upper)}`;
  }
  if (upper.includes('CIVILIZATION')) {
    return `DISCARD ${getTileShortName(upper)}`;
  }
  if (upper.includes('GOLDEN GOD')) {
    return 'SWAP';
  }
  return null;
}

type Player = {
  // The tiles the player currently has in his collection.
  collection: Tile[];
  // The current point total of the player.
  points: number;
  // The full name of the player.
  playerName: string;
  // The list of sun the player can bid.
  usableSun: number[];
  // The List of sun the player has previously bid.
  unusableSun: number[];
};

type GameState = {
  // Total number of rounds to play.
  totalRounds: number;
  // Total number of Ra tiles per round.
  numRasPerRound: number;
  // Total number of active players.
  numPlayers: number;
  // maximum number of tiles up for auction at once
  maxAuctionTiles: number;

  // The current round.
  currentRound: number;
  // If true, the player[i] is active.
  activePlayers: boolean[];
  // The number of Ra tiles revealed so far.
  numRasThisRound: number;
  // The value of the sun tile in the center.
  centerSun: number;
  // The tiles currently up for auction.
  auctionTiles: Tile[];
  // For each player i, how much sun have they bid if any.
  auctionSuns: (number | null)[];
  // Whether or not an action has started.
  auctionStarted: boolean;
  // The index of the player that started the auction, if any.
  auctionStartPlayer: number | null;
  // The index of the current player.
  currentPlayer: number;
  // The index of the player that won the auction, if any.
  auctionWinningPlayer: number | null;
  // The serialized player states.
  playerStates: Player[];
  // True if the game is over.
  gameEnded: boolean;
};
const DefaultGameState = {
  totalRounds: 0,
  numRasPerRound: 0,
  numPlayers: 0,
  maxAuctionTiles: 0,

  currentRound: 0,
  activePlayers: [],
  numRasThisRound: 0,
  centerSun: 0,
  auctionTiles: [],
  auctionSuns: [],
  auctionStarted: false,
  auctionStartPlayer: null,
  currentPlayer: 0,
  auctionWinningPlayer: null,
  playerStates: [],
  gameEnded: false,
};

type PointMapping = {
  [key: string]: number;
};
type Game = {
  playerNames: string[];
  gameLog: ([string, number | null] | number)[],
  gameState: GameState;
  // Mapping from player names to unrealized points.
  unrealizedPoints: PointMapping;
  auctionTileValues: PointMapping;
};

const DefaultGame: Game = {
  playerNames: [],
  gameLog: [],
  gameState: DefaultGameState,
  unrealizedPoints: {},
  auctionTileValues: {},
};

function notEmpty<TValue>(value: TValue | null | undefined): value is TValue {
  return value !== null && value !== undefined;
}

export type {
  Game,
  GameState,
  Player,
  PointMapping,
  Tile,
  TileAction,
};

export {
  DefaultGame,
  DefaultPlayer,
  getTileAction,
  getTileShortName,
  notEmpty,
};
