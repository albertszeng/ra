import React, {
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  // Autocomplete,
  Button,
  ButtonGroup,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Paper,
  Slider,
  Typography,
} from '@mui/material';
import { Delete, PersonAdd, VideogameAsset } from '@mui/icons-material';
import Grid from '@mui/material/Unstable_Grid2';

import { enqueueSnackbar } from 'notistack';

import { socket } from '../common';
import { notEmpty } from '../libs/game';
import type {
  AddPlayerRequest,
  DeleteRequest,
  MessageResponse,
  ListGame,
  ListGamesResponse,
  StartRequest,
  ValidatedListGame,
  Visibility,
} from '../libs/request';

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
function merge(
  prev: ValidatedListGame[],
  updates: ValidatedListGame[],
  deleted: ListGame[],
): ValidatedListGame[] {
  const local: (ValidatedListGame | null)[] = [...prev];
  const idToIdx = prev.reduce(
    (acc, game, idx) => ({ ...acc, [game.id]: idx }),
    {} as { [key: string] : number },
  );
  const newGames = updates.map((game: ValidatedListGame) => {
    if (game.id in idToIdx) {
      local[idToIdx[game.id]] = game;
      return null;
    }
    return game;
  }).filter(notEmpty);
  deleted.forEach(({ id }: ListGame) => {
    if (id in idToIdx) {
      local[idToIdx[id]] = null;
    }
  });
  return local.filter(notEmpty).concat(newGames);
}
function clean(games: ListGame[]): ValidatedListGame[] {
  return games.map((game: ListGame) => {
    if (game.deleted || !game.players || !game.visibility || !game.numPlayers) {
      return null;
    }
    return game as ValidatedListGame;
  }).filter(notEmpty);
}

type GameListProps = {
  handleLoadGame: (gameId: string) => void;
};
function GameList({ handleLoadGame }: GameListProps): JSX.Element {
  // const [formValid, setFormValid] = useState(false);
  const [privateGames, setPrivateGames] = useState<ValidatedListGame[]>([]);
  const [publicGames, setPublicGames] = useState<ValidatedListGame[]>([]);
  const [numPlayers, setNumPlayers] = useState<number>(2);

  const handleNewGame = useCallback((visibility: Visibility) => {
    const request: StartRequest = { numPlayers, visibility };
    socket.emit('start_game', request);
  }, [numPlayers]);

  const handleDeleteGame = useCallback((toDeleteId: string) => {
    const request: DeleteRequest = { gameId: toDeleteId };
    socket.emit('delete', request);
  }, []);
  const handleAddPlayer = useCallback((gameId: string) => {
    const request: AddPlayerRequest = { gameId };
    socket.emit('add_player', request);
  }, []);

  const onListGames = useCallback(({ games, partial } : ListGamesResponse) => {
    const deleted = games.filter((game) => game.deleted);
    const privateG = clean(games.filter((game) => game.visibility === 'PRIVATE'));
    setPrivateGames((prev) => ((partial) ? merge(prev, privateG, deleted) : privateG));

    const publicG = clean(games.filter((game) => game.visibility === 'PUBLIC'));
    setPublicGames((prev) => ((partial) ? merge(prev, publicG, deleted) : publicG));
  }, []);
  const onDelete = useCallback(({ message, level }: MessageResponse) => {
    enqueueSnackbar(message, { variant: level });
  }, []);
  useEffect(() => {
    socket.on('list_games', onListGames);
    socket.emit('list_games');
    return () => {
      socket.off('list_games', onListGames);
    };
  }, [onListGames]);
  useEffect(() => {
    socket.on('delete', onDelete);
    return () => {
      socket.off('delete', onDelete);
    };
  }, [onDelete]);

  const renderGame = useCallback(({ id, players, numPlayers: count }: ValidatedListGame) => (
    <ListItem
      key={`game-${id}`}
      alignItems="flex-start"
      secondaryAction={(
        <ButtonGroup>
          <IconButton
            aria-label="join"
            onClick={() => handleAddPlayer(id)}
          >
            <PersonAdd />
          </IconButton>
          <IconButton
            aria-label="delete"
            onClick={() => handleDeleteGame(id)}
          >
            <Delete />
          </IconButton>
        </ButtonGroup>
      )}
    >
      <ListItemButton
        dense
        onClick={() => handleLoadGame(id)}
      >
        <ListItemIcon>
          <VideogameAsset />
        </ListItemIcon>
        <ListItemText
          primary={`Game ID: ${id}`}
          secondary={`(${players.length}/${count}): ${players.toString()}`}
        />
      </ListItemButton>
    </ListItem>
  ), [handleAddPlayer, handleDeleteGame, handleLoadGame]);

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
