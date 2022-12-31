import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';

import {
  Brightness4,
  Brightness7,
  Delete,
  Logout,
  ResetTv,
} from '@mui/icons-material';
import {
  AppBar,
  CssBaseline,
  Container,
  IconButton,
  Toolbar,
  useMediaQuery,
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Grid from '@mui/material/Unstable_Grid2';
import { closeSnackbar, enqueueSnackbar, SnackbarProvider } from 'notistack';
import type { SnackbarKey } from 'notistack';

import { socket, ColorModeContext } from './common';
import './App.css';
import Game from './components/Game';
import Header from './components/Header';
import Login from './components/Login';

import type { LoginSuccess, MessageResponse } from './libs/request';

const MODE_KEY = 'preferredTheme';
const TOKEN_KEY = 'token';

function App() {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState<'light' | 'dark'>(
    localStorage.getItem(MODE_KEY) || (prefersDarkMode) ? 'dark' : 'light',
  );
  const [loggedIn, setLoggedIn] = useState(false);
  // Only valid when logged in.
  const [playerName, setPlayerName] = useState('');
  // Gets set to a snackbar id when we lose connection.
  const [connAlert, setConnAlert] = useState<SnackbarKey | null>(null);
  // Tracks when a player leaves a game.
  const [inGame, setInGame] = useState(false);
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
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));
  const renderAction = useCallback((snackbarId: SnackbarKey | undefined) => (
    <IconButton
      aria-label="delete"
      onClick={() => closeSnackbar(snackbarId)}
    >
      <Delete />
    </IconButton>
  ), []);
  const onLogout = useCallback(({ message, level }: MessageResponse) => {
    setLoggedIn(false);
    setPlayerName('');
    localStorage.removeItem(TOKEN_KEY);
    enqueueSnackbar(message, { variant: level });
  }, []);
  const onDisconnect = useCallback(() => {
    const id = enqueueSnackbar('Disconnected', { variant: 'error', persist: true });
    setConnAlert(id);
  }, []);
  const onConnect = useCallback(() => {
    if (connAlert) {
      closeSnackbar(connAlert);
      setConnAlert(null);
    }
  }, [connAlert]);
  useEffect(() => {
    socket.on('disconnect', onDisconnect);
    socket.on('connect', onConnect);
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
    };
  }, [onConnect, onDisconnect]);
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      socket.emit('login', { token });
    }
    socket.on('logout', onLogout);
    return () => {
      socket.off('logout', onLogout);
    };
  }, [onLogout]);
  const onLoginSuccess = useCallback(({ username, token }: LoginSuccess) => {
    setLoggedIn(true);
    setPlayerName(username);
    localStorage.setItem(TOKEN_KEY, token);
  }, []);
  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppBar position="static">
          <Toolbar>
            <IconButton
              size="large"
              onClick={() => socket.emit('logout')}
              disabled={!loggedIn}
            >
              <Logout />
            </IconButton>
            <Header />
            <IconButton
              size="large"
              onClick={() => setInGame(false)}
              disabled={!inGame}
            >
              <ResetTv />
            </IconButton>
            <IconButton onClick={colorMode.toggleColorMode} color="inherit">
              {theme.palette.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
          </Toolbar>
        </AppBar>
        <SnackbarProvider
          preventDuplicate
          autoHideDuration={3500}
          maxSnack={(isSmallScreen) ? 1 : 4}
          action={renderAction}
        >
          <Container maxWidth="lg">
            <Grid container spacing={2}>
              <Grid xs />
              <Grid xs={12}>
                {(loggedIn)
                  ? (
                    <Game
                      playerName={playerName}
                      isPlaying={inGame}
                      setIsPlaying={setInGame}
                    />
                  )
                  : <Login onLoginSuccess={onLoginSuccess} />}
              </Grid>
            </Grid>
          </Container>
        </SnackbarProvider>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export default App;
