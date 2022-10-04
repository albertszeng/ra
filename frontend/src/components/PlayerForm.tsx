import React, { ChangeEvent, useState } from 'react';
import ReactTooltip from 'react-tooltip';
import styled from 'styled-components';

const IntroText = styled.p`
  font-size: 2rem;
`;

const StartButton = styled.button`
  width: 40%;
  border-radius: 1rem;
  border: none;
  font-size: 2rem;
  padding-block: 0.5rem;
  background-color: var(--violet-blue-crayola);
  color: var(--off-white);
  letter-spacing: 0.2rem;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: var(--oxford-blue-light) 0px 1px 3px;
`;

const PlayerInput = styled.input`
  padding: 0.5em;
  margin: 0.5em;
  color: 'palevioletred';
  border-radius: 3px;
  font-size: 18pt;
`;

type PlayerFormProps = {
  handleSubmit: () => void;
};

function isValid(input: string): boolean {
  if (input.includes(',')) {
    // Must be player names. Validate at least 2.
    const segments = input.split(',');
    return segments && segments.length >= 2;
  }
  // Must be game id.
  let hex = input;
  if (input.includes('-')) {
    hex = input.replace('-', '');
  }
  return (parseInt(hex, 16).toString(16) === hex.toLowerCase());
}

function PlayerForm({ handleSubmit }: PlayerFormProps): JSX.Element {
  const [playersStr, setPlayers] = useState<string>('');
  const [formValid, setFormValid] = useState(false);
  const handleChange = (e: ChangeEvent<HTMLInputElement>): void => {
    e.persist();
    setFormValid(isValid(e.target.value));
    setPlayers(e.target.value);
  };
  const [tooltip, showTooltip] = useState(false);
  return (
    <>
      { tooltip && (
        <ReactTooltip
          id="players or id"
          type="info"
          place="bottom"
        >
          Enter comma-seperated list of players or the Game ID of an existing game.
        </ReactTooltip>
      )}
      <form onSubmit={handleSubmit}>
        <IntroText>Start a Game of Ra!</IntroText>
        {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
        <label htmlFor="players">
          Player Names/Game ID:
          {' '}
          <PlayerInput
            data-tip
            data-for="players or id"
            id="players"
            type="text"
            value={playersStr}
            onChange={handleChange}
            onMouseEnter={() => { showTooltip(true); }}
            onMouseLeave={() => { showTooltip(false); }}
          />
        </label>
        <StartButton
          type="submit"
          disabled={!formValid}
        >
          Start
        </StartButton>
      </form>
    </>
  );
}

export default PlayerForm;
