import React from 'react';

import { Button, ButtonGroup, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';
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
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('sm'));
  const buttonSize = (matchDownSm) ? 'medium' : 'large';
  const widthLt470px = useMediaQuery('(max-width:470px)');
  return (
    <>
      <Grid
        xs={(widthLt470px) ? 12 : 8}
        display="flex"
        justifyContent={(widthLt470px) ? 'center' : 'left'}
        alignItems={(widthLt470px) ? 'center' : 'left'}
      >
        <ButtonGroup
          disabled={disabled}
          size={buttonSize}
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
      <Grid
        xs={(widthLt470px) ? 12 : 4}
        display="flex"
        justifyContent={(widthLt470px) ? 'center' : 'right'}
        alignItems={(widthLt470px) ? 'center' : 'right'}
      >
        <Button
          variant="contained"
          size={buttonSize}
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
