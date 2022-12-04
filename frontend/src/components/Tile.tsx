import React from 'react';
import {
  Card,
  CardMedia,
} from '@mui/material';

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
  return <Tile altText="empty ra" imageSrc="/assets/tiles/emptyRa.png" />;
}
function SlotTile(): JSX.Element {
  return <Tile altText="empty slot" imageSrc="/assets/tiles/slot.png" />;
}

type RaTileProps = {
  filled: boolean;
};
function RaTile({ filled }: RaTileProps) : JSX.Element {
  return (filled) ? <Tile imageSrc="/assets/tiles/ra.png" altText="ra" /> : <EmptyRaTile />;
}

export {
  RaTile,
  SlotTile,
  Tile,
};
