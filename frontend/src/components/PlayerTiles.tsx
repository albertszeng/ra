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
  onTileClick: (tile: TileInfo) => void;
};

function PlayerTiles({ tiles, onTileClick }: PlayerTilesProps): JSX.Element {
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('sm'));
  const matchDownMd = useMediaQuery(theme.breakpoints.down('md'));
  const height = (matchDownSm) ? undefined : 200;
  const rowHeight = (height) ? (height - 10) / 2 : undefined;

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
      <ImageListItem key={name} onClick={() => onTileClick(tile)}>
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
  // eslint-disable-next-line no-nested-ternary
  const cols = (matchDownSm) ? 3 : (matchDownMd) ? 5 : 6;
  const values = Object.values(tileCounts);
  return (
    (values.length > 0) ? (
      <ImageList sx={{ height }} cols={cols} rowHeight={rowHeight}>
        {values.map(renderTile)}
      </ImageList>
    ) : <div />
  );
}

export default PlayerTiles;
