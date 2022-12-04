import React from 'react';
import {
  Card,
  CardMedia,
} from '@mui/material';

import raTileImage from '../images/tiles/ra.png';

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
function EmptyTile(): JSX.Element {
  return <Card sx={{ minWidth: 275 }} />;
}
type RaTileProps = {
  filled: boolean;
};
function RaTile({ filled }: RaTileProps) : JSX.Element {
  return (filled) ? <Tile imageSrc={raTileImage} altText="ra" /> : <EmptyTile />;
}

export {
  Tile,
  RaTile,
};
