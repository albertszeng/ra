import styled from 'styled-components';
import React from 'react';
import CardGrid from './CardGrid';
import EndInfo from './EndInfo';
import PlayerInfo from './PlayerInfo';
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

const IntroText = styled.p`
  font-size: 2rem;
`;

const StartButton = styled.button`
  width: 40%;
  border-radius: 1rem;
  border: none;
  font-size: 2rem;
  padding-block: 0.5rem;
  background-color: var(--violet-blue-crayola);
  color: var(--off-white);
  letter-spacing: 0.2rem;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: var(--oxford-blue-light) 0px 1px 3px;
`;

type GameProps = {
  game: GameLib,
};

function Game({ game } : GameProps): JSX.Element {
  const resetGame = () => {};
  const isPlaying = true;
  const gameEnded = false;
  return (
    <GameContainer>
      {gameEnded ? <EndInfo resetGame={resetGame} /> : <div /> }
      {(!gameEnded && isPlaying) ? (
        <CardGrid />
      ) : (
        <StartContainer>
          <IntroText>Find all of the matching pairs of cards!</IntroText>
          <StartButton>Start</StartButton>
        </StartContainer>
      )}
      <PlayerInfo />
    </GameContainer>
  );
}

export default Game;
