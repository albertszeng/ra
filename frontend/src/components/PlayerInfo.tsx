import React from 'react';

import { Badge } from '@mui/material';
import { Leaderboard } from '@mui/icons-material';

import PlayerActions from './PlayerActions';
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
}: PlayerInfoProps) {
  return (
    <>
      <p>
        {`Name: ${playerName}`}
      </p>
      <p>{`Tiles: ${collection.toString()}`}</p>
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
    </>
  );
}

export default PlayerInfo;
