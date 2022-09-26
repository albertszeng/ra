import React, { useState, ChangeEvent, FormEvent } from 'react';
import './App.css';


type FormState = {
  gameId: string,
  command: string;
};

type GameState = {
  data: string;
};

type ApiResponse = {
  message?: string;
  gameId?: string;
  gameState?: string;
};

const apiUrl = process.env.BACKEND || "http://127.0.0.1:5000";

async function handleCommand(gameId: string, command: string): Promise<ApiResponse> {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gameId, command }),
  };
  const res = await fetch(`${apiUrl}/action`, requestOptions);
  return res.json();
}

async function startGame(players: string): Promise<ApiResponse> {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      player_names: players.split(","),
    }),
  };
  const res = await fetch(`${apiUrl}/start`, requestOptions);
  return res.json();
}

async function deleteGame(gameId: string): Promise<ApiResponse> {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      gameId: gameId,
    }),
  };
  const res = await fetch(`${apiUrl}/delete`, requestOptions);
  return res.json();
}

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
    const { message, gameState } = await handleCommand(form.gameId, form.command);
    if (message || !gameState) {
      alert(message);
      return;
    }
    setForm((form) => ({...form, data: ''}));
    setGame((game) => ({...game, data: gameState }));
  };
  const handleStart = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message, gameId, gameState } = await startGame(form.gameId);
    if (message || !gameId || !gameState) {
      alert(message);
      return;
    }
    setGame((game) => ({...game, data: gameState }));
    setForm((form) => ({...form, gameId }));
  };
  const handleDelete = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message } = await deleteGame(form.gameId);
    alert(message);
  };
  const handleLoad = async (e: FormEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const { message, gameState } = await handleCommand(form.gameId, 'LOAD');
    if (message || !gameState) {
      alert(message);
      return;
    }
    setGame((game) => ({...game, data: gameState }));
  }

  return (
    <div className="form-container">
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
    </div>
  );
}

export default App;
