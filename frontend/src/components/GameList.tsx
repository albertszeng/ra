import React, {
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  // Autocomplete,
  Button,
  ButtonGroup,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Paper,
  Slider,
  // TextField,
  // Tooltip,
  Typography,
} from '@mui/material';
import { VideogameAsset } from '@mui/icons-material';
import Grid from '@mui/material/Unstable_Grid2';

// import { enqueueSnackbar } from 'notistack';

import { socket } from '../common';
import { notEmpty } from '../libs/game';
import type {
  // MessageResponse,
  ListGame,
  ListGamesResponse,
  StartRequest,
  Visibility,
} from '../libs/request';

type GameListProps = {
  handleLoadGame: (gameId: string) => void;
  handleDeleteGame: (gameId: string) => void;
};

// function isPlayerNames(input: string): boolean {
//   if (input.includes(',')) {
//     // Must be player names. Validate at least 2.
//     const segments = input.split(',');
//     return segments && segments.length >= 2;
//   }
//   return false;
// }

// function isGameId(input: string): boolean {
//   // Assume it must be a game id.
//   let hex = input;
//   if (input.includes('-')) {
//     hex = input.replace(/-|\s/g, '');
//   }
//   return hex.length === 32;
// }

// function isValid(input: string): boolean {
//   return input !== '' && (isPlayerNames(input) || isGameId(input));
// }

/* Merges two game lists. Identical ids in prev are overriden by update. */
function merge(prev: ListGame[], update: ListGame[]): ListGame[] {
  const local = [...prev];
  const idToIdx = prev.reduce(
    (acc, game, idx) => ({ ...acc, [game.id]: idx }),
    {} as { [key: string] : number },
  );
  const newGames = update.map((game: ListGame) => {
    if (game.id in idToIdx) {
      local[idToIdx[game.id]] = game;
      return null;
    }
    return game;
  }).filter(notEmpty);
  return local.concat(newGames);
}

function GameList(_unused: GameListProps): JSX.Element {
  // const [formValid, setFormValid] = useState(false);
  const [privateGames, setPrivateGames] = useState<ListGame[]>([]);
  const [publicGames, setPublicGames] = useState<ListGame[]>([]);
  const [numPlayers, setNumPlayers] = useState<number>(2);

  const handleNewGame = useCallback((visibility: Visibility) => {
    const request: StartRequest = { numPlayers, visibility };
    socket.emit('start_game', request);
  }, [numPlayers]);

  const onListGames = useCallback(({ games, partial } : ListGamesResponse) => {
    const privateG = games.filter((game) => game.visibility === 'PRIVATE');
    setPrivateGames((prev) => ((partial) ? merge(prev, privateG) : privateG));

    const publicG = games.filter((game) => game.visibility === 'PUBLIC');
    setPublicGames((prev) => ((partial) ? merge(prev, publicG) : publicG));
  }, []);
  // const onDelete = useCallback(({ message, level }: MessageResponse) => {
  //   enqueueSnackbar(message, { variant: level });
  //   if (level === 'success') {
  //     setGameOrPlayers('');
  //     socket.emit('list_games');
  //   }
  // }, []);
  useEffect(() => {
    socket.on('list_games', onListGames);
    socket.emit('list_games');
    return () => {
      socket.off('list_games', onListGames);
    };
  }, [onListGames]);
  // useEffect(() => {
  //   socket.on('delete', onDelete);
  //   return () => {
  //     socket.off('delete', onDelete);
  //   };
  // }, [onDelete]);

  const renderGame = useCallback(({ id, players }: ListGame) => (
    <ListItem alignItems="flex-start">
      <ListItemIcon>
        <VideogameAsset />
      </ListItemIcon>
      <ListItemText
        primary={`Game ID: ${id}`}
        secondary={players.toString()}
      />
    </ListItem>
  ), []);

  // const handleChange = useCallback((
  //   e: SyntheticEvent<Element, Event>,
  //   value: string | null,
  // ): void => {
  //   if (!value) {
  //     return;
  //   }
  //   setFormValid(isValid(value));
  //   setGameOrPlayers(value);
  // }, []);
  // const handleDelete = useCallback(() => {
  //   if (!isGameId(gameOrPlayers)) {
  //     enqueueSnackbar('Invalid game id.', { variant: 'warning' });
  //     return;
  //   }
  //   handleDeleteGame(gameOrPlayers);
  // }, [gameOrPlayers, handleDeleteGame]);
  // const tooltipText = 'Enter comma-seperated list of players or the Game ID
  // of an existing game.';
  return (
    <Paper elevation={1}>
      <Grid container spacing={2} columns={{ xs: 4, sm: 8, md: 12 }}>
        <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
          <Typography variant="h4">
            Start a Game of Ra!
          </Typography>
        </Grid>
        <Grid xs={12} justifyContent="center" alignItems="center">
          <List>
            <ListSubheader>
              {`Public (${publicGames.length})`}
            </ListSubheader>
            {publicGames.map(renderGame)}
            <ListSubheader>
              {`Private (${privateGames.length})`}
            </ListSubheader>
            {privateGames.map(renderGame)}
          </List>
        </Grid>
        <Grid xs={6} justifyContent="center" alignItems="center">
          <Slider
            marks
            aria-label="Number of Players"
            valueLabelDisplay="auto"
            step={1}
            min={2}
            max={5}
            value={numPlayers}
            getAriaValueText={(n: number) => `${n} Players`}
            onChangeCommitted={(e, value: number | number[]) => {
              if (!Array.isArray(value)) {
                setNumPlayers(value);
              }
            }}
          />
        </Grid>
        <Grid xs={6} justifyContent="center" alignItems="center">
          <ButtonGroup
            variant="contained"
            size="large"
            aria-label="game action buttons"
          >
            <Button
              color="primary"
              onClick={() => handleNewGame('PUBLIC')}
            >
              Start Public Game
            </Button>
            <Button
              color="secondary"
              onClick={() => handleNewGame('PRIVATE')}
            >
              Start Private Game
            </Button>
          </ButtonGroup>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default GameList;
