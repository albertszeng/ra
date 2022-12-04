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
    <Card sx={{ minWidth: 275 }}>
      <CardMedia
        component="img"
        height="140"
        image={imageSrc}
        alt={altText}
      />
    </Card>
  );
}

function RaTile() : JSX.Element {
  return <Tile imageSrc={raTileImage} altText="ra" />;
}

export {
  Tile,
  RaTile,
};
