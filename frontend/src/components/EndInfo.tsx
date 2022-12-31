import React from 'react';

import { Typography } from '@mui/material';

import type { Player } from '../libs/game';

type EndInfoProps = {
  players: Player[];
};
function EndInfo({ players }: EndInfoProps): JSX.Element {
  const maxPoints = Math.max(...players.map(({ points }: Player) => points));
  const winners = players.filter(
    ({ points }: Player) => points === maxPoints,
  ).map(({ playerName }) => playerName);
  return (
    <Typography variant="h4">
      {`Winner${(winners.length === 1) ? '' : 's'}: ${winners.toString()}`}
    </Typography>
  );
}

export default EndInfo;
