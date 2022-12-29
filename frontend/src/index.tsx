import React from 'react';
import ReactDOM from 'react-dom/client';
import TagManager from 'react-gtm-module';

import { closeSnackbar, SnackbarProvider } from 'notistack';

import { IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';

import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const tagManagerArgs = {
  gtmId: 'G-SYVY210CLF',
};
TagManager.initialize(tagManagerArgs);

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement,
);
root.render(
  <React.StrictMode>
    <SnackbarProvider
      preventDuplicate
      autoHideDuration={5000}
      maxSnack={3}
      action={(snackbarId) => (
        <IconButton
          aria-label="delete"
          onClick={() => closeSnackbar(snackbarId)}
        >
          <Delete />
        </IconButton>
      )}
    >
      <App />
    </SnackbarProvider>
  </React.StrictMode>,
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
