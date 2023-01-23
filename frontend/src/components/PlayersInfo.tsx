import React, {
  useCallback,
  useEffect,
  useState,
  SyntheticEvent,
} from 'react';

import { Leaderboard, WbSunny } from '@mui/icons-material';
import { TabContext, TabList, TabPanel } from '@mui/lab';
import {
  Badge,
  Box,
  Card,
  List,
  ListItem,
  ListItemText,
  Tab,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Unstable_Grid2';

import { Actions, ActionsProps } from './Actions';
import PlayerInfo from './PlayerInfo';
import { notEmpty } from '../libs/game';
import type { Player, PointMapping, Tile } from '../libs/game';

type PlayersInfoProps = {
  // Name of the local player, if any. Null is when spectating.
  localName: string | null;
  players: Player[];
  playerPointsIfWin: PointMapping;
  playerEstimatedDelta: PointMapping;
  active: boolean[];
  current: number;
  centerSun: number;
  // For each player i, how much sun they have bid (if any).
  auctionSuns: (number | null)[];
  auctionStarted: boolean;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
  // True if the golden god the current player holds is selected.
  goldenGodSelected: boolean;
  // Called when a player selects a tile in their bag.
  selectTile: (player: Player, tile: Tile) => void;
  actionsProps: ActionsProps;
  // Log of all actions during the game. Passed here only for easy display.
  gameLog: string[];
};

function PlayersInfo({
  localName, players, active, current, auctionStarted, bidWithSun, selectTile,
  centerSun, auctionSuns, playerPointsIfWin, playerEstimatedDelta, goldenGodSelected, gameLog,
  actionsProps: {
    disabled: actionsDisabled, onDraw, onAuction,
  },
}: PlayersInfoProps) {
  const [value, setValue] = useState(current.toString());
  const handleChange = useCallback((event: SyntheticEvent, newValue: string) => {
    setValue(newValue);
  }, []);
  // Update value when current changes.
  useEffect(() => setValue(current.toString()), [current]);
  const theme = useTheme();
  const matchDownSm = useMediaQuery(theme.breakpoints.down('sm'));
  // Maximum of actually bid values. Otherwise, maximum is 0;
  const bidValues = auctionSuns.filter(notEmpty);
  const maxBidSun = (bidValues.length > 0) ? Math.max(...bidValues) : 0;
  const disableActions = actionsDisabled || auctionStarted;
  return (
    <Box sx={{ width: '100%', typography: 'body1' }}>
      <TabContext value={value}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <TabList
            onChange={handleChange}
            variant={(matchDownSm) ? 'scrollable' : 'standard'}
            centered={!matchDownSm}
            textColor="primary"
            indicatorColor="primary"
            aria-label="player tabs"
          >
            {players.map(({ playerName, points }, idx) => {
              const pointDiff = playerEstimatedDelta[playerName];
              // eslint-disable-next-line no-nested-ternary
              const labelSuffix = (auctionSuns[idx])
                ? ` (${auctionSuns[idx] || ''})`
                : (!active[idx]) ? ' (P)' : '';
              return (
                <Tab
                  iconPosition="start"
                  key={playerName}
                  label={`${playerName}${labelSuffix}`}
                  value={idx.toString()}
                  icon={(
                    <Badge
                      badgeContent={`${points}(${(pointDiff >= 0) ? '+' : ''}${pointDiff})`}
                      color="secondary"
                      max={100000}
                    >
                      <Leaderboard fontSize="large" color="action" />
                    </Badge>
                  )}
                />
              );
            })}
            <Tab
              iconPosition="end"
              label="Center Sun"
              key="gameLog"
              value={players.length.toString()}
              icon={(
                <Badge badgeContent={centerSun} color="secondary">
                  <WbSunny fontSize="large" color="action" />
                </Badge>
              )}
            />
          </TabList>
        </Box>
        {players.map((player: Player, idx: number) => (
          <TabPanel key={`${player.playerName}`} value={idx.toString()}>
            <Card
              sx={{ border: (current === idx) ? 2 : 0, borderColor: 'primary.main' }}
              variant={(current === idx) ? 'outlined' : undefined}
            >
              <Grid container spacing={2} columns={{ xs: 12 }}>
                <Actions
                  onDraw={onDraw}
                  onAuction={onAuction}
                  pointsIfWin={playerPointsIfWin[player.playerName]}
                  disabled={disableActions || current !== idx || player.playerName !== localName}
                />
                <PlayerInfo
                  auctionStarted={auctionStarted}
                  data={players[idx]}
                  isActive={active[idx]}
                  isCurrent={current === idx}
                  isLocalPlayer={player.playerName === localName}
                  bidWithSun={bidWithSun}
                  maxBidSun={maxBidSun}
                  selectTile={selectTile}
                  goldenGodSelected={player.playerName === localName && goldenGodSelected}
                />
              </Grid>
            </Card>
          </TabPanel>
        ))}
        <TabPanel key="gameLog" value={players.length.toString()}>
          <List
            dense
            sx={{
              width: '100%',
              bgcolor: 'background.paper',
              position: 'relative',
              overflow: 'auto',
              maxHeight: 300,
              '& ul': { padding: 0 },
            }}
          >
            {gameLog.map((entry: string) => (
              <ListItem>
                <ListItemText primary={entry} />
              </ListItem>
            )).reverse()}
          </List>
        </TabPanel>
      </TabContext>
    </Box>
  );
}

export default PlayersInfo;
