import React, { useContext } from 'react';

import { Brightness4, Brightness7 } from '@mui/icons-material';
import {
  IconButton,
  Paper,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Unstable_Grid2';

import ColorModeContext from '../common';
import sword from '../images/sword_01.png';
import shield from '../images/wooden_shield.png';

function Header() {
  const theme = useTheme();
  const colorMode = useContext(ColorModeContext);
  const matchDownSm = useMediaQuery(theme.breakpoints.down('md'));
  const iconSize = `${(matchDownSm) ? 45 : 70}px`;
  return (
    <Paper elevation={2}>
      <Grid container spacing={2}>
        <Grid display="flex" justifyContent="right" alignItems="right" xs={2}>
          <img src={sword} alt="sword" width={iconSize} height={iconSize} />
        </Grid>
        <Grid display="flex" justifyContent="center" alignItems="center" xs={7}>
          <Typography variant={(matchDownSm) ? 'h4' : 'h3'}>
            <b>Online Ra Game</b>
          </Typography>
        </Grid>
        <Grid display="flex" justifyContent="left" alignItems="left" xs={1}>
          <img src={shield} alt="sword" width={iconSize} height={iconSize} />
        </Grid>
        <Grid display="flex" justifyContent="right" alignItems="right" xs={1}>
          <IconButton onClick={colorMode.toggleColorMode} color="inherit">
            {theme.palette.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default Header;
