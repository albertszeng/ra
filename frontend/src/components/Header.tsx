import React from 'react';

import {
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Unstable_Grid2';

import sword from '../images/sword_01.png';
import shield from '../images/wooden_shield.png';

function Header() {
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('md'));
  const iconSize = `${(matchDownSm) ? 30 : 50}px`;
  return (
    <Grid container spacing={2} component="div" sx={{ flexGrow: 1 }}>
      <Grid display="flex" justifyContent="right" alignItems="right" xs={2}>
        <img src={sword} alt="sword" width={iconSize} height={iconSize} />
      </Grid>
      <Grid display="flex" justifyContent="center" alignItems="center" xs={8}>
        <Typography variant={(matchDownSm) ? 'h3' : 'h2'}>
          <b>Ra</b>
        </Typography>
      </Grid>
      <Grid display="flex" justifyContent="left" alignItems="left" xs={2}>
        <img src={shield} alt="sword" width={iconSize} height={iconSize} />
      </Grid>
    </Grid>
  );
}

export default Header;
