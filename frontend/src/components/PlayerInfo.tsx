import React from 'react';

import { Badge, Button, ButtonGroup } from '@mui/material';
import { Leaderboard, StrikethroughS, WbSunny } from '@mui/icons-material';

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
      <ButtonGroup
        disabled={!isActive || !isCurrent || !auctionStarted}
        size="large"
        color="success"
        aria-label="large button group"
      >
        {usableSun.map((sun, idx) => (
          <Button
            endIcon={<WbSunny />}
            variant="contained"
            key={sun}
            onClick={() => bidWithSun(idx)}
          >
            {sun}
          </Button>
        ))}
        {unusableSun.map((sun, idx) => (
          <Button
            disabled
            endIcon={<StrikethroughS />}
            variant="contained"
            key={sun}
          >
            {sun}
          </Button>
        ))}
      </ButtonGroup>
      <Badge badgeContent={points} color="secondary">
        <Leaderboard fontSize="large" color="action" />
      </Badge>
    </>
  );
}

export default PlayerInfo;
