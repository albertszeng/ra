import React, { useState, ChangeEvent, FormEvent } from 'react';
import {
  DefaultGame,
  deleteGame,
  handleCommand,
  startGame,
} from './libs/game';

import './App.css';
import Game from './components/Game';
import Header from './components/Header';
import type { Game as GameProps } from './libs/game';

type FormState = {
  gameId: string;
  command: string;
};

type GameState = {
  data: string;
  game: GameProps;
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

  const [game, setGame] = useState<GameState>({ data: '', game: DefaultGame });
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const { message, gameAsStr, gameState } = await handleCommand(form.gameId, form.command);
    if (message || !gameAsStr || !gameState) {
      alert(message);
      return;
    }
    setForm((prevForm: FormState) => ({ ...prevForm, data: '' }));
    setGame((prevGame: GameState) => ({ ...prevGame, data: gameAsStr, game: gameState }));
  };
  const handleStart = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const {
      message,
      gameId,
      gameAsStr,
      gameState,
    } = await startGame(form.gameId);
    if (message || !gameId || !gameAsStr || !gameState) {
      alert(message);
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, data: gameAsStr, game: gameState }));
    setForm((prevForm: FormState) => ({ ...prevForm, gameId }));
  };
  const handleDelete = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message } = await deleteGame(form.gameId);
    alert(message);
  };
  const handleLoad = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message, gameAsStr, gameState } = await handleCommand(form.gameId, 'LOAD');
    if (message || !gameAsStr || !gameState) {
      alert(message);
      return;
    }
    setGame((prevGame: GameState) => ({ ...prevGame, data: gameAsStr, game: gameState }));
  };

  return (
    <>
      <Header />
      <Game game={game.game} />
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
        <button className="form-field" type="button" onClick={handleStart}>
          Start New Game
        </button>
        <button className="form-field" type="button" onClick={handleLoad}>
          Load Game
        </button>
        <button className="form-field" type="button" onClick={handleDelete}>
          Delete Game
        </button>
      </form>
    </>
  );
}

export default App;
