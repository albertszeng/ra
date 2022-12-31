import React from 'react';
import {
  Card,
  CardHeader,
  CardMedia,
  Tooltip,
} from '@mui/material';

import { getTileShortName } from '../libs/game';
import type { Tile as TileInfo } from '../libs/game';

type TileProps = {
  tile: TileInfo;
  selected: boolean | undefined,
  onSelect: ((tile: TileInfo) => void) | null;
};

function Tile({ tile, selected, onSelect }: TileProps): JSX.Element {
  const { name } = tile;
  const imageSrc = `${process.env.PUBLIC_URL}/assets/tiles/${name}.jpeg`;
  return (
    <Card
      sx={{
        border: (tile.tileType === 'DISASTER' || selected) ? 3 : 0,
        borderColor: (selected) ? 'yellow' : 'red',
      }}
      onClick={(onSelect) ? (() => onSelect(tile)) : undefined}
    >
      <Tooltip title={name}>
        <CardMedia
          component="img"
          image={imageSrc}
          alt={name}
        />
      </Tooltip>
      <CardHeader subheader={getTileShortName(name)} />
    </Card>
  );
}

function EmptyRaTile(): JSX.Element {
  return (
    <Card>
      <CardMedia
        component="img"
        image={`${process.env.PUBLIC_URL}/assets/tiles/emptyRa.png`}
        alt="empty ra"
      />
    </Card>
  );
}

function FilledRaTile(): JSX.Element {
  return (
    <Card>
      <CardMedia
        component="img"
        image={`${process.env.PUBLIC_URL}/assets/tiles/ra.png`}
        alt="ra"
      />
    </Card>
  );
}

function SlotTile(): JSX.Element {
  return (
    <Card>
      <CardMedia
        component="img"
        image={`${process.env.PUBLIC_URL}/assets/tiles/slot.png`}
        alt="empty slot"
      />
    </Card>
  );
}

type RaTileProps = {
  filled: boolean;
};
function RaTile({ filled }: RaTileProps) : JSX.Element {
  return (filled) ? <FilledRaTile /> : <EmptyRaTile />;
}

export {
  RaTile,
  SlotTile,
  Tile,
};
