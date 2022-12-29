import React, {
  ChangeEvent,
  MouseEvent,
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  Button,
  Container,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

import { AccountCircle, Visibility, VisibilityOff } from '@mui/icons-material';

import { socket } from '../common';
import type { AlertData } from '../libs/game';
import type { LoginResponse, LoginSuccess } from '../libs/request';

type LoginProps = {
  // Called on successful login.
  onLoginSuccess: (data: LoginSuccess) => void;
  setAlert: (alert: AlertData) => void;
};

function Login({ onLoginSuccess, setAlert }: LoginProps): JSX.Element {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const handleClickShowPassword = () => setShowPassword((show) => !show);
  const handleMouseDownPassword = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  const handleSubmit = useCallback(() => {
    if (user.length < 3) {
      setAlert({ show: true, message: 'Username too short. Must be at least 3 characters.', level: 'info' });
      return;
    }
    if (password.length < 4) {
      setAlert({ show: true, message: 'Password too short. Must be at least 4 characters.', level: 'info' });
      return;
    }
    socket.emit('login', { username: user, password });
  }, [user, password, setAlert]);
  const onLogin = useCallback(({
    token, username, message, level,
  }: LoginResponse) => {
    if (token && username) {
      onLoginSuccess({ token, username });
    }
    setAlert({ show: true, message: message || 'Unknown', level });
  }, [onLoginSuccess, setAlert]);
  useEffect(() => {
    socket.on('login', onLogin);
    return () => {
      socket.off('login', onLogin);
    };
  }, [onLogin]);
  return (
    <form>
      <Container disableGutters>
        <Grid container columns={{ xs: 4 }}>
          <Grid xs={4} display="flex" justifyContent="center" alignItems="center">
            <Typography variant="h4">
              Login
            </Typography>
          </Grid>
          <Grid xs={4} display="flex" justifyContent="center" alignItems="center">
            <TextField
              id="username"
              label="Username"
              size="medium"
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <AccountCircle />
                  </InputAdornment>
                ),
                autoComplete: 'username',
              }}
              value={user}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setUser(e.target.value)}
            />
          </Grid>
          <Grid xs={4} display="flex" justifyContent="center" alignItems="center">
            <TextField
              id="password"
              label="Password"
              size="medium"
              type={(showPassword) ? 'text' : 'password'}
              margin="normal"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleClickShowPassword}
                      onMouseDown={handleMouseDownPassword}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
                autoComplete: 'new-password',
              }}
              value={password}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            />
          </Grid>
          <Grid xs={4} display="flex" justifyContent="center" alignItems="center">
            <Button
              variant="contained"
              size="large"
              color="primary"
              disabled={user.length === 0 || password.length === 0}
              onClick={handleSubmit}
            >
              Login or Register
            </Button>
          </Grid>
        </Grid>
      </Container>
    </form>
  );
}

export default Login;
