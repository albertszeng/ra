import React, { useState, ChangeEvent, FormEvent } from 'react';
import {
  deleteGame,
  handleCommand,
} from './libs/game';

import './App.css';
import Game from './components/Game';
import Header from './components/Header';

type FormState = {
  gameId: string;
  command: string;
};

type GameState = {
  data: string;
};

function App() {
  // Tracks the state of the form.
  const [form, setForm] = useState<FormState>({
    command: '',
    gameId: '',
  });
  const onCommandChange = (e: ChangeEvent<HTMLInputElement>): void => {
    e.persist();
    setForm((prevForm: FormState) => ({
      ...prevForm,
      command: e.target.value,
    }));
  };
  const onGameIdChange = (e: ChangeEvent<HTMLInputElement>): void => {
    e.persist();
    setForm((prevForm: FormState) => ({
      ...prevForm,
      gameId: e.target.value,
    }));
  };

  const [game, setGame] = useState<GameState>({ data: '' });
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const { message, gameAsStr } = await handleCommand(form.gameId, form.command);
    if (message || !gameAsStr) {
      return;
    }
    setForm((prevForm: FormState) => ({ ...prevForm, data: '' }));
    setGame((prevGame: GameState) => ({ ...prevGame, data: gameAsStr }));
  };
  const handleDelete = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    await deleteGame(form.gameId);
  };
  return (
    <>
      <Header />
      <Game />
      <form className="register-form" onSubmit={handleSubmit}>
        {game.data && <div className="display-linebreak">{game.data}</div>}
        <input
          id="gameId"
          className="form-field"
          type="text"
          placeholder="Player Names/Game ID"
          value={form.gameId}
          onChange={onGameIdChange}
        />
        <input
          id="command"
          className="form-field"
          type="text"
          placeholder="Text Command"
          value={form.command}
          onChange={onCommandChange}
        />
        <button className="form-field" type="submit">
          Act
        </button>
        <button className="form-field" type="button" onClick={handleDelete}>
          Delete Game
        </button>
      </form>
    </>
  );
}

export default App;
