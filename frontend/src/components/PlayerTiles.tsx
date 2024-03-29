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
import { getTileShortName } from '../libs/game';
import type { Tile as TileInfo } from '../libs/game';

type PlayerTilesProps = {
  tiles: TileInfo[];
  onTileClick: (tile: TileInfo) => void;
  goldenGodSelected: boolean;
  disabledTiles: boolean;
};

function PlayerTiles({
  tiles, onTileClick, goldenGodSelected, disabledTiles,
}: PlayerTilesProps): JSX.Element {
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('sm'));
  const matchDownMd = useMediaQuery(theme.breakpoints.down('md'));
  const height = (matchDownSm) ? undefined : 300;
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
      <ImageListItem key={name}>
        <Tile
          tile={tile}
          selected={name.toUpperCase() === 'GOLDEN GOD' && goldenGodSelected}
          onSelect={(disabledTiles) ? null : onTileClick}
        />
        <ImageListItemBar
          title={getTileShortName(name)}
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
  const cols = (matchDownSm) ? 3 : (matchDownMd) ? 4 : 5;
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
