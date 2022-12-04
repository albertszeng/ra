import React from 'react';
import {
  Card,
  CardMedia,
} from '@mui/material';

import raTileImage from '../images/tiles/ra.png';
import emptyRaTileImage from '../images/tiles/emptyRa.png';
import slotTileImage from '../images/tiles/slot.png';

type TileProps = {
  altText: string;
  imageSrc: string;
};

function Tile({ altText, imageSrc }: TileProps): JSX.Element {
  return (
    <Card>
      <CardMedia
        component="img"
        image={imageSrc}
        alt={altText}
      />
    </Card>
  );
}
function EmptyRaTile(): JSX.Element {
  return <Tile altText="empty ra" imageSrc={emptyRaTileImage} />;
}
function SlotTile(): JSX.Element {
  return <Tile altText="empty slot" imageSrc={slotTileImage} />;
}

type RaTileProps = {
  filled: boolean;
};
function RaTile({ filled }: RaTileProps) : JSX.Element {
  return (filled) ? <Tile imageSrc={raTileImage} altText="ra" /> : <EmptyRaTile />;
}

export {
  RaTile,
  SlotTile,
};
