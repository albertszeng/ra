import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import PlayerActions from './PlayerActions';
import PlayerTiles from './PlayerTiles';
import type { Player } from '../libs/game';

type PlayerInfoProps = {
  data: Player
  isActive: boolean;
  isCurrent: boolean;
  auctionStarted: boolean;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
};

function PlayerInfo({
  data: {
    collection, usableSun, unusableSun,
  }, isActive, isCurrent, auctionStarted, bidWithSun,
}: PlayerInfoProps): JSX.Element {
  return (
    <Grid container spacing={{ xs: 1, md: 2 }}>
      <Grid xs={2}>
        <PlayerActions
          isActive={isActive}
          isCurrent={isCurrent}
          auctionStarted={auctionStarted}
          availableSun={usableSun}
          unavailableSun={unusableSun}
          bidWithSun={bidWithSun}
        />
      </Grid>
      <Grid xs={12}>
        <PlayerTiles tiles={collection} />
      </Grid>
    </Grid>
  );
}

export default PlayerInfo;
