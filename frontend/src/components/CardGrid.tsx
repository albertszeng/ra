import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import { RaTile } from './Tile';
import type { GameState } from '../libs/game';

type CardGridProps = {
  game: GameState;
};
function CardGrid({ game: { numRasPerRound, numRasThisRound } }: CardGridProps): JSX.Element {
  const renderRaTile = (idx: number) => (
    <Grid key={idx} xs={1}>
      <RaTile filled/* ={idx < numRasThisRound} */ />
    </Grid>
  );
  return (
    <Grid container spacing={{ xs: 2, md: 3 }} columns={{ xs: numRasPerRound }}>
      {[...Array(numRasPerRound).keys()].map(renderRaTile)}
    </Grid>
  );
}

export default CardGrid;
