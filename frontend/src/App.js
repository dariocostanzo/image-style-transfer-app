import React from 'react';
import './App.css';
import StyleTransfer from './components/StyleTransfer';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Image Style Transfer</h1>
      </header>
      <main>
        <StyleTransfer />
      </main>
      <footer>
        <p>Neural Style Transfer App</p>
      </footer>
    </div>
  );
}

export default App;