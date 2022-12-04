import React from 'react';

import { Button, ButtonGroup } from '@mui/material';
import { Groups, ShoppingBag } from '@mui/icons-material';

type ActionsProps = {
  disabled: boolean;
  onDraw: () => void;
  onAuction: () => void;
};
export default function Actions({ disabled, onDraw, onAuction }: ActionsProps): JSX.Element {
  return (
    <ButtonGroup
      disabled={disabled}
      size="large"
      variant="contained"
      aria-label="outlined primary button group"
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
  );
}
