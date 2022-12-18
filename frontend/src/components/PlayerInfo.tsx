import React, { useCallback } from 'react';

import PlayerActions from './PlayerActions';
import PlayerTiles from './PlayerTiles';
import type { Player, Tile } from '../libs/game';

type PlayerInfoProps = {
  data: Player
  isActive: boolean;
  isCurrent: boolean;
  isLocalPlayer: boolean;
  auctionStarted: boolean;
  maxBidSun: number;
  // Called with the index of the bid tile. 0 is lowest.
  bidWithSun: (idx: number) => void;
  // When a tile is selected by the player, this is called.
  selectTile: (player: Player, tile: Tile) => void;

};

function PlayerInfo({
  data: player, isActive, isCurrent, isLocalPlayer, auctionStarted,
  maxBidSun, bidWithSun, selectTile,
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
        isLocalPlayer={isLocalPlayer}
        auctionStarted={auctionStarted}
        maxBidSun={maxBidSun}
        availableSun={usableSun}
        unavailableSun={unusableSun}
        bidWithSun={bidWithSun}
      />
      <PlayerTiles tiles={collection} onTileClick={handleTileClick} />
    </>
  );
}

export default PlayerInfo;
