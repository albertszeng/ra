import React, { useState, ChangeEvent, FormEvent } from 'react';
import { 
  ApiResponse,
  deleteGame,
  Game,
  handleCommand,
  Player,
  startGame,
} from './libs/game'

import './App.css';


type FormState = {
  gameId: string,
  command: string;
};

type GameState = {
  data: string;
};


function App() {
  // Tracks the state of the form.
  const [form, setForm] = useState<FormState>({
    command: '',
    gameId: ''
  });
  const onCommandChange = (e: ChangeEvent<HTMLInputElement>): void => {
    e.persist();
    setForm((form) => ({
      ...form,
      command: e.target.value,
    }));
  };
  const onGameIdChange = (e: ChangeEvent<HTMLInputElement>): void => {
    e.persist();
    setForm((form) => ({
      ...form,
      gameId: e.target.value,
    }));
  };

  const [game, setGame] = useState<GameState>({data: ''});
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const { message, gameAsStr } = await handleCommand(form.gameId, form.command);
    if (message || !gameAsStr) {
      alert(message);
      return;
    }
    setForm((form) => ({...form, data: ''}));
    setGame((game) => ({...game, data: gameAsStr }));
  };
  const handleStart = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message, gameId, gameAsStr } = await startGame(form.gameId);
    if (message || !gameId || !gameAsStr) {
      alert(message);
      return;
    }
    setGame((game) => ({...game, data: gameAsStr }));
    setForm((form) => ({...form, gameId }));
  };
  const handleDelete = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message } = await deleteGame(form.gameId);
    alert(message);
  };
  const handleLoad = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message, gameAsStr } = await handleCommand(form.gameId, 'LOAD');
    if (message || !gameAsStr) {
      alert(message);
      return;
    }
    setGame((game) => ({...game, data: gameAsStr }));
  }

  return (
    <form className="register-form" onSubmit={handleSubmit}>
      {game.data && <div className='display-linebreak'>{game.data}</div>}
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
      <button className="form-field" onClick={handleStart}>
        Start New Game
      </button>
      <button className="form-field" onClick={handleLoad}>
        Load Game
      </button>
      <button className="form-field" onClick={handleDelete}>
        Delete Game
      </button>
    </form>
  );
}

export default App;
