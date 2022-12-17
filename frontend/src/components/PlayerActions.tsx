import React from 'react';

import { Button, ButtonGroup, useMediaQuery } from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';
import { NextPlan, StrikethroughS, WbSunny } from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

type PlayerActionsProps = {
  availableSun: number[],
  unavailableSun: number[],
  isActive: boolean;
  isCurrent: boolean;
  auctionStarted: boolean;
  minBidSun: number;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
};

function PlayerActions({
  availableSun, unavailableSun, isActive, isCurrent, auctionStarted, bidWithSun, minBidSun,
}: PlayerActionsProps) {
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('sm'));
  const size = (matchDownSm) ? undefined : 'large';
  return (
    <>
      <Grid xs={6} display="flex" justifyContent="left" alignItems="left">
        <ButtonGroup
          disabled={!isActive || !isCurrent || !auctionStarted}
          size={size}
          color="success"
          aria-label="available sun button group"
        >
          {availableSun.map((sun: number, idx: number) => (
            <Button
              disabled={sun <= minBidSun}
              endIcon={<WbSunny />}
              variant="contained"
              key={sun}
              onClick={() => bidWithSun(idx)}
            >
              {sun}
            </Button>
          ))}
        </ButtonGroup>
      </Grid>
      <Grid xs={6} display="flex" justifyContent="right" alignItems="right">
        <ButtonGroup
          disabled={!isActive || !isCurrent || !auctionStarted}
          size={size}
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
          <Button
            endIcon={<NextPlan />}
            variant="contained"
            color="secondary"
            onClick={() => bidWithSun(-1)}
          >
            Pass
          </Button>
        </ButtonGroup>
      </Grid>
    </>
  );
}

export default PlayerActions;
