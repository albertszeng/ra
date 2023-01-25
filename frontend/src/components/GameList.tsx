import React, {
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  ButtonGroup,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Paper,
  Typography,
} from '@mui/material';
import {
  ContentCopy,
  Delete,
  PersonAdd,
  VideogameAsset,
} from '@mui/icons-material';
import Grid from '@mui/material/Unstable_Grid2';

import { enqueueSnackbar } from 'notistack';

import JoinPrivateDialog from './JoinPrivateDialog';
import { socket } from '../common';
import { notEmpty } from '../libs/game';
import type {
  AddPlayerRequest,
  DeleteRequest,
  MessageResponse,
  ListGame,
  ListGamesResponse,
  ValidatedListGame,
} from '../libs/request';

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
    if (game.deleted || !game.players || !game.visibility || !game.numPlayers || !game.status) {
      return null;
    }
    return game as ValidatedListGame;
  }).filter(notEmpty);
}
/* Sorts games so those including the user are first.
    sorted = [gamesWithUser, gamesWithoutUser]
  Each partition above is then sorted internally players left to start.
*/
function smartSort(user: string, games: ValidatedListGame[]): ValidatedListGame[] {
  const withUser = games.filter(({ players }) => players.includes(user));
  const withoutUser = games.filter(({ players }) => !players.includes(user));
  const compareFn = (a: ValidatedListGame, b: ValidatedListGame) => {
    const aLeft = a.numPlayers - a.players.length;
    const bLeft = b.numPlayers - b.players.length;
    return aLeft - bLeft;
  };
  withUser.sort(compareFn);
  withoutUser.sort(compareFn);
  return withUser.concat(withoutUser);
}

type GameListProps = {
  user: string;
  handleLoadGame: (gameId: string) => void;
};
function GameList({ user, handleLoadGame }: GameListProps): JSX.Element {
  // const [formValid, setFormValid] = useState(false);
  const [privateGames, setPrivateGames] = useState<ValidatedListGame[]>([]);
  const [publicGames, setPublicGames] = useState<ValidatedListGame[]>([]);
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
    setPrivateGames((prev) => (
      smartSort(user, (partial) ? merge(prev, privateG, deleted) : privateG)));

    const publicG = clean(games.filter((game) => game.visibility === 'PUBLIC'));
    setPublicGames((prev) => (
      smartSort(user, (partial) ? merge(prev, publicG, deleted) : publicG)));
  }, [user]);
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

  const renderGame = useCallback(({
    id, status, players, numPlayers: count,
  }: ValidatedListGame) => {
    const secondaryAction = (
      <ButtonGroup>
        {(status === 'WAITING') ? (
          <IconButton
            aria-label="join"
            onClick={() => handleAddPlayer(id)}
          >
            <PersonAdd />
          </IconButton>
        ) : null}
        {(status === 'WAITING') ? (
          <IconButton
            aria-label="share"
            onClick={async () => {
              await navigator.clipboard.writeText(id);
              enqueueSnackbar('Copied to clipboard', { variant: 'info' });
            }}
          >
            <ContentCopy />
          </IconButton>
        ) : null}
        {(players.includes(user)) ? (
          <IconButton
            aria-label="delete"
            onClick={() => handleDeleteGame(id)}
          >
            <Delete />
          </IconButton>
        ) : null}
      </ButtonGroup>
    );
    return (
      <ListItem
        key={`game-${id}`}
        alignItems="flex-start"
        secondaryAction={secondaryAction}
      >
        <ListItemButton dense onClick={() => handleLoadGame(id)}>
          <ListItemIcon>
            <VideogameAsset />
          </ListItemIcon>
          <ListItemText
            primary={`[${status}] Game: ${id}`}
            secondary={`(${players.length}/${count}): ${players.toString()}`}
          />
        </ListItemButton>
      </ListItem>
    );
  }, [handleAddPlayer, handleDeleteGame, handleLoadGame, user]);

  return (
    <Paper elevation={1}>
      <Grid container spacing={2} columns={{ xs: 4, sm: 8, md: 12 }}>
        <Grid xs={12} display="flex" justifyContent="center" alignItems="center">
          <Typography variant="h4">
            Available Games
          </Typography>
        </Grid>
        <Grid xs={12} justifyContent="center" alignItems="center">
          <List
            sx={{
              width: '100%',
              overflow: 'auto',
              maxHeight: 680,
            }}
          >
            <ListSubheader>
              {`Public (${publicGames.length})`}
            </ListSubheader>
            {publicGames.map(renderGame)}
            <ListSubheader>
              {`Private (${privateGames.length})`}
            </ListSubheader>
            {privateGames.map(renderGame)}
            <ListItem
              key="join-private"
              alignItems="center"
            >
              <JoinPrivateDialog onJoin={handleLoadGame} />
            </ListItem>
          </List>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default GameList;
