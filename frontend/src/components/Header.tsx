import React from 'react';
import styled from 'styled-components';
import sword from '../images/sword_01.png';
import shield from '../images/wooden_shield.png';

const MainHeader = styled.header`
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  width: 100%;
`;

const Heading = styled.h1`
  color: var(--violet-blue-crayola);
  font-size: min(8vw, 3rem);
  padding-inline: 2rem;
`;

function Header() {
  return (
    <MainHeader>
      <img src={sword} alt="sword" width="50px" height="50px" />
      <Heading>Online Ra Game</Heading>
      <img src={shield} alt="sword" width="50px" height="50px" />
    </MainHeader>
  );
}

export default Header;
