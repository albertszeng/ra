type Player = {
  // The tiles the player currently has in his collection.
  collection: string[];
  // The current point total of the player.
  points: number;
  // The full name of the player.
  playerName: string;
  // The list of sun the player can bid.
  usableSun: number[];
  // The List of sun the player has previously bid.
  unusableSun: number[];
};

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

type Game = {
  playerNames: string[];
  gameState: GameState;
};

const DefaultGame: Game = {
  playerNames: [],
  gameState: DefaultGameState,
};

type ApiResponse = {
  message?: string;
  gameId?: string;
  gameAsStr?: string;
  gameState?: Game;
};

const apiUrl = process.env.BACKEND || 'http://127.0.0.1:5000';

async function handleCommand(gameId: string, command: string): Promise<ApiResponse> {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gameId, command }),
  };
  const res = await fetch(`${apiUrl}/action`, requestOptions);
  return res.json() as ApiResponse;
}

async function startGame(players: string[]): Promise<ApiResponse> {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      playerNames: players,
    }),
  };
  const res = await fetch(`${apiUrl}/start`, requestOptions);
  return res.json() as ApiResponse;
}

async function deleteGame(gameId: string): Promise<ApiResponse> {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      gameId,
    }),
  };
  const res = await fetch(`${apiUrl}/delete`, requestOptions);
  return res.json() as ApiResponse;
}

export type {
  ApiResponse,
  Game,
  GameState,
  Player,
};

export {
  DefaultGame,
  DefaultPlayer,
  deleteGame,
  handleCommand,
  startGame,
};
