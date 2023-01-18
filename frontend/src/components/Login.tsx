import React, {
  ChangeEvent,
  MouseEvent,
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  Button,
  ButtonGroup,
  Container,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';
import { AccountCircle, Visibility, VisibilityOff } from '@mui/icons-material';
import { enqueueSnackbar } from 'notistack';

import { socket } from '../common';
import type { LoginOrRegisterRequest, LoginResponse, LoginSuccess } from '../libs/request';

type AuthEndpoint = 'login' | 'register';
function isValidForm(username: string, password: string): boolean {
  return username.length >= 3 && password.length >= 4;
}

type LoginProps = {
  // Called on successful login.
  onLoginSuccess: (data: LoginSuccess) => void;
};

function Login({ onLoginSuccess }: LoginProps): JSX.Element {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const handleClickShowPassword = () => setShowPassword((show) => !show);
  const handleMouseDownPassword = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  const handleSubmit = useCallback((endpoint: AuthEndpoint) => {
    if (user.length < 3) {
      enqueueSnackbar('Username too short. Must be at least 3 characters.', { variant: 'info' });
      return;
    }
    if (password.length < 4) {
      enqueueSnackbar('Password too short. Must be at least 4 characters.', { variant: 'info' });
      return;
    }
    const request = { username: user, password } as LoginOrRegisterRequest;
    socket.emit(endpoint, request);
  }, [user, password]);
  const onLogin = useCallback(({
    token, username, message, level,
  }: LoginResponse) => {
    if (token && username) {
      onLoginSuccess({ token, username });
    }
    enqueueSnackbar(message || 'Unknown', { variant: level });
  }, [onLoginSuccess]);
  useEffect(() => {
    socket.on('login', onLogin);
    return () => {
      socket.off('login', onLogin);
    };
  }, [onLogin]);
  const upHandler = useCallback((e: KeyboardEvent) => {
    if (isValidForm(user, password) && e.keyCode === 13) {
      handleSubmit('login');
    }
  }, [handleSubmit, password, user]);
  // Add 'Enter' key event press.
  useEffect(() => {
    window.addEventListener('keyup', upHandler);
    return () => {
      window.removeEventListener('keyup', upHandler);
    };
  }, [upHandler]);
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
            <ButtonGroup
              variant="contained"
              size="large"
              disabled={!isValidForm(user, password)}
            >
              <Button
                color="primary"
                onClick={() => handleSubmit('login')}
              >
                Login
              </Button>
              <Button
                color="secondary"
                onClick={() => handleSubmit('register')}
              >
                Register
              </Button>
            </ButtonGroup>
          </Grid>
        </Grid>
      </Container>
    </form>
  );
}

export default Login;
