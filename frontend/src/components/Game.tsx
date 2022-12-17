import React, { useCallback, useEffect, useState } from 'react';

import Grid from '@mui/material/Unstable_Grid2';
import {
  Alert,
  AlertTitle,
  Container,
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
  const [alertMsg, setAlertMsg] = useState<string>('');
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
      gameId: remoteGameId,
      gameState,
    } = await startGame(players);
    if (message || !remoteGameId || !gameState) {
      setAlertMsg(message || 'Unknown error.');
      return;
    }
    setIsPlaying(true);
    setGameId(remoteGameId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);
  const handleLoadGame = useCallback(async (requestedId: string) => {
    const { message, gameState } = await handleCommand(requestedId, 'LOAD');
    if (message || !gameState) {
      setAlertMsg(message || 'Unknown error.');
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
      setAlertMsg('No active game.');
      return;
    }
    const { message, gameState } = await handleCommand(gameId, 'DRAW');
    if (message || !gameState) {
      setAlertMsg(message || 'Unknown error.');
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId]);
  const handleAuction = useCallback(async () => {
    if (!gameId) {
      setAlertMsg('No active game.');
      return;
    }
    const { message, gameState } = await handleCommand(gameId, 'AUCTION');
    if (message || !gameState) {
      setAlertMsg(message || 'Unknown error.');
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
      setAlertMsg(message || 'Unknown error.');
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
      setAlertMsg(`Click your Golden God to atttempt a swap for ${name}.`);
      setSwapInfo([shouldSwap, idx]);
      return;
    }
    // Server command is 1-indexed, so we increment here.
    const { message, gameState } = await handleCommand(gameId, `G${idx + 1}`);
    if (message || !gameState) {
      setAlertMsg(message || 'Unknown error.');
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo]);
  const handlePlayerSelectTile = useCallback(async (player: Player, tile: Tile) => {
    if (!gameId) {
      setAlertMsg('No active game.');
      return;
    }
    let action = getTileAction(tile);
    if (!action) {
      setAlertMsg(`${tile.name} is not play-able.`);
      return;
    }
    if (action === 'SWAP') {
      const [/* shouldSwap */, swapIdx] = swapInfo;
      if (swapIdx < 0) {
        setAlertMsg('Click the card you wish to swap for your Golden God');
        return;
      }
      action = `G${swapIdx + 1}`;
    }

    const { message, gameState } = await handleCommand(gameId, action);
    if (message || !gameState) {
      setAlertMsg(message || 'Unknown error.');
      return;
    }
    setSwapInfo([false, -1]); // Reset swap info.
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId, swapInfo]);

  const resetGame = () => {
    setIsPlaying(false);
    // Let the server know we've left the game.
    socket.emit('leave', { gameId });
  };

  const { gameState } = game;
  const {
    gameEnded, playerStates, activePlayers, currentPlayer, auctionStarted,
  } = gameState;
  return (
    <Container disableGutters>
      {gameEnded ? <EndInfo resetGame={resetGame} /> : <div /> }
      {(!gameEnded && isPlaying) ? (
        <Grid container spacing={{ xs: 2, md: 3 }}>
          <Grid xs={12}>
            <CardGrid game={gameState} selectTileForSwap={handleSelectCardFromGrid} />
          </Grid>
          <PlayersInfo
            players={playerStates}
            auctionStarted={auctionStarted}
            active={activePlayers}
            current={currentPlayer}
            bidWithSun={handleBidAction}
            selectTile={handlePlayerSelectTile}
            actionsProps={{
              onDraw: handleDraw,
              onAuction: handleAuction,
              disabled: gameEnded || !isPlaying,
              resetGame,
            }}
          />
          <Snackbar
            open={!!alertMsg}
            autoHideDuration={2500}
            onClose={() => setAlertMsg('')}
          >
            <Alert
              onClose={() => setAlertMsg('')}
              variant="filled"
              severity="error"
            >
              <AlertTitle>Invalid Input</AlertTitle>
              {alertMsg}
            </Alert>
          </Snackbar>
        </Grid>
      ) : (
        <PlayerForm
          handleNewGame={handleNewGame}
          handleLoadGame={handleLoadGame}
        />
      )}
    </Container>
  );
}

export default Game;
