import React, { useCallback, useEffect, useState } from 'react';

import Grid from '@mui/material/Unstable_Grid2';
import {
  Container,
  Paper,
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

type GameProps = {
  // Sets an alert at the highest level.
  setAlert: (alert: AlertData) => void;
  playerName: string;
  // This is temporarily here for bc. Will remove eventually.
  setPlayerName: (playerName: string) => void;
};

function Game({ playerName, setAlert, setPlayerName }: GameProps): JSX.Element {
  const GAME_STATE_KEY = 'LOCAL_GAME_STATE';
  const [game, setGame] = useState<GameState>(DefaultGame);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameId, setGameId] = useState<string>('');
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
      setAlert({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setPlayerName(user);
    setIsPlaying(true);
    setGameId(remoteGameId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [setAlert, setPlayerName]);
  const handleLoadGame = useCallback(async (requestedId: string, user: string) => {
    const { level, message, gameState } = await handleCommand(requestedId, user, 'LOAD');
    if (message || level || !gameState) {
      setAlert({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    // Also let the server know we've joined again.
    socket.emit('join', { gameId: requestedId, name: user });
    setPlayerName(user);
    setIsPlaying(true);
    setGameId(requestedId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [setAlert, setPlayerName]);
  const handleDraw = useCallback(async () => {
    if (!gameId) {
      setAlert({ show: true, message: 'No active game.', level: 'warning' });
      return;
    }
    const { level, message, gameState } = await handleCommand(gameId, playerName, 'DRAW');
    if (level || message || !gameState) {
      setAlert({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, playerName, setAlert]);
  const handleAuction = useCallback(async () => {
    if (!gameId) {
      setAlert({ show: true, message: 'No active game.', level: 'warning' });
      return;
    }
    const { level, message, gameState } = await handleCommand(gameId, playerName, 'AUCTION');
    if (message || !gameState) {
      setAlert({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, playerName, setAlert]);
  const handleBidAction = useCallback(async (idx: number) => {
    if (!gameId) {
      return;
    }
    // 1-indexed. 0 corresponds to passing in which case idx === -1.
    const { level, message, gameState } = await handleCommand(gameId, playerName, `B${idx + 1}`);
    if (message || !gameState) {
      setAlert({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, playerName, setAlert]);
  const handleSelectCardFromGrid = useCallback(async (idx: number, { name: tileName }: Tile) => {
    if (!gameId) {
      return;
    }
    const [shouldSwap] = swapInfo;
    if (!shouldSwap) {
      setAlert({ show: true, message: `Click your Golden God to atttempt a swap for ${tileName}.`, level: 'info' });
      setSwapInfo([shouldSwap, idx]);
      return;
    }
    // Server command is 1-indexed, so we increment here.
    const { level, message, gameState } = await handleCommand(gameId, playerName, `G${idx + 1}`);
    if (message || !gameState) {
      setAlert({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo, playerName, setAlert]);
  const handlePlayerSelectTile = useCallback(async (player: Player, tile: Tile) => {
    if (!gameId) {
      setAlert({ show: true, message: 'No active game.', level: 'info' });
      return;
    }
    let action = getTileAction(tile);
    if (!action) {
      setAlert({ show: true, message: `${tile.name} is not play-able.`, level: 'warning' });
      return;
    }
    if (action === 'SWAP') {
      const [/* shouldSwap */, swapIdx] = swapInfo;
      if (swapIdx < 0) {
        setAlert({ show: true, message: 'Click the card you wish to swap for your Golden God', level: 'info' });
        return;
      }
      action = `G${swapIdx + 1}`;
    }

    const { level, message, gameState } = await handleCommand(gameId, playerName, action);
    if (message || !gameState) {
      setAlert({ show: true, message: message || 'Unknown error.', level });
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setAlert({ show: true, message: `Performed action: ${action}`, level: 'info' });
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo, playerName, setAlert]);

  const resetGame = useCallback(() => {
    setIsPlaying(false);
    setGameId('');
    // TODO: remove.
    setPlayerName('');
    window.localStorage.setItem(GAME_STATE_KEY, '{}');
    // Let the server know we've left the game.
    socket.emit('leave', { gameId, name: playerName });
  }, [gameId, playerName, setPlayerName]);

  useEffect(() => {
    // When the gameId changes, store in local storage.
    if (gameId) {
      window.localStorage.setItem(GAME_STATE_KEY, JSON.stringify({ gameId, playerName }));
    }
  }, [gameId, playerName]);
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
  const [timestampMs, setTimestampMs] = useState(Date.now());
  const AIUIDelayMs = 2000;
  useEffect(() => {
    socket.on('connect', () => {
      if (gameId) {
        socket.emit('join', { gameId, name: playerName });
      }
    });
    socket.on('disconnect', () => {
      resetGame();
    });
    socket.on('update', ({ level, message, gameState }: ApiResponse) => {
      const now = Date.now();
      if (now >= timestampMs + AIUIDelayMs) {
        setTimestampMs(now);
        if (message || level || !gameState) {
          setAlert({ show: true, message: message || 'Unknown error.', level });
          return;
        }
        setGame(gameState);
      } else {
        // Increase timestamp so next action happens at at least this delay.
        setTimestampMs((prev) => prev + AIUIDelayMs);
        // Need to enqueue the action to execute later.
        setTimeout(() => {
          if (message || level || !gameState) {
            setAlert({ show: true, message: message || 'Unknown error.', level });
            return;
          }
          setGame(gameState);
        }, (timestampMs + AIUIDelayMs) - now);
      }
    });
    socket.on('spectate', () => {
      setAlert({
        show: true,
        message: 'In Spectator Mode',
        level: 'success',
        permanent: true,
      });
    });
    return () => {
      socket.off('spectate');
      socket.off('update');
      socket.off('disconnect');
      socket.off('connect');
    };
  }, [gameId, playerName, resetGame, timestampMs, setAlert]);

  const { auctionTileValues, unrealizedPoints, gameState } = game;
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
                localName={playerName}
                players={playerStates}
                playerPointsIfWin={auctionTileValues}
                playerEstimatedDelta={unrealizedPoints}
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
                  pointsIfWin: null,
                }}
              />
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <PlayerForm
          handleNewGame={handleNewGame}
          handleLoadGame={handleLoadGame}
          setAlert={setAlert}
        />
      )}
    </Container>
  );
}

export default Game;
