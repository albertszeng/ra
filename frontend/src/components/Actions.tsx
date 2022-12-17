import React from 'react';

import { Button, ButtonGroup } from '@mui/material';
import { Groups, ResetTv, ShoppingBag } from '@mui/icons-material';
import Grid from '@mui/material/Unstable_Grid2';

type ActionsProps = {
  disabled: boolean;
  onDraw: () => void;
  onAuction: () => void;
  resetGame: () => void;
};
function Actions({
  disabled, onDraw, onAuction, resetGame,
}: ActionsProps): JSX.Element {
  return (
    <>
      <Grid xs={8} display="flex" justifyContent="left" alignItems="left">
        <ButtonGroup
          disabled={disabled}
          size="large"
          variant="contained"
          aria-label="large action button group"
        >
          <Button
            onClick={onDraw}
            startIcon={<ShoppingBag />}
          >
            Draw
          </Button>
          <Button
            onClick={onAuction}
            endIcon={<Groups />}
          >
            Auction
          </Button>
        </ButtonGroup>
      </Grid>
      <Grid xs={4} display="flex" justifyContent="right" alignItems="right">
        <Button
          variant="contained"
          size="large"
          onClick={resetGame}
          color="secondary"
          endIcon={<ResetTv />}
        >
          Leave
        </Button>
      </Grid>
    </>
  );
}

export type { ActionsProps };
export { Actions };
