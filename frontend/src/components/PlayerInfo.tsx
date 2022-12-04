import React from 'react';
// import styled from 'styled-components';

import type { Player } from '../libs/game';

type PlayerInfoProps = {
  data: Player
};

function PlayerInfo({ data }: PlayerInfoProps) {
  return (
    <>
      <p>{`Name: ${data.playerName} (${data.points})`}</p>
      <p>{`Tiles: ${data.collection.toString()}`}</p>
      <p>{`Sun: ${data.usableSun.toString()}`}</p>
      <p>{`Used Sun: ${data.unusableSun.toString()}`}</p>
    </>
  );
}

export default PlayerInfo;
