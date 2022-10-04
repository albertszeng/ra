import React from 'react';
import styled from 'styled-components';
import CardGrid from './CardGrid';
import EndInfo from './EndInfo';
import PlayerInfo from './PlayerInfo';
import PlayerForm from './PlayerForm';
import type { Game as GameLib } from '../libs/game';

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

type GameProps = {
  game: GameLib;
};

function Game({ game } : GameProps): JSX.Element {
  const resetGame = () => {
    alert('reset is not impleted');
  };
  const isPlaying = false;
  const gameEnded = false;
  return (
    <GameContainer>
      {gameEnded ? <EndInfo resetGame={resetGame} /> : <div /> }
      {(!gameEnded && isPlaying) ? (
        <CardGrid />
      ) : (
        <StartContainer>
          <PlayerForm handleSubmit={() => { /* no op */ }} />
        </StartContainer>
      )}
      <PlayerInfo />
    </GameContainer>
  );
}

export default Game;
