import React, { useCallback, useEffect, useState } from 'react';

import Grid from '@mui/material/Unstable_Grid2';
import {
  Alert,
  Container,
  Paper,
  Snackbar,
} from '@mui/material';

import CardGrid from './CardGrid';
import EndInfo from './EndInfo';
import PlayersInfo from './PlayersInfo';
import PlayerForm from './PlayerForm';

import {
  DefaultGame,
  getTileAction,
  handleCommand,
  startGame,
  socket,
} from '../libs/game';
import type {
  AlertData,
  ApiResponse,
  Game as GameState,
  Player,
  Tile,
} from '../libs/game';

function Game(): JSX.Element {
  const GAME_STATE_KEY = 'LOCAL_GAME_STATE';
  const [game, setGame] = useState<GameState>(DefaultGame);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameId, setGameId] = useState<string>('');
  const [alertData, setAlertData] = useState<AlertData>(
    { show: false, message: '', level: 'info' },
  );
  // When true and set to a valid index, swap occurs.
  const [swapInfo, setSwapInfo] = useState<[boolean, number]>([false, -1]);

  // Store local game state to storage.
  useEffect(() => {
    if (game !== DefaultGame) {
      window.localStorage.setItem(GAME_STATE_KEY, JSON.stringify({
        game, gameId, isPlaying,
      }));
    }
  }, [game, isPlaying, gameId]);
  useEffect(() => {
    const data = window.localStorage.getItem(GAME_STATE_KEY);
    if (data !== null) {
      const {
        game: restoredGame,
        gameId: restoredGameId,
        isPlaying: restoredIsPlaying,
      } = JSON.parse(data) as { game: GameState, isPlaying: boolean, gameId: string };
      setGame(restoredGame);
      setIsPlaying(restoredIsPlaying);
      setGameId(restoredGameId);
      // Also let the server know we've joined again.
      socket.emit('join', { gameId: restoredGameId });
    }
  }, []);
  useEffect(() => {
    socket.on('update', ({ gameState }: ApiResponse) => {
      if (gameState) {
        setGame(gameState);
      }
    });
    return () => {
      socket.off('update');
    };
  }, []);

  const handleNewGame = useCallback(async (players: string[]) => {
    const {
      message,
      level,
      gameId: remoteGameId,
      gameState,
    } = await startGame(players);
    if (message || level || !remoteGameId || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setIsPlaying(true);
    setGameId(remoteGameId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);
  const handleLoadGame = useCallback(async (requestedId: string) => {
    const { level, message, gameState } = await handleCommand(requestedId, 'LOAD');
    if (message || level || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setIsPlaying(true);
    setGameId(requestedId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
    // Also let the server know we've joined again.
    socket.emit('join', { gameId: requestedId });
  }, []);
  const handleDraw = useCallback(async () => {
    if (!gameId) {
      setAlertData({ show: true, message: 'No active game.', level: 'warning' });
      return;
    }
    const { level, message, gameState } = await handleCommand(gameId, 'DRAW');
    if (level || message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId]);
  const handleAuction = useCallback(async () => {
    if (!gameId) {
      setAlertData({ show: true, message: 'No active game.', level: 'warning' });
      return;
    }
    const { message, gameState } = await handleCommand(gameId, 'AUCTION');
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level: 'error' });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId]);
  const handleBidAction = useCallback(async (idx: number) => {
    if (!gameId) {
      return;
    }
    // 1-indexed. 0 corresponds to passing in which case idx === -1.
    const { message, gameState } = await handleCommand(gameId, `B${idx + 1}`);
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level: 'error' });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId]);
  const handleSelectCardFromGrid = useCallback(async (idx: number, { name }: Tile) => {
    if (!gameId) {
      return;
    }
    const [shouldSwap] = swapInfo;
    if (!shouldSwap) {
      setAlertData({ show: true, message: `Click your Golden God to atttempt a swap for ${name}.`, level: 'info' });
      setSwapInfo([shouldSwap, idx]);
      return;
    }
    // Server command is 1-indexed, so we increment here.
    const { message, gameState } = await handleCommand(gameId, `G${idx + 1}`);
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level: 'error' });
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo]);
  const handlePlayerSelectTile = useCallback(async (player: Player, tile: Tile) => {
    if (!gameId) {
      setAlertData({ show: true, message: 'No active game.', level: 'info' });
      return;
    }
    let action = getTileAction(tile);
    if (!action) {
      setAlertData({ show: true, message: `${tile.name} is not play-able.`, level: 'warning' });
      return;
    }
    if (action === 'SWAP') {
      const [/* shouldSwap */, swapIdx] = swapInfo;
      if (swapIdx < 0) {
        setAlertData({ show: true, message: 'Click the card you wish to swap for your Golden God', level: 'info' });
        return;
      }
      action = `G${swapIdx + 1}`;
    }

    const { message, gameState } = await handleCommand(gameId, action);
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level: 'error' });
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setAlertData({ show: true, message: `Performed action: ${action}`, level: 'info' });
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo]);

  const resetGame = () => {
    setIsPlaying(false);
    // Let the server know we've left the game.
    socket.emit('leave', { gameId });
  };

  const { gameState } = game;
  const {
    centerSun, gameEnded, playerStates, activePlayers, currentPlayer, auctionStarted,
  } = gameState;
  return (
    <Container disableGutters>
      {gameEnded ? <EndInfo resetGame={resetGame} /> : <div /> }
      {(!gameEnded && isPlaying) ? (
        <Grid container spacing={{ xs: 2, md: 3 }}>
          <Grid xs={12}>
            <Paper elevation={3}>
              <CardGrid game={gameState} selectTileForSwap={handleSelectCardFromGrid} />
            </Paper>
          </Grid>
          <Grid xs={12} />
          <Grid xs={12}>
            <Paper elevation={3}>
              <PlayersInfo
                players={playerStates}
                auctionStarted={auctionStarted}
                active={activePlayers}
                current={currentPlayer}
                centerSun={centerSun}
                bidWithSun={handleBidAction}
                selectTile={handlePlayerSelectTile}
                actionsProps={{
                  onDraw: handleDraw,
                  onAuction: handleAuction,
                  disabled: gameEnded || !isPlaying,
                  resetGame,
                }}
              />
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <PlayerForm
          handleNewGame={handleNewGame}
          handleLoadGame={handleLoadGame}
          setAlert={setAlertData}
        />
      )}
      <Snackbar
        open={alertData.show}
        autoHideDuration={5000}
        onClose={() => setAlertData({ show: false, message: '' })}
      >
        <Alert
          onClose={() => setAlertData({ show: false, message: '' })}
          variant="filled"
          severity={alertData.level}
        >
          {alertData.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default Game;
