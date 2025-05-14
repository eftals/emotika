import React from 'react';
import './App.css';
import ChatBox from './components/ChatBox';
import { useSession } from './hooks/useSession';

function App() {
  // Initialize session management
  useSession();

  return (
    <div className="App">
      <header className="App-header">
        <h1>Emotika Chat</h1>
      </header>
      <main>
        <ChatBox />
      </main>
    </div>
  );
}

export default App; 