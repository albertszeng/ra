import React from 'react';

import { Button, ButtonGroup } from '@mui/material';
import { NextPlan, StrikethroughS, WbSunny } from '@mui/icons-material';

type PlayerActionsProps = {
  availableSun: number[],
  unavailableSun: number[],
  isActive: boolean;
  isCurrent: boolean;
  auctionStarted: boolean;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
};

function PlayerActions({
  availableSun, unavailableSun, isActive, isCurrent, auctionStarted, bidWithSun,
}: PlayerActionsProps) {
  return (
    <>
      <ButtonGroup
        disabled={!isActive || !isCurrent || !auctionStarted}
        size="large"
        color="success"
        aria-label="available sun button group"
      >
        {availableSun.map((sun: number, idx: number) => (
          <Button
            endIcon={<WbSunny />}
            variant="contained"
            key={sun}
            onClick={() => bidWithSun(idx)}
          >
            {sun}
          </Button>
        ))}
        <Button
          endIcon={<NextPlan />}
          variant="contained"
          color="secondary"
          onClick={() => bidWithSun(-1)}
        >
          Pass
        </Button>
      </ButtonGroup>
      <ButtonGroup
        disabled={!isActive || !isCurrent || !auctionStarted}
        size="large"
        color="success"
        aria-label="unavailable sun button group"
      >
        {unavailableSun.map((sun: number) => (
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
    </>
  );
}

export default PlayerActions;
