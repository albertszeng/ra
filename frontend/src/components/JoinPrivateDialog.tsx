import React, { ChangeEvent, useState } from 'react';

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  InputAdornment,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
} from '@mui/material';
import {
  Cancel,
  Diversity3,
  Games,
} from '@mui/icons-material';

function isGameId(input: string): boolean {
  // Assume it must be a game id.
  let hex = input;
  if (input.includes('-')) {
    hex = input.replace(/-|\s/g, '');
  }
  return hex.length === 32;
}

function isValid(input: string): boolean {
  return input !== '' && isGameId(input);
}

type JoinPrivateDialogProps = {
  onJoin: (id: string) => void;
};
function JoinPrivateDialog({ onJoin }: JoinPrivateDialogProps): JSX.Element {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const onClose = () => setOpen(false);
  return (
    <>
      <ListItemButton onClick={() => setOpen(true)} dense>
        <ListItemIcon>
          <Diversity3 />
        </ListItemIcon>
        <ListItemText primary="Join Private Game" />
      </ListItemButton>
      <Dialog open={open} onClose={onClose}>
        <DialogTitle>Join A Private Game</DialogTitle>
        <DialogContent>
          <DialogContentText>
            To join, please enter the full ID of the game.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="gameId"
            label="Game ID"
            type="text"
            fullWidth
            variant="filled"
            value={input}
            onChange={({ target: { value } }: ChangeEvent<HTMLInputElement>) => setInput(value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Games />
                </InputAdornment>
              ),
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={onClose}
            endIcon={<Cancel />}
          >
            Cancel
          </Button>
          <Button
            disabled={!isValid(input)}
            onClick={() => onJoin('')}
            endIcon={<Diversity3 />}
          >
            Join
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default JoinPrivateDialog;
