import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import { RaTile, SlotTile } from './Tile';
import type { GameState } from '../libs/game';

type CardGridProps = {
  game: GameState;
};
function CardGrid({
  game: {
    numRasPerRound, numRasThisRound, maxAuctionTiles,
  },
}: CardGridProps): JSX.Element {
  const renderRaTile = (idx: number) => (
    <Grid key={idx} xs={1}>
      <RaTile filled={idx < numRasThisRound} />
    </Grid>
  );
  const renderAuctionTile = (idx: number) => (
    <Grid key={idx} xs={2} sm={1}>
      <SlotTile />
    </Grid>
  );
  return (
    <>
      <Grid container spacing={{ xs: 2, md: 3 }} columns={{ xs: numRasPerRound }}>
        {[...Array(numRasPerRound).keys()].map(renderRaTile)}
      </Grid>
      <Grid container spacing={{ xs: 2, md: 3 }} columns={{ xs: maxAuctionTiles }}>
        {[...Array(maxAuctionTiles).keys()].map(renderAuctionTile)}
      </Grid>
    </>
  );
}

export default CardGrid;
