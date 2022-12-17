import React from 'react';

import { Button, ButtonGroup } from '@mui/material';
import { Groups, ResetTv, ShoppingBag } from '@mui/icons-material';

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
      <Button
        variant="contained"
        size="large"
        onClick={resetGame}
        endIcon={<ResetTv />}
      >
        Leave
      </Button>
    </>
  );
}

export type { ActionsProps };
export { Actions };
