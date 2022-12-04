import React, { useCallback, useEffect, useState } from 'react';
import styled from 'styled-components';

import Actions from './Actions';
import CardGrid from './CardGrid';
import EndInfo from './EndInfo';
import PlayersInfo from './PlayersInfo';
import PlayerForm from './PlayerForm';

import { DefaultGame, handleCommand, startGame } from '../libs/game';
import type { Game as GameState } from '../libs/game';

const GameContainer = styled.main`
  width: min(99%, 1000px);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 82vh;
  /* border: 1px solid var(--oxford-blue); */
  box-shadow: var(--oxford-blue-light) 0px 1px 6px;
  border-radius: 0.5rem;
  padding: 2rem 0 0 0;
  background-color: var(--mauvelous-light);
`;

const StartContainer = styled.div`
  text-align: center;
  margin-top: auto;
  font-size: 2rem;
`;

function Game(): JSX.Element {
  const GAME_STATE_KEY = 'LOCAL_GAME_STATE';
  const [game, setGame] = useState<GameState>(DefaultGame);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameId, setGameId] = useState<string | null>(null);

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
    }
  }, []);

  const handleNewGame = useCallback(async (players: string[]) => {
    const {
      message,
      gameId: remoteGameId,
      gameState,
    } = await startGame(players);
    if (message || !remoteGameId || !gameState) {
      alert(message);
      return;
    }
    setIsPlaying(true);
    setGameId(remoteGameId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);
  const handleLoadGame = useCallback(async (requestedId: string) => {
    const { message, gameState } = await handleCommand(requestedId, 'LOAD');
    if (message || !gameState) {
      alert(message);
      return;
    }
    setIsPlaying(true);
    setGameId(requestedId);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);
  const handleDraw = useCallback(async () => {
    if (!gameId) {
      return;
    }
    const { message, gameState } = await handleCommand(gameId, 'DRAW');
    if (message || !gameState) {
      alert(message);
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId]);
  const handleAuction = useCallback(async () => {
    if (!gameId) {
      return;
    }
    const { message, gameState } = await handleCommand(gameId, 'AUCTION');
    if (message || !gameState) {
      alert(message);
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId]);
  const handleActionBid = useCallback(async (idx: number) => {
    if (!gameId) {
      return;
    }
    const { message, gameState } = await handleCommand(gameId, `B${idx + 1}`);
    if (message || !gameState) {
      alert(message);
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, [gameId]);

  const resetGame = () => {
    setIsPlaying(false);
  };

  const { gameState } = game;
  const {
    gameEnded, playerStates, activePlayers, currentPlayer, auctionStarted,
  } = gameState;
  return (
    <GameContainer>
      {gameEnded ? <EndInfo resetGame={resetGame} /> : <div /> }
      {(!gameEnded && isPlaying) ? (
        <CardGrid game={gameState} />
      ) : (
        <StartContainer>
          <PlayerForm
            handleNewGame={handleNewGame}
            handleLoadGame={handleLoadGame}
          />
        </StartContainer>
      )}
      <PlayersInfo
        players={playerStates}
        auctionStarted={auctionStarted}
        active={activePlayers}
        current={currentPlayer}
        bidWithSun={handleActionBid}
      />
      <Actions
        onDraw={handleDraw}
        onAuction={handleAuction}
        disabled={gameEnded || !isPlaying}
      />
    </GameContainer>
  );
}

export default Game;
