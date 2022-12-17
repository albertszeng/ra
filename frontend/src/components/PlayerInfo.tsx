import React, { useCallback } from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import PlayerActions from './PlayerActions';
import PlayerTiles from './PlayerTiles';
import type { Player, Tile } from '../libs/game';

type PlayerInfoProps = {
  data: Player
  isActive: boolean;
  isCurrent: boolean;
  auctionStarted: boolean;
  minBidSun: number;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
  // When a tile is selected by the player, this is called.
  selectTile: (player: Player, tile: Tile) => void;

};

function PlayerInfo({
  data: player, isActive, isCurrent, auctionStarted, minBidSun, bidWithSun, selectTile,
}: PlayerInfoProps): JSX.Element {
  const { collection, usableSun, unusableSun } = player;
  const handleTileClick = useCallback(
    (tile: Tile) => selectTile(player, tile),
    [player, selectTile],
  );
  return (
    <>
      <PlayerActions
        isActive={isActive}
        isCurrent={isCurrent}
        auctionStarted={auctionStarted}
        minBidSun={minBidSun}
        availableSun={usableSun}
        unavailableSun={unusableSun}
        bidWithSun={bidWithSun}
      />
      <Grid xs={12}>
        <PlayerTiles tiles={collection} onTileClick={handleTileClick} />
      </Grid>
    </>
  );
}

export default PlayerInfo;
