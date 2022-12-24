import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { Brightness4, Brightness7, Menu } from '@mui/icons-material';
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

import { socket, ColorModeContext } from './common';
import './App.css';
import AlertModal from './components/AlertModal';
import Game from './components/Game';
import Header from './components/Header';
import Login from './components/Login';

import type { AlertData, ApiResponse, LoginSuccess } from './libs/game';

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
  const [alertData, setAlertData] = useState<AlertData>(
    { show: false, message: '', level: 'info' },
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
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      socket.emit('login', { token });
    }
    socket.on('logout', ({ message, level }: ApiResponse) => {
      setLoggedIn(false);
      if (message || level) {
        setAlertData({ show: true, message: message || 'Unknown error', level });
      }
    });
    return () => {
      socket.off('logout');
    };
  }, []);
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
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 2 }}
            >
              <Menu />
            </IconButton>
            <Header />
            <IconButton onClick={colorMode.toggleColorMode} color="inherit">
              {theme.palette.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg">
          <Grid container spacing={2}>
            <Grid xs />
            <Grid xs={12}>
              {(loggedIn || !process.env.REACT_APP_ENABLE_LOGIN)
                ? (
                  <Game
                    playerName={playerName}
                    setPlayerName={setPlayerName}
                    setAlert={setAlertData}
                  />
                )
                : <Login setAlert={setAlertData} onLoginSuccess={onLoginSuccess} />}
            </Grid>
          </Grid>
          <AlertModal
            alert={alertData}
            setAlert={setAlertData}
          />
        </Container>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export default App;
