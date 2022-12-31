import React, { useCallback, useEffect, useState } from 'react';

import Grid from '@mui/material/Unstable_Grid2';
import {
  Backdrop,
  CircularProgress,
  Container,
  Paper,
} from '@mui/material';
import { closeSnackbar, enqueueSnackbar } from 'notistack';

import CardGrid from './CardGrid';
import EndInfo from './EndInfo';
import GameList from './GameList';
import PlayersInfo from './PlayersInfo';
import StartGameForm from './StartGameForm';

import { socket } from '../common';
import {
  DefaultGame,
  getTileAction,
} from '../libs/game';
import type {
  Game as GameState,
  Player,
  Tile,
} from '../libs/game';
import type {
  ApiResponse,
  ActionRequest,
  JoinLeaveRequest,
} from '../libs/request';

type GameProps = {
  // Parent component keeps track of whether we're in a game or not.
  isPlaying: boolean;
  setIsPlaying: (value: boolean) => void;
  playerName: string;
};

function Game({ playerName, isPlaying, setIsPlaying }: GameProps): JSX.Element {
  const GAME_STATE_KEY = 'LOCAL_GAME_STATE';
  const [game, setGame] = useState<GameState>(DefaultGame);
  const [gameId, setGameId] = useState<string>('');
  // When true and set to a valid index, swap occurs.
  const [swapInfo, setSwapInfo] = useState<[boolean, number]>([false, -1]);
  // Used when waiting between updates to game state.
  const [loading, setLoading] = useState<boolean>(false);
  // Track when we select a golden god.
  const [goldenGodSelected, setGoldeGodSelected] = useState(false);

  const handleLoadGame = useCallback((requestedId: string) => {
    const request: ActionRequest = { gameId: requestedId, command: 'LOAD' };
    socket.emit('act', request);
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
    if (!goldenGodSelected) {
      enqueueSnackbar(`Click your Golden God to atttempt a swap for ${tileName}.`, { variant: 'info' });
      setSwapInfo([true, idx]);
      return;
    }
    setSwapInfo([false, -1]);
    const request: ActionRequest = { gameId, command: `G${idx + 1}` };
    socket.emit('act', request);
  }, [gameId, goldenGodSelected]);
  const resetSelectCardFromGrid = useCallback(() => {
    setSwapInfo([false, -1]);
  }, []);
  const handlePlayerSelectTile = useCallback((player: Player, tile: Tile) => {
    let action = getTileAction(tile);
    if (!action) {
      enqueueSnackbar(`${tile.name} is not play-able.`, { variant: 'warning' });
      return;
    }
    if (action === 'SWAP') {
      const [/* shouldSwap */, swapIdx] = swapInfo;
      if (swapIdx < 0) {
        if (!goldenGodSelected) {
          // If already selected, we're deselecting.
          enqueueSnackbar('Click the card you wish to swap for your Golden God', { variant: 'info' });
        }
        setGoldeGodSelected(!goldenGodSelected);
        return;
      }
      setGoldeGodSelected(false);
      action = `G${swapIdx + 1}`;
    }
    const request: ActionRequest = { gameId, command: action };
    socket.emit('act', request);
  }, [gameId, swapInfo, goldenGodSelected]);

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
  const AIUIDelayMs = 1000;

  const onReset = useCallback(() => {
    closeSnackbar();
    setIsPlaying(false);
    setGameId('');
    window.localStorage.setItem(GAME_STATE_KEY, '{}');
    // Let the server know we've left the game.
    socket.emit('leave', { gameId } as JoinLeaveRequest);
  }, [gameId, setIsPlaying]);
  const onConnect = useCallback(() => {
    if (gameId) {
      // Join game if one is available.
      socket.emit('join', { gameId } as JoinLeaveRequest);
    }
  }, [gameId]);
  const updateGame = useCallback(({
    level, message, gameState, action, username, gameId: remoteGameId,
  }: ApiResponse) => {
    if (message || level || !gameState) {
      enqueueSnackbar(message || 'Unknown error.', { variant: level });
      return;
    }
    if (remoteGameId) {
      setGameId(remoteGameId);
    }
    setIsPlaying(true);
    setSwapInfo([false, -1]); // Reset swap info.
    setGame(gameState);
    if (action !== 'LOAD') {
      enqueueSnackbar(`${username} performed action: ${action}`, { variant: 'info' });
    }
  }, [setIsPlaying]);
  const onUpdateGame = useCallback((resp: ApiResponse | ApiResponse[]) => {
    if (!Array.isArray(resp)) {
      updateGame(resp);
      return;
    }
    setLoading(true);
    resp.forEach((item: ApiResponse, idx: number) => {
      if (idx > 0 || idx < resp.length - 1) {
        setTimeout(() => updateGame(item), idx * AIUIDelayMs);
      }
    });
    setTimeout(() => {
      setLoading(false);
      updateGame(resp[resp.length - 1]);
    }, (resp.length - 1) * AIUIDelayMs);
  }, [updateGame]);
  const onSpectate = useCallback((isSpectating: boolean) => {
    if (isSpectating) {
      enqueueSnackbar('In Spectator Mode', { variant: 'success', persist: true });
    }
  }, []);

  useEffect(() => {
    socket.on('connect', onConnect);
    return () => {
      socket.off('connect', onConnect);
    };
  }, [onConnect]);
  useEffect(() => {
    socket.on('disconnect', onReset);
    return () => {
      socket.off('disconnect', onReset);
    };
  }, [onReset]);
  useEffect(() => {
    socket.on('logout', onReset);
    return () => {
      socket.off('logout', onReset);
    };
  }, [onReset]);
  useEffect(() => {
    socket.on('update', onUpdateGame);
    return () => {
      socket.off('update', onUpdateGame);
    };
  }, [onUpdateGame]);
  useEffect(() => {
    socket.on('spectate', onSpectate);
    return () => {
      socket.off('spectate', onSpectate);
    };
  }, [onSpectate]);

  const { auctionTileValues, unrealizedPoints, gameState } = game;
  const {
    centerSun, gameEnded, playerStates, activePlayers, currentPlayer,
    auctionStarted, auctionSuns,
  } = gameState;
  return (
    <Container disableGutters>
      {(isPlaying) ? (
        <Grid container spacing={{ xs: 2, md: 3 }}>
          {gameEnded ? (
            <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
              <EndInfo players={playerStates} />
            </Grid>
          ) : null}
          <Grid xs={12}>
            <Paper elevation={3}>
              <CardGrid
                game={gameState}
                selectTileForSwap={handleSelectCardFromGrid}
                resetSelectTileForSwap={resetSelectCardFromGrid}
                selectedTileIdx={swapInfo[1]}
              />
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
                goldenGodSelected={goldenGodSelected}
                actionsProps={{
                  onDraw: handleDraw,
                  onAuction: handleAuction,
                  disabled: gameEnded || !isPlaying,
                  pointsIfWin: null,
                }}
              />
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <Grid container spacing={{ xs: 2, md: 3 }}>
          <Grid xs={12}>
            <StartGameForm />
          </Grid>
          <Grid xs={12} />
          <Grid xs={12}>
            <GameList user={playerName} handleLoadGame={handleLoadGame} />
          </Grid>
        </Grid>
      )}
      <Backdrop open={loading}>
        <CircularProgress color="inherit" />
      </Backdrop>
    </Container>
  );
}

export default Game;
