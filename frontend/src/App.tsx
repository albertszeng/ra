import React, { useMemo, useState } from 'react';

import { CssBaseline, Container, useMediaQuery } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Grid from '@mui/material/Unstable_Grid2';

import ColorModeContext from './common';
import './App.css';
import Game from './components/Game';
import Header from './components/Header';

const MODE_KEY = 'preferredTheme';

function App() {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState<'light' | 'dark'>(
    localStorage.getItem(MODE_KEY) || (prefersDarkMode) ? 'dark' : 'light',
  );
  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => {
          const nextMode = (prevMode === 'light' ? 'dark' : 'light');
          localStorage.setItem(MODE_KEY, nextMode);
          return nextMode;
        });
      },
    }),
    [],
  );
  const theme = useMemo(
    () => createTheme({
      palette: {
        mode,
      },
    }),
    [mode],
  );
  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="md">
          <Grid container spacing={2}>
            <Grid xs={12}>
              <Header />
            </Grid>
            <Grid xs />
            <Grid xs={12}>
              <Game />
            </Grid>
          </Grid>
        </Container>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export default App;
