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
  const [numPlayers, setNumPlayers] = useState<number>(2);
  const [numAIPlayers, setNumAIPlayers] = useState<number>(0);
  const [aiLevelIdx, setAILevelIdx] = useState<number>(0);

  const handleNewGame = useCallback((visibility: Visibility) => {
    const request: StartRequest = {
      numPlayers,
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
              {[1, 2, 3, 4, 5].filter(
                (n) => n + numAIPlayers >= 2 && n + numAIPlayers <= 5,
              ).map((nPlayers: number) => (
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
              {[0, 1, 2, 3, 4].filter(
                (n) => n + numPlayers >= 2 && n + numPlayers <= 5,
              ).map((nAIs: number) => (
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
            disabled={numAIPlayers + numPlayers > 5 || numAIPlayers + numPlayers < 2}
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
