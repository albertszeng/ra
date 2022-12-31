import React, { useCallback, useState } from 'react';

import {
  // Autocomplete,
  Button,
  ButtonGroup,
  FormControl,
  FormControlLabel,
  FormLabel,
  Paper,
  Radio,
  RadioGroup,
  Typography,
} from '@mui/material';
import {
  AddModerator,
  Public,
} from '@mui/icons-material';
import Grid from '@mui/material/Unstable_Grid2';

// import { enqueueSnackbar } from 'notistack';

import { socket } from '../common';
import type {
  StartRequest,
  Visibility,
} from '../libs/request';

function StartGameForm(): JSX.Element {
  const [numPlayers, setNumPlayers] = useState<number>(2);
  const [numAIs, setNumAIs] = useState<number>(0);

  const handleNewGame = useCallback((visibility: Visibility) => {
    const request: StartRequest = { numPlayers, visibility };
    socket.emit('start_game', request);
  }, [numPlayers]);

  return (
    <Paper variant="outlined" elevation={1}>
      <Grid container spacing={2} columns={{ xs: 4, sm: 8, md: 12 }}>
        <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
          <Typography variant="h4">
            Start New Game
          </Typography>
        </Grid>
        <Grid xs={4} display="flex" justifyContent="center" alignItems="center">
          <FormControl>
            <FormLabel id="player-label">Human Players</FormLabel>
            <RadioGroup
              row
              aria-labelledby="player-label"
              name="players-group"
              value={numPlayers}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                setNumPlayers(Number(event.target.value));
              }}
            >
              {[2, 3, 4, 5].map((nPlayers: number) => (
                <FormControlLabel
                  disabled={nPlayers + numAIs > 5}
                  value={nPlayers}
                  control={<Radio />}
                  label={nPlayers}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </Grid>
        <Grid xs={4} display="flex" justifyContent="center" alignItems="center">
          <FormControl>
            <FormLabel id="ai-label">AI Players</FormLabel>
            <RadioGroup
              row
              aria-labelledby="ai-label"
              name="ais-group"
              value={numAIs}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                setNumAIs(Number(event.target.value));
              }}
            >
              {[0, 1, 2, 3].map((nAIs: number) => (
                <FormControlLabel
                  disabled={nAIs + numPlayers > 5}
                  value={nAIs}
                  control={<Radio />}
                  label={nAIs}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </Grid>
        <Grid xs={4} sm={8} md={4} display="flex" justifyContent="center" alignItems="center">
          <ButtonGroup
            variant="contained"
            size="large"
            aria-label="game action buttons"
          >
            <Button
              color="primary"
              onClick={() => handleNewGame('PUBLIC')}
              startIcon={<Public />}
            >
              Public
            </Button>
            <Button
              color="secondary"
              onClick={() => handleNewGame('PRIVATE')}
              startIcon={<AddModerator />}
            >
              Private
            </Button>
          </ButtonGroup>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default StartGameForm;
