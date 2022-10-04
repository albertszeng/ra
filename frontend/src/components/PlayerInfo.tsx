import React from 'react';
// import styled from 'styled-components';

import type { Player } from '../libs/game';

type PlayerInfoProps = {
  data: Player
};

function PlayerInfo({ data }: PlayerInfoProps) {
  return (
    <>
      <p>{`Name: ${data.player_name} (${data.points})`}</p>
      <p>{`Tiles: ${data.collection.toString()}`}</p>
      <p>{`Sun: ${data.usable_sun.toString()}`}</p>
      <p>{`Used Sun: ${data.unusable_sun.toString()}`}</p>
    </>
  );
}

export default PlayerInfo;
