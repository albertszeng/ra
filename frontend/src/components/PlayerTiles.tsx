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

  const tileCounts = tiles.reduce((counter, tile: TileInfo) => {
    const { name } = tile;
    const currentCount = (counter[name]) ? counter[name][0] + 1 : 1;
    return {
      ...counter, [name]: [currentCount, tile] as [number, TileInfo],
    };
  }, {} as { [key: string]: [number, TileInfo] });
  const renderTile = ([count, tile]: [number, TileInfo]) => {
    const { name, tileType } = tile;
    return (
      <ImageListItem key={name}>
        <Tile tile={tile} />
        <ImageListItemBar
          title={name}
          subtitle={tileType}
          actionIcon={(
            <Avatar sx={{ bgcolor: deepPurple[500] }}>
              {count}
            </Avatar>
          )}
        />
      </ImageListItem>
    );
  };

  return (
    <ImageList sx={{ height }} cols={(matchDownMd) ? 3 : 5} rowHeight={height}>
      {Object.values(tileCounts).map(renderTile)}
    </ImageList>
  );
}

export default PlayerTiles;
