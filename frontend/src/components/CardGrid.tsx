import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import { RaTile, SlotTile, Tile } from './Tile';
import type { GameState, Tile as TileInfo } from '../libs/game';

type CardGridProps = {
  game: GameState;
  // Called when a player selects one of the cards in the grid.
  selectTileForSwap: (idx: number, tile: TileInfo) => void;
};
function CardGrid({
  game: {
    numRasPerRound, numRasThisRound, maxAuctionTiles, auctionTiles,
  }, selectTileForSwap,
}: CardGridProps): JSX.Element {
  const renderRaTile = (idx: number) => (
    <Grid key={idx} xs={2} sm={1}>
      <RaTile filled={idx < numRasThisRound} />
    </Grid>
  );
  const renderAuctionTile = (idx: number) => {
    let tile = <SlotTile />;
    if (idx < auctionTiles.length) {
      tile = <Tile tile={auctionTiles[idx]} />;
    }
    return (
      <Grid
        onClick={() => selectTileForSwap(idx, auctionTiles[idx])}
        key={idx}
        xs={2}
        sm={1}
      >
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
