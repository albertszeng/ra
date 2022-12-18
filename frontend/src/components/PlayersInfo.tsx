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
  Tab,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Unstable_Grid2';

import { Actions, ActionsProps } from './Actions';
import PlayerInfo from './PlayerInfo';
import { notEmpty } from '../libs/game';
import type { Player, Tile } from '../libs/game';

type PlayersInfoProps = {
  // Name of the local player, if any. Null is when spectating.
  localName: string | null;
  players: Player[];
  active: boolean[];
  current: number;
  centerSun: number;
  // For each player i, how much sun they have bid (if any).
  auctionSuns: (number | null)[];
  auctionStarted: boolean;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
  // Called when a player selects a tile in their bag.
  selectTile: (player: Player, tile: Tile) => void;
  actionsProps: ActionsProps;
};

function PlayersInfo({
  localName, players, active, current, auctionStarted, bidWithSun,
  selectTile, centerSun, auctionSuns,
  actionsProps: {
    disabled: actionsDisabled, onDraw, onAuction, resetGame,
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
                    <Badge badgeContent={points} color="secondary">
                      <Leaderboard fontSize="large" color="action" />
                    </Badge>
                  )}
                />
              );
            })}
            <Tab
              disabled
              iconPosition="end"
              label="Center Sun"
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
            <Card variant={(current === idx) ? 'outlined' : undefined}>
              <Grid container spacing={2} columns={{ xs: 12 }}>
                <Actions
                  onDraw={onDraw}
                  onAuction={onAuction}
                  disabled={actionsDisabled || current !== idx
                    || auctionStarted || player.playerName !== localName}
                  resetGame={resetGame}
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
                />
              </Grid>
            </Card>
          </TabPanel>
        ))}
      </TabContext>
    </Box>
  );
}

export default PlayersInfo;
