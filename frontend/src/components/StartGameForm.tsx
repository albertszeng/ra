import React, { useCallback, useState } from 'react';

import {
  Button,
  ButtonGroup,
  FormControl,
  FormControlLabel,
  FormLabel,
  Paper,
  Radio,
  RadioGroup,
  Slider,
  Typography,
} from '@mui/material';
import {
  AddModerator,
  Public,
} from '@mui/icons-material';
import Grid from '@mui/material/Unstable_Grid2';

import { socket } from '../common';
import { AILevels } from '../libs/request';
import type {
  StartRequest,
  Visibility,
} from '../libs/request';

function StartGameForm(): JSX.Element {
  // Total number of players (including AI players)
  const [numPlayers, setNumPlayers] = useState<number>(2);
  // Number of AI players. numPlayers - numAIPlayers is the number of human players.
  const [numAIPlayers, setNumAIPlayers] = useState<number>(1);
  // The difficulty. Rough mapping is 0 => Easy, 1 => Medium, 2 => Hard.
  const [aiLevelIdx, setAILevelIdx] = useState<number>(2);

  const handleNewGame = useCallback((visibility: Visibility) => {
    const request: StartRequest = {
      numPlayers: numPlayers - numAIPlayers,
      visibility,
      numAIPlayers,
      AILevel: AILevels[aiLevelIdx],
    };
    socket.emit('start_game', request);
  }, [numPlayers, numAIPlayers, aiLevelIdx]);

  return (
    <Paper elevation={1}>
      <Grid container spacing={2} columns={{ xs: 4, sm: 8, md: 12 }}>
        <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
          <Typography variant="h4">
            Start New Game
          </Typography>
        </Grid>
        <Grid xs={4} display="flex" justifyContent="center" alignItems="center">
          <FormControl>
            <FormLabel id="player-label">Total Players</FormLabel>
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
                  key={`nPlayers-${nPlayers}`}
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
              color="secondary"
              aria-labelledby="ai-label"
              name="ais-group"
              value={numAIPlayers}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                setNumAIPlayers(Number(event.target.value));
              }}
            >
              {[0, 1, 2, 3, 4].filter((n) => n < numPlayers).map((nAIs: number) => (
                <FormControlLabel
                  key={`nAIs-${nAIs}`}
                  value={nAIs}
                  control={<Radio />}
                  label={nAIs}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </Grid>
        <Grid xs={4} sm={8} md={4} display="flex" justifyContent="center" alignItems="center">
          <FormControl>
            <FormControlLabel
              value="top"
              control={(
                <Slider
                  aria-label="AI Difficulty"
                  color="secondary"
                  size="medium"
                  step={1}
                  min={0}
                  max={2}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(idx: number) => AILevels[idx]}
                  disabled={numAIPlayers <= 0}
                  marks
                  getAriaValueText={(_val: number, idx: number) => AILevels[idx]}
                  getAriaLabel={(idx: number) => AILevels[idx]}
                  value={aiLevelIdx}
                  onChangeCommitted={(e, val: number | number[]) => {
                    if (!Array.isArray(val)) {
                      setAILevelIdx(val);
                    }
                  }}
                />
              )}
              label="AI Difficulty"
              labelPlacement="bottom"
            />
          </FormControl>
        </Grid>
        <Grid xs={4} sm={8} md={12} display="flex" justifyContent="center" alignItems="center">
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
