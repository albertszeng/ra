import React from 'react';

import { Button, ButtonGroup, useMediaQuery } from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';
import { NextPlan, StrikethroughS, WbSunny } from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

type PlayerActionsProps = {
  availableSun: number[],
  unavailableSun: number[],
  isLocalPlayer: boolean;
  isActive: boolean;
  isCurrent: boolean;
  auctionStarted: boolean;
  maxBidSun: number;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
};

function PlayerActions({
  availableSun, unavailableSun, isActive, isLocalPlayer, isCurrent,
  auctionStarted, bidWithSun, maxBidSun,
}: PlayerActionsProps) {
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('sm'));
  const widthLt470px = useMediaQuery('(max-width:470px)');
  const size = (matchDownSm) ? 'medium' : 'large';
  return (
    <>
      <Grid
        xs={(widthLt470px) ? 12 : 6}
        display="flex"
        justifyContent={(widthLt470px) ? 'center' : 'left'}
        alignItems={(widthLt470px) ? 'center' : 'left'}
      >
        <ButtonGroup
          disabled={!isActive || !isCurrent || !auctionStarted || !isLocalPlayer}
          size={size}
          color="success"
          aria-label="available sun button group"
        >
          {availableSun.map((sun: number, idx: number) => (
            <Button
              disabled={sun <= maxBidSun}
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
      <Grid
        xs={(widthLt470px) ? 12 : 6}
        display="flex"
        justifyContent={(widthLt470px) ? 'center' : 'right'}
        alignItems={(widthLt470px) ? 'center' : 'right'}
      >
        <ButtonGroup
          disabled={!isActive || !isCurrent || !auctionStarted || !isLocalPlayer}
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
