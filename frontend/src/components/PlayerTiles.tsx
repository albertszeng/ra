import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import { PlayerTile } from './Tile';
import type { Tile as TileInfo } from '../libs/game';

type PlayerTilesProps = {
  tiles: TileInfo[];
};

function PlayerTiles({ tiles }: PlayerTilesProps): JSX.Element {
  const renderTile = (tile: TileInfo) => {
    const { name } = tile;
    return (
      <Grid key={name} xs={2} sm={1}>
        <PlayerTile tile={tile} count={1} />
      </Grid>
    );
  };
  return (
    <Grid container spacing={{ xs: 1 }} columns={{ xs: tiles.length }}>
      {tiles.map(renderTile)}
    </Grid>
  );
}

export default PlayerTiles;
