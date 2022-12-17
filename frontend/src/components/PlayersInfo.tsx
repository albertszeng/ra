import React, {
  useCallback,
  useEffect,
  useState,
  SyntheticEvent,
} from 'react';

import { Leaderboard } from '@mui/icons-material';
import { TabContext, TabList, TabPanel } from '@mui/lab';
import {
  Badge,
  Box,
  Card,
  Tab,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

import { Actions, ActionsProps } from './Actions';
import PlayerInfo from './PlayerInfo';
import type { Player, Tile } from '../libs/game';

type PlayersInfoProps = {
  players: Player[];
  active: boolean[];
  current: number;
  auctionStarted: boolean;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
  // Called when a player selects a tile in their bag.
  selectTile: (player: Player, tile: Tile) => void;
  actionsProps: ActionsProps;
};

function PlayersInfo({
  players, active, current, auctionStarted, bidWithSun, selectTile,
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
  return (
    <Box sx={{ width: '100%', typography: 'body1' }}>
      <TabContext value={value}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <TabList
            onChange={handleChange}
            centered
            textColor="primary"
            indicatorColor="primary"
            aria-label="player tabs"
          >
            {players.map(({ playerName, points }, idx) => (
              <Tab
                iconPosition="start"
                key={playerName}
                label={playerName}
                value={idx.toString()}
                disabled={!active[idx]}
                icon={(
                  <Badge badgeContent={points} color="secondary">
                    <Leaderboard fontSize="large" color="action" />
                  </Badge>
                )}
              />
            ))}
          </TabList>
        </Box>
        {players.map((player: Player, idx: number) => (
          <TabPanel key={`${player.playerName}`} value={idx.toString()}>
            <Card variant={(current === idx) ? 'outlined' : undefined}>
              <Grid container spacing={2}>
                <Grid xs={12}>
                  <Actions
                    onDraw={onDraw}
                    onAuction={onAuction}
                    disabled={actionsDisabled || current !== idx}
                    resetGame={resetGame}
                  />
                </Grid>
                <Grid xs={12}>
                  <PlayerInfo
                    auctionStarted={auctionStarted}
                    data={players[idx]}
                    isActive={active[idx]}
                    isCurrent={current === idx}
                    bidWithSun={bidWithSun}
                    selectTile={selectTile}
                  />
                </Grid>
              </Grid>
            </Card>
          </TabPanel>
        ))}
      </TabContext>
    </Box>
  );
}

export default PlayersInfo;
