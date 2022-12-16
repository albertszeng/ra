import React from 'react';

import {
  Avatar,
  ImageList,
  ImageListItem,
  ImageListItemBar,
  useMediaQuery,
} from '@mui/material';
import { deepPurple } from '@mui/material/colors';
import { useTheme } from '@mui/material/styles';

import { Tile } from './Tile';
import type { Tile as TileInfo } from '../libs/game';

type PlayerTilesProps = {
  tiles: TileInfo[];
};

function PlayerTiles({ tiles }: PlayerTilesProps): JSX.Element {
  const theme = useTheme();
  const matchDownMd = useMediaQuery(theme.breakpoints.down('sm'));
  const height = 100;
  const renderTile = (tile: TileInfo) => {
    const { name, tileType } = tile;
    return (
      <ImageListItem key={name}>
        <Tile tile={tile} />
        <ImageListItemBar
          title={name}
          subtitle={tileType}
          actionIcon={<Avatar sx={{ bgcolor: deepPurple[500] }}>1</Avatar>}
        />
      </ImageListItem>
    );
  };
  return (
    <ImageList sx={{ height }} cols={(matchDownMd) ? 3 : 5} rowHeight={height}>
      {tiles.map(renderTile)}
    </ImageList>
  );
}

export default PlayerTiles;
