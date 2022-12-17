import React, { useEffect } from 'react';
import styled from 'styled-components';

import { Leaderboard } from '@mui/icons-material';
import { TabContext, TabList, TabPanel } from '@mui/lab';
import { Badge, Box, Tab } from '@mui/material';

import { Actions, ActionsProps } from './Actions';
import PlayerInfo from './PlayerInfo';
import type { Player } from '../libs/game';

interface PlayerBoxProps {
  readonly isActive: boolean;
  readonly isCurrent: boolean;
}

// margin-top: auto;
const PlayerBox = styled.section<PlayerBoxProps>`
  font-size: 1.5rem;
  border-radius: 15px;
  background-color: ${(props) => (props.isActive ? 'lightblue' : 'lightgray')};
  border: 2px solid ${(props) => (props.isCurrent ? 'blue' : 'black')};
`;

type PlayersInfoProps = {
  players: Player[];
  active: boolean[];
  current: number;
  auctionStarted: boolean;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
  actionsProps: ActionsProps;
};

function PlayersInfo({
  players, active, current, auctionStarted, bidWithSun,
  actionsProps: {
    disabled: actionsDisabled, onDraw, onAuction, resetGame,
  },
}: PlayersInfoProps) {
  const [value, setValue] = React.useState(current.toString());
  const handleChange = (event: React.SyntheticEvent, newValue: string) => {
    setValue(newValue);
  };
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
          <TabPanel value={idx.toString()}>
            <PlayerBox
              key={player.playerName}
              isActive={active[idx]}
              isCurrent={current === idx}
            >
              <Actions
                onDraw={onDraw}
                onAuction={onAuction}
                disabled={actionsDisabled || current !== idx}
                resetGame={resetGame}
              />
              <PlayerInfo
                auctionStarted={auctionStarted}
                data={players[idx]}
                isActive={active[idx]}
                isCurrent={current === idx}
                bidWithSun={bidWithSun}
              />
            </PlayerBox>
          </TabPanel>
        ))}
      </TabContext>
    </Box>
  );
}

export default PlayersInfo;
