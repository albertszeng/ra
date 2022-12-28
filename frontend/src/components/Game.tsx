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

import { socket } from '../common';
import {
  DefaultGame,
  getTileAction,
} from '../libs/game';
import type {
  AlertData,
  Game as GameState,
  Player,
  Tile,
} from '../libs/game';
import type {
  ApiResponse,
  ActionRequest,
  DeleteRequest,
  JoinLeaveRequest,
  StartRequest,
  StartResponse,
} from '../libs/request';

type GameProps = {
  // Sets an alert at the highest level.
  setAlert: (alert: AlertData) => void;
  playerName: string;
};

function Game({ playerName, setAlert }: GameProps): JSX.Element {
  const GAME_STATE_KEY = 'LOCAL_GAME_STATE';
  const [game, setGame] = useState<GameState>(DefaultGame);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameId, setGameId] = useState<string>('');
  // When true and set to a valid index, swap occurs.
  const [swapInfo, setSwapInfo] = useState<[boolean, number]>([false, -1]);

  const handleNewGame = useCallback((players: string[]) => {
    const request: StartRequest = { playerNames: players, numPlayers: players.length };
    socket.emit('start_game', request);
  }, []);
  const handleLoadGame = useCallback((requestedId: string) => {
    const request: ActionRequest = { gameId: requestedId, command: 'LOAD' };
    socket.emit('act', request);
  }, []);
  const handleDeleteGame = useCallback((toDeleteId: string) => {
    const request: DeleteRequest = { gameId: toDeleteId };
    socket.emit('delete', request);
  }, []);
  const handleDraw = useCallback(() => {
    const request: ActionRequest = { gameId, command: 'DRAW' };
    socket.emit('act', request);
  }, [gameId]);
  const handleAuction = useCallback(() => {
    const request: ActionRequest = { gameId, command: 'AUCTION' };
    socket.emit('act', request);
  }, [gameId]);
  const handleBidAction = useCallback((idx: number) => {
    // 1-indexed. 0 corresponds to passing in which case idx === -1.
    const request: ActionRequest = { gameId, command: `B${idx + 1}` };
    socket.emit('act', request);
  }, [gameId]);
  const handleSelectCardFromGrid = useCallback((idx: number, { name: tileName }: Tile) => {
    const [shouldSwap/* swapIdx */] = swapInfo;
    if (!shouldSwap) {
      setAlert({ show: true, message: `Click your Golden God to atttempt a swap for ${tileName}.`, level: 'info' });
      setSwapInfo([shouldSwap, idx]);
      return;
    }
    const request: ActionRequest = { gameId, command: `G${idx + 1}` };
    socket.emit('act', request);
  }, [gameId, swapInfo, setAlert]);
  const handlePlayerSelectTile = useCallback((player: Player, tile: Tile) => {
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
    const request: ActionRequest = { gameId, command: action };
    socket.emit('act', request);
  }, [gameId, swapInfo, setAlert]);

  const resetGame = useCallback(() => {
    setIsPlaying(false);
    setGameId('');
    window.localStorage.setItem(GAME_STATE_KEY, '{}');
    // Let the server know we've left the game.
    socket.emit('leave', { gameId } as JoinLeaveRequest);
  }, [gameId]);

  useEffect(() => {
    // When the gameId changes, store in local storage.
    if (gameId) {
      window.localStorage.setItem(GAME_STATE_KEY, JSON.stringify({ gameId }));
    }
  }, [gameId]);
  useEffect(() => {
    // On refresh of component, get latest game state if we had a gameId.
    const { gameId: restoredGameId } = JSON.parse(
      window.localStorage.getItem(GAME_STATE_KEY) || '{}',
    ) as { gameId?: string };
    if (restoredGameId) {
      handleLoadGame(restoredGameId);
    }
  }, [handleLoadGame]);
  const [timestampMs, setTimestampMs] = useState(Date.now());
  const AIUIDelayMs = 2000;
  useEffect(() => {
    socket.on('disconnect', () => {
      resetGame();
    });
    return () => {
      socket.off('disconnect');
    };
  }, [resetGame]);
  useEffect(() => {
    socket.on('start_game', ({ gameId: id, gameState: state } : StartResponse) => {
      setIsPlaying(true);
      setGameId(id);
      setGame((prevGame: GameState) => ({ ...prevGame, ...state }));
      // Let the server know we've joined.
      socket.emit('join', { gameId: id } as JoinLeaveRequest);
    });
    return () => {
      socket.off('start_game');
    };
  }, []);
  useEffect(() => {
    socket.on('update', ({
      level, message, gameState, action, username, gameId: remoteGameId,
    }: ApiResponse) => {
      const now = Date.now();
      if (now >= timestampMs + AIUIDelayMs) {
        setTimestampMs(now);
        if (message || level || !gameState) {
          setAlert({ show: true, message: message || 'Unknown error.', level });
          return;
        }
        if (remoteGameId) {
          setGameId(remoteGameId);
        }
        setIsPlaying(true);
        setSwapInfo([false, -1]); // Reset swap info.
        setGame(gameState);
        setAlert({ show: true, message: `${username} performed action: ${action}`, level: 'info' });
      } else {
        // Increase timestamp so next action happens at at least this delay.
        setTimestampMs((prev) => prev + AIUIDelayMs);
        // Need to enqueue the action to execute later.
        setTimeout(() => {
          if (message || level || !gameState) {
            setAlert({ show: true, message: message || 'Unknown error.', level });
            return;
          }
          if (remoteGameId) {
            setGameId(remoteGameId);
          }
          setIsPlaying(true);
          setSwapInfo([false, -1]); // Reset swap info.
          setGame(gameState);
          setAlert({ show: true, message: `${username} performed action: ${action}`, level: 'info' });
        }, (timestampMs + AIUIDelayMs) - now);
      }
    });
    return () => {
      socket.off('update');
    };
  }, [setAlert, timestampMs]);
  useEffect(() => {
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
    };
  }, [setAlert]);

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
          handleDeleteGame={handleDeleteGame}
          setAlert={setAlert}
        />
      )}
    </Container>
  );
}

export default Game;
