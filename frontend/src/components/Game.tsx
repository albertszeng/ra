import React, { useCallback, useEffect, useState } from 'react';
import styled from 'styled-components';

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

  // Store local game state to storage.
  useEffect(() => {
    if (game !== DefaultGame) {
      window.localStorage.setItem(GAME_STATE_KEY, JSON.stringify({
        game, isPlaying,
      }));
    }
  }, [game, isPlaying]);
  useEffect(() => {
    const data = window.localStorage.getItem(GAME_STATE_KEY);
    if (data !== null) {
      const {
        game: restoredGame,
        isPlaying: restoredIsPlaying,
      } = JSON.parse(data) as { game: GameState, isPlaying: boolean };
      setGame(restoredGame);
      setIsPlaying(restoredIsPlaying);
    }
  }, []);

  const handleNewGame = useCallback(async (players: string[]) => {
    const {
      message,
      gameId,
      gameState,
    } = await startGame(players);
    if (message || !gameId || !gameState) {
      alert(message);
      return;
    }
    setIsPlaying(true);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);
  const handleLoadGame = useCallback(async (gameId: string) => {
    const { message, gameState } = await handleCommand(gameId, 'LOAD');
    if (message || !gameState) {
      alert(message);
      return;
    }
    setIsPlaying(true);
    setGame((prevGame: GameState) => ({ ...prevGame, ...gameState }));
  }, []);

  const resetGame = () => {
    setIsPlaying(false);
  };

  const { gameState } = game;
  const {
    gameEnded, playerStates, activePlayers, currentPlayer,
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
        active={activePlayers}
        current={currentPlayer}
      />
    </GameContainer>
  );
}

export default Game;
