import React from 'react';
import './App.css';
import StyleTransfer from './components/StyleTransfer';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Neural Style Transfer</h1>
      </header>
      <main>
        <StyleTransfer />
      </main>
      <footer>
        <p>Created with TensorFlow and React</p>
      </footer>
    </div>
  );
}

export default App;