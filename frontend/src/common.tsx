import { createContext } from 'react';
import io from 'socket.io-client';

const ColorModeContext = createContext({ toggleColorMode: () => { /* void */ } });
const apiUrl = (process.env.REACT_APP_BACKEND) ? `https://${process.env.REACT_APP_BACKEND}` : 'http://0.0.0.0:8080';
const socket = io((process.env.REACT_APP_BACKEND) ? `wss://${process.env.REACT_APP_BACKEND}` : 'ws://0.0.0.0:8080');

type WarningLevel = 'success' | 'info' | 'warning' | 'error';

export {
  apiUrl,
  ColorModeContext,
  socket,
};
export type {
  WarningLevel,
};
