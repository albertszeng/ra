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
  const [name, setName] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameId, setGameId] = useState<string>('');
  const [alertData, setAlertData] = useState<AlertData>(
    { show: false, message: '', level: 'info' },
  );
  // When true and set to a valid index, swap occurs.
  const [swapInfo, setSwapInfo] = useState<[boolean, number]>([false, -1]);

  const handleNewGame = useCallback(async (players: string[], user: string) => {
    const {
      message,
      level,
      gameId: remoteGameId,
      gameState,
    } = await startGame(players, user);
    if (message || level || !remoteGameId || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setName(user);
    setIsPlaying(true);
    setGameId(remoteGameId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);
  const handleLoadGame = useCallback(async (requestedId: string, user: string) => {
    const { level, message, gameState } = await handleCommand(requestedId, user, 'LOAD');
    if (message || level || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    // Also let the server know we've joined again.
    socket.emit('join', { gameId: requestedId, name: user });
    setName(user);
    setIsPlaying(true);
    setGameId(requestedId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);
  const handleDraw = useCallback(async () => {
    if (!gameId) {
      setAlertData({ show: true, message: 'No active game.', level: 'warning' });
      return;
    }
    if (!name) {
      setAlertData({ show: true, message: 'No player found. Reload?.', level: 'warning' });
      return;
    }
    const { level, message, gameState } = await handleCommand(gameId, name, 'DRAW');
    if (level || message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, name]);
  const handleAuction = useCallback(async () => {
    if (!gameId) {
      setAlertData({ show: true, message: 'No active game.', level: 'warning' });
      return;
    }
    if (!name) {
      setAlertData({ show: true, message: 'No player found. Reload?.', level: 'warning' });
      return;
    }
    const { level, message, gameState } = await handleCommand(gameId, name, 'AUCTION');
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, name]);
  const handleBidAction = useCallback(async (idx: number) => {
    if (!gameId) {
      return;
    }
    if (!name) {
      setAlertData({ show: true, message: 'No player found. Reload?.', level: 'warning' });
      return;
    }
    // 1-indexed. 0 corresponds to passing in which case idx === -1.
    const { level, message, gameState } = await handleCommand(gameId, name, `B${idx + 1}`);
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, name]);
  const handleSelectCardFromGrid = useCallback(async (idx: number, { name: tileName }: Tile) => {
    if (!gameId) {
      return;
    }
    if (!name) {
      setAlertData({ show: true, message: 'No player found. Reload?.', level: 'warning' });
      return;
    }
    const [shouldSwap] = swapInfo;
    if (!shouldSwap) {
      setAlertData({ show: true, message: `Click your Golden God to atttempt a swap for ${tileName}.`, level: 'info' });
      setSwapInfo([shouldSwap, idx]);
      return;
    }
    // Server command is 1-indexed, so we increment here.
    const { level, message, gameState } = await handleCommand(gameId, name, `G${idx + 1}`);
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo, name]);
  const handlePlayerSelectTile = useCallback(async (player: Player, tile: Tile) => {
    if (!gameId) {
      setAlertData({ show: true, message: 'No active game.', level: 'info' });
      return;
    }
    if (!name) {
      setAlertData({ show: true, message: 'No player found. Reload?.', level: 'warning' });
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

    const { level, message, gameState } = await handleCommand(gameId, name, action);
    if (message || !gameState) {
      setAlertData({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setAlertData({ show: true, message: `Performed action: ${action}`, level: 'info' });
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo, name]);

  const resetGame = useCallback(() => {
    setIsPlaying(false);
    setGameId('');
    setName('');
    window.localStorage.setItem(GAME_STATE_KEY, '{}');
    // Let the server know we've left the game.
    socket.emit('leave', { gameId, name });
  }, [gameId, name]);

  useEffect(() => {
    // When the gameId changes, store in local storage.
    if (gameId && name) {
      window.localStorage.setItem(GAME_STATE_KEY, JSON.stringify({ gameId, name }));
    }
  }, [gameId, name]);
  useEffect(() => {
    // On refresh of component, get latest game state if we had a gameId.
    const { gameId: restoredGameId, name: restoredName } = JSON.parse(
      window.localStorage.getItem(GAME_STATE_KEY) || '{}',
    ) as { gameId?: string, name?: string };
    if (restoredGameId && restoredName) {
      // Attempt to join the game again.
      // eslint-disable-next-line @typescript-eslint/naming-convention
      const _ = handleLoadGame(restoredGameId, restoredName);
    }
  }, [handleLoadGame]);
  useEffect(() => {
    socket.on('connect', () => {
      if (gameId && name) {
        socket.emit('join', { gameId, name });
      }
    });
    socket.on('disconnect', (reason) => {
      if (reason === 'io server disconnect') {
        socket.connect();
      }
    });
    socket.on('update', ({ gameState }: ApiResponse) => {
      if (gameState) {
        setGame(gameState);
      }
    });
    socket.on('spectate', () => {
      setAlertData({
        show: true,
        message: 'In Spectator Mode',
        level: 'success',
        permanent: true,
      });
    });
    return () => {
      socket.off('update');
      socket.off('disconnect');
      socket.off('connect');
    };
  }, [gameId, name]);

  const { gameState } = game;
  const {
    centerSun, gameEnded, playerStates, activePlayers, currentPlayer,
    auctionStarted, auctionSuns,
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
                localName={name}
                players={playerStates}
                auctionStarted={auctionStarted}
                active={activePlayers}
                current={currentPlayer}
                centerSun={centerSun}
                auctionSuns={auctionSuns}
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
        autoHideDuration={(alertData.permanent) ? undefined : 5000}
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
