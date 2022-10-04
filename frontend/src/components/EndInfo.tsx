import React, { useState } from 'react';
import styled from 'styled-components';

const EndGameContainer = styled.section`
  margin-top: auto;
  text-align: center;
  font-size: 1.3rem;
`;

const EndGameButtonContainer = styled.div`
  width: 70%;
  margin: 3rem auto 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
`;

const EndGameButtonYes = styled.button`
  width: 65%;
  border-radius: 1rem;
  border: none;
  font-size: 1.5rem;
  padding-block: 0.5rem;
  cursor: pointer;
  background-color: var(--violet-blue-crayola);
  color: var(--off-white);
  text-transform: uppercase;
  box-shadow: var(--oxford-blue-light) 0px 1px 2px;
`;
const EndGameButtonNo = styled.button`
  width: 35%;
  border-radius: 1rem;
  border: 1px solid var(--oxford-blue);
  background-color: var(--off-white);
  font-size: 1.2rem;
  padding-block: 0.5rem;
  cursor: pointer;
  text-transform: lowercase;
  box-shadow: var(--oxford-blue-light) 0px 1px 2px;
`;

type EndInfoProps = {
  resetGame: () => void;
};

function EndInfo({ resetGame }: EndInfoProps): JSX.Element {
  const [isFinished, setIsFinished] = useState(false);
  return (
    <EndGameContainer>
      {isFinished ? (
        <p>Thanks for playing!</p>
      ) : (
        <>
          <h2>Well done!</h2>
          <p>You have completed the game!</p>
          <p>Would you like to play again?</p>
          <EndGameButtonContainer>
            <EndGameButtonYes onClick={resetGame}>Yes</EndGameButtonYes>
            <EndGameButtonNo
              onClick={() => {
                setIsFinished(true);
              }}
            >
              No
            </EndGameButtonNo>
          </EndGameButtonContainer>
        </>
      )}
    </EndGameContainer>
  );
}

export default EndInfo;
