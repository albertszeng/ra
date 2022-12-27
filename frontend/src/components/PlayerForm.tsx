import React, {
  SyntheticEvent,
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  Autocomplete,
  Button,
  ButtonGroup,
  Paper,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

import { socket } from '../common';
import type { AlertData } from '../libs/game';
import type {
  MessageResponse,
  ListGame,
  ListGamesResponse,
} from '../libs/request';

type PlayerFormProps = {
  handleNewGame: (players: string[]) => void;
  handleLoadGame: (gameId: string) => void;
  handleDeleteGame: (gameId: string) => void;
  setAlert: (alert: AlertData) => void;
};

function isPlayerNames(input: string): boolean {
  if (input.includes(',')) {
    // Must be player names. Validate at least 2.
    const segments = input.split(',');
    return segments && segments.length >= 2;
  }
  return false;
}

function isGameId(input: string): boolean {
  // Assume it must be a game id.
  let hex = input;
  if (input.includes('-')) {
    hex = input.replace(/-|\s/g, '');
  }
  return hex.length === 32;
}

function isValid(input: string): boolean {
  return input !== '' && (isPlayerNames(input) || isGameId(input));
}

function PlayerForm({
  handleNewGame, handleLoadGame, handleDeleteGame, setAlert,
}: PlayerFormProps): JSX.Element {
  const [gameOrPlayers, setGameOrPlayers] = useState<string>('');
  const [formValid, setFormValid] = useState(false);
  const [gameList, setGameList] = useState<ListGame[]>([]);

  useEffect(() => {
    socket.on('list_games', ({ games } : ListGamesResponse) => {
      setGameList(games);
    });
    socket.emit('list_games');
    return () => {
      socket.off('list_games');
    };
  }, []);
  useEffect(() => {
    socket.on('delete', ({ message, level }: MessageResponse) => {
      setAlert({ show: true, message, level });
      if (level === 'success') {
        setGameOrPlayers('');
      }
    });
    return () => {
      socket.off('delete');
    };
  }, [setAlert]);

  const handleChange = useCallback((
    e: SyntheticEvent<Element, Event>,
    value: string | null,
  ): void => {
    if (!value) {
      return;
    }
    setFormValid(isValid(value));
    setGameOrPlayers(value);
  }, []);
  const handleSubmit = useCallback(() => {
    if (gameOrPlayers.includes(',')) {
      // Players, start a new game.
      handleNewGame(gameOrPlayers.split(','));
      return;
    }
    // Game id, start load it.
    handleLoadGame(gameOrPlayers);
  }, [gameOrPlayers, handleLoadGame, handleNewGame]);
  const handleDelete = useCallback(() => {
    if (!isGameId(gameOrPlayers)) {
      setAlert({ show: true, message: 'Invalid game id.', level: 'warning' });
      return;
    }
    handleDeleteGame(gameOrPlayers);
  }, [gameOrPlayers, setAlert, handleDeleteGame]);
  const tooltipText = 'Enter comma-seperated list of players or the Game ID of an existing game.';
  return (
    <Paper elevation={1}>
      <Grid container spacing={2} columns={{ xs: 4, sm: 8, md: 12 }}>
        <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
          <Typography variant="h4">
            Start a Game of Ra!
          </Typography>
        </Grid>
        <Grid xs={12} justifyContent="center" alignItems="center">
          {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
          <Tooltip
            followCursor
            title={tooltipText}
            enterDelay={250}
          >
            <Autocomplete
              freeSolo
              id="games_or_players"
              options={gameList}
              renderOption={(props, { id, players }: ListGame) => (
                // eslint-disable-next-line react/jsx-props-no-spreading
                <li {...props}>
                  {`${id.substring(0, 4)}: ${players.toString()}`}
                </li>
              )}
              getOptionLabel={(option: ListGame | string) => {
                if (typeof option === 'string') {
                  return option;
                }
                return option.id;
              }}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              value={gameOrPlayers}
              onInputChange={handleChange}
              renderInput={(params) => (
                <TextField
                  /* eslint-disable-next-line react/jsx-props-no-spreading */
                  {...params}
                  label="Player Names/Game ID"
                />
              )}
            />
          </Tooltip>
        </Grid>
        <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
          <ButtonGroup
            variant="contained"
            size="large"
            aria-label="load action buttons"
          >
            <Button
              color={(gameOrPlayers.includes('-')) ? 'secondary' : 'primary'}
              disabled={!formValid}
              onClick={handleSubmit}
            >
              {(gameOrPlayers.includes('-')) ? 'Load' : 'Start'}
            </Button>
            <Button
              color="error"
              disabled={!formValid && !gameOrPlayers.includes(',')}
              onClick={handleDelete}
            >
              Delete
            </Button>
          </ButtonGroup>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default PlayerForm;
