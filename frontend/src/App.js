import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [contentFile, setContentFile] = useState(null);
  const [styleFile, setStyleFile] = useState(null);
  const [contentPreview, setContentPreview] = useState(null);
  const [stylePreview, setStylePreview] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleContentChange = (e) => {
    const file = e.target.files[0];
    setContentFile(file);
    
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setContentPreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setContentPreview(null);
    }
  };

  const handleStyleChange = (e) => {
    const file = e.target.files[0];
    setStyleFile(file);
    
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setStylePreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setStylePreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!contentFile || !styleFile) {
      setError('Please select both content and style images');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('content', contentFile);
    formData.append('style', styleFile);
    
    try {
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setResultImage(`http://localhost:5000${response.data.result}`);
      setLoading(false);
    } catch (err) {
      setError('Error processing images. Please try again.');
      setLoading(false);
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Image Style Transfer</h1>
        <p>Apply artistic styles to your images using neural style transfer</p>
      </header>
      
      <main>
        <form onSubmit={handleSubmit}>
          <div className="image-inputs">
            <div className="image-input">
              <h2>Content Image</h2>
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleContentChange}
              />
              {contentPreview && (
                <div className="image-preview">
                  <img src={contentPreview} alt="Content preview" />
                </div>
              )}
            </div>
            
            <div className="image-input">
              <h2>Style Image</h2>
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleStyleChange}
              />
              {stylePreview && (
                <div className="image-preview">
                  <img src={stylePreview} alt="Style preview" />
                </div>
              )}
            </div>
          </div>
          
          <button 
            type="submit" 
            disabled={loading || !contentFile || !styleFile}
          >
            {loading ? 'Processing...' : 'Transfer Style'}
          </button>
          
          {error && <p className="error">{error}</p>}
        </form>
        
        {loading && (
          <div className="loading">
            <p>Processing your images. This may take a few minutes...</p>
          </div>
        )}
        
        {resultImage && !loading && (
          <div className="result">
            <h2>Result</h2>
            <img src={resultImage} alt="Style transfer result" />
            <a href={resultImage} download className="download-btn">
              Download Result
            </a>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;