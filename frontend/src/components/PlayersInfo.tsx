import React from 'react';
import styled from 'styled-components';

import PlayerInfo from './PlayerInfo';
import type { Player } from '../libs/game';

interface PlayerBoxProps {
  readonly isActive: boolean;
  readonly isCurrent: boolean;
}

// margin-top: auto;
const PlayerBox = styled.section<PlayerBoxProps>`
  display: flex;
  justify-content: space-evenly;
  width: 80%;
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
    <>
      {players.map((player: Player, idx: number) => (
        <PlayerBox key={player.playerName} isActive={active[idx]} isCurrent={current === idx}>
          <PlayerInfo
            auctionStarted={auctionStarted}
            data={players[idx]}
            isActive={active[idx]}
            isCurrent={current === idx}
            bidWithSun={bidWithSun}
          />
        </PlayerBox>
      ))}
    </>
  );
}

export default PlayersInfo;
