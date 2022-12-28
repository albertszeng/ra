import React from 'react';

import { Alert, Snackbar } from '@mui/material';

import type { AlertData } from '../libs/game';

type AlertModalProps = {
  alert: AlertData;
  setAlert: (alert: AlertData) => void;
};

function AlertModal({ alert, setAlert }: AlertModalProps): JSX.Element {
  return (
    <Snackbar
      open={alert.show}
      autoHideDuration={(alert.permanent) ? undefined : 2500}
      onClose={() => setAlert({ show: false, message: '' })}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <Alert
        onClose={() => setAlert({ show: false, message: '' })}
        variant="filled"
        severity={alert.level}
      >
        {alert.message}
      </Alert>
    </Snackbar>
  );
}

export default AlertModal;
