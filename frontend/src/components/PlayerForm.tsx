import React, {
  SyntheticEvent,
  useEffect,
  useState,
} from 'react';

import {
  Alert,
  Autocomplete,
  Button,
  ButtonGroup,
  Paper,
  Snackbar,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

import { listGames, deleteGame } from '../libs/game';

type PlayerFormProps = {
  handleNewGame: (players: string[]) => void;
  handleLoadGame: (gameId: string) => void;
};

function isValid(input: string): boolean {
  if (input.includes(',')) {
    // Must be player names. Validate at least 2.
    const segments = input.split(',');
    return segments && segments.length >= 2;
  }
  // Must be game id.
  let hex = input;
  if (input.includes('-')) {
    hex = input.replace(/-|\s/g, '');
  }
  return hex.length === 32;
}

function PlayerForm({ handleNewGame, handleLoadGame }: PlayerFormProps): JSX.Element {
  const [input, setInput] = useState<string>('');
  const [formValid, setFormValid] = useState(false);
  const [games, setGames] = useState<string[]>([]);
  const [userMsg, setUserMsg] = useState('');

  useEffect(() => {
    const fetchGames = async () => {
      const { gameIds } = await listGames();
      setGames(gameIds);
    };
    // eslint-disable-next-line @typescript-eslint/naming-convention
    const _ = fetchGames();
  }, []);

  const handleChange = (e: SyntheticEvent<Element, Event>, value: string | null): void => {
    if (!value) {
      return;
    }
    setFormValid(isValid(value));
    setInput(value);
  };
  const handleSubmit = () => {
    if (input.includes(',')) {
      // Players, start a new game.
      return handleNewGame(input.split(','));
    }
    // Game id, start load it.
    return handleLoadGame(input);
  };
  const handleDelete = () => {
    const remoteDelete = async () => {
      const { message } = await deleteGame(input);
      const { gameIds } = await listGames();
      setGames(gameIds);
      if (message) {
        setUserMsg(message);
      }
    };
    // eslint-disable-next-line @typescript-eslint/naming-convention
    const _ = remoteDelete();
  };
  const tooltipText = 'Enter comma-seperated list of players or the Game ID of an existing game.';
  return (
    <>
      <Paper elevation={1}>
        <Grid container spacing={3}>
          <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
            <Typography variant="h4">
              Start a Game of Ra!
            </Typography>
          </Grid>
          <Grid xs={2} />
          <Grid xs={8}>
            {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
            <Tooltip
              followCursor
              title={tooltipText}
              enterDelay={250}
            >
              <Autocomplete
                freeSolo
                id="players"
                options={games}
                value={input}
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
          <Grid xs={2} />
          <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
            <ButtonGroup
              variant="contained"
              size="large"
              aria-label="load action buttons"
            >
              <Button
                color={(input.includes('-')) ? 'secondary' : 'primary'}
                disabled={!formValid}
                onClick={handleSubmit}
              >
                {(input.includes('-')) ? 'Load' : 'Start'}
              </Button>
              <Button
                color="error"
                disabled={!formValid && !input.includes(',')}
                onClick={handleDelete}
              >
                Delete
              </Button>
            </ButtonGroup>
          </Grid>
        </Grid>
      </Paper>
      <Snackbar
        open={!!userMsg}
        autoHideDuration={6000}
        onClose={() => setUserMsg('')}
      >
        <Alert
          onClose={() => setUserMsg('')}
          severity="warning"
          sx={{ width: '100%' }}
        >
          {userMsg}
        </Alert>
      </Snackbar>
    </>
  );
}

export default PlayerForm;
