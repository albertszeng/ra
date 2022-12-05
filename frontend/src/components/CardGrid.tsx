import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import { RaTile, SlotTile, Tile } from './Tile';
import type { GameState } from '../libs/game';

type CardGridProps = {
  game: GameState;
};
function CardGrid({
  game: {
    numRasPerRound, numRasThisRound, maxAuctionTiles, auctionTiles,
  },
}: CardGridProps): JSX.Element {
  const renderRaTile = (idx: number) => (
    <Grid key={idx} xs={1}>
      <RaTile filled={idx < numRasThisRound} />
    </Grid>
  );
  const renderAuctionTile = (idx: number) => {
    let tile = <SlotTile />;
    if (idx < auctionTiles.length) {
      const { name } = auctionTiles[idx];
      tile = <Tile altText={name} imageSrc={`${process.env.PUBLIC_URL}/assets/tiles/${name}.png`} />;
    }
    return (
      <Grid key={idx} xs={2} sm={1}>
        {tile}
      </Grid>
    );
  };
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
