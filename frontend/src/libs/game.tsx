type Player = {
  // The tiles the player currently has in his collection.
  collection: string[];
  // The current point total of the player.
  points: number;
  // The full name of the player.
  player_name: string;
  // The list of sun the player can bid.
  usable_sun: number[];
  // The List of sun the player has previously bid.
  unusable_sun: number[];
};

type Game = {
  player_names: string[];
  game_state: {
    // The current round.
    current_round: number;
    // If true, the player[i] is active.
    active_players: boolean[];
    // The number of Ra tiles revealed so far.
    num_ras_this_round: number;
    // The value of the sun tile in the center.
    center_sun: number;
    // The tiles currently up for auction.
    auction_tiles: string[];
    // For each player i, how much sun have they bid if any.
    auction_suns: (number | null)[];
    // Whether or not an action has started.
    auction_started: boolean;
    // The index of the player that started the auction, if any.
    auction_start_player: number | null;
    // The index of the current player.
    current_player: number;
    // The index of the player that won the auction, if any.
    auction_winning_player: number | null;
    // The serialized player states.
    player_states: Player[];
    // True if the game is over.
    game_ended: boolean;
  }
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

async function startGame(players: string): Promise<ApiResponse> {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      player_names: players.split(','),
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
  Player,
};

export {
  deleteGame,
  handleCommand,
  startGame,
};
