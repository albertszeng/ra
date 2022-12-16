import React from 'react';
import styled from 'styled-components';

import Grid from '@mui/material/Unstable_Grid2';

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
};

function PlayersInfo({
  players, active, current, auctionStarted, bidWithSun,
}: PlayersInfoProps) {
  return (
    <Grid container spacing={{ xs: 1, md: 2 }}>
      {players.map((player: Player, idx: number) => (
        <Grid xs={12}>
          <PlayerBox key={player.playerName} isActive={active[idx]} isCurrent={current === idx}>
            <PlayerInfo
              auctionStarted={auctionStarted}
              data={players[idx]}
              isActive={active[idx]}
              isCurrent={current === idx}
              bidWithSun={bidWithSun}
            />
          </PlayerBox>
        </Grid>
      ))}
    </Grid>
  );
}

export default PlayersInfo;
