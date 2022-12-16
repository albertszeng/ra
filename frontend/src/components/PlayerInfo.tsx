import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import { Badge } from '@mui/material';
import { Leaderboard } from '@mui/icons-material';

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
    playerName, points, collection, usableSun, unusableSun,
  }, isActive, isCurrent, auctionStarted, bidWithSun,
}: PlayerInfoProps): JSX.Element {
  return (
    <Grid container spacing={{ xs: 1, md: 2 }}>
      <Grid xs={3}>
        <p>
          {`Name: ${playerName}`}
        </p>
      </Grid>
      <Grid xs={9}>
        <PlayerTiles tiles={collection} />
      </Grid>
      <Grid xs={8}>
        <PlayerActions
          isActive={isActive}
          isCurrent={isCurrent}
          auctionStarted={auctionStarted}
          availableSun={usableSun}
          unavailableSun={unusableSun}
          bidWithSun={bidWithSun}
        />
        <Badge badgeContent={points} color="secondary">
          <Leaderboard fontSize="large" color="action" />
        </Badge>
      </Grid>
    </Grid>
  );
}

export default PlayerInfo;
