import React from 'react';

import {
  Badge,
  Button,
  ButtonGroup,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  Groups,
  ShoppingBag,
} from '@mui/icons-material';
import Grid from '@mui/material/Unstable_Grid2';

type ActionsProps = {
  disabled: boolean;
  pointsIfWin: number | null;
  onDraw: () => void;
  onAuction: () => void;
};
function Actions({
  disabled, onDraw, onAuction, pointsIfWin,
}: ActionsProps): JSX.Element {
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('sm'));
  const buttonSize = (matchDownSm) ? 'medium' : 'large';
  const widthLt470px = useMediaQuery('(max-width:470px)');
  return (
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
          endIcon={(
            <Badge
              color="secondary"
              showZero
              badgeContent={pointsIfWin}
            >
              <Groups />
            </Badge>
          )}
        >
          Auction
        </Button>
      </ButtonGroup>
    </Grid>
  );
}

export type { ActionsProps };
export { Actions };
