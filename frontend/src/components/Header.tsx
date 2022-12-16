import React, { useContext } from 'react';
import styled from 'styled-components';

import { Brightness4, Brightness7 } from '@mui/icons-material';
import { IconButton } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import ColorModeContext from '../common';
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
`;

function Header() {
  const theme = useTheme();
  const colorMode = useContext(ColorModeContext);
  return (
    <MainHeader>
      <img src={sword} alt="sword" width="50px" height="50px" />
      <Heading>Online Ra Game</Heading>
      <IconButton sx={{ ml: 1 }} onClick={colorMode.toggleColorMode} color="inherit">
        {theme.palette.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
      </IconButton>
      <img src={shield} alt="sword" width="50px" height="50px" />
    </MainHeader>
  );
}

export default Header;
