import React, { useState, ChangeEvent, FormEvent } from 'react';
import './App.css';


type FormState = {
  data: string;
};

type GameState = {
  data: string;
};

async function handleCommand(command: string): Promise<string> {
  const apiUrl = process.env.BACKEND || "http://127.0.0.1:5000";
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command })
  };
  const res = await fetch(apiUrl, requestOptions);
  const data = await res.json();
  return data.data;
}

function App() {
  // Tracks the state of the form.
  const [form, setForm] = useState<FormState>({
    data: ''
  });
  const handleFormOnChange = (e: ChangeEvent<HTMLInputElement>): void => {
    e.persist();
    setForm((form) => ({
      ...form,
      data: e.target.value,
    }));
  };

  const [game, setGame] = useState<GameState>({data: ''});
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    const response = await handleCommand(form.data);
    
    setForm((form) => ({...form, data: ''}));
    setGame((game) => ({...game, data: response }));
    
  };

  return (
    <div className="form-container">
      <form className="register-form" onSubmit={handleSubmit}>
        {/* Uncomment the next line to show the success message */}
        {game.data && <div className='success-message'>{game.data}</div>}
        <input
          id="data"
          className="form-field"
          type="text"
          placeholder="Text Command"
          value={form.data}
          onChange={handleFormOnChange}
        />
        <button className="form-field" type="submit">
          Submit
        </button>
      </form>
    </div>
  );
}

export default App;
