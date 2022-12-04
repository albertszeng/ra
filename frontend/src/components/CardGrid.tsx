import React from 'react';

import { RaTile } from './Tile';
import type { GameState } from '../libs/game';

type CardGridProps = {
  game: GameState;
};
function CardGrid({ game }: CardGridProps): JSX.Element {
  return (
    <>
      {[...Array(game.numRasPerRound).keys()].map(() => <RaTile />)}
    </>
  );
}

export default CardGrid;
