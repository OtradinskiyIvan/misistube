import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import VideoList from './components/VideoList';
import VideoPlayer from './components/VideoPlayer';
import apiClient from './api/client';
import './App.css';

function App() {
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async ({ query, limit, offset }) => {
    try {
      setIsLoading(true);
      setError(null);
      const results = await apiClient.searchVideos(query, offset, limit);
      setSearchResults(results);
    } catch (err) {
      setError(err.message || 'Произошла ошибка при поиске');
      setSearchResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Routes>
          <Route 
            path="/" 
            element={
              <div className="container">
                <div className="page-header mb-6">
                  <h1>Поиск видео</h1>
                  <p className="text-muted">Найдите нужное видео по названию или тегам</p>
                </div>
                
                <SearchForm onSearch={handleSearch} isLoading={isLoading} />
                
                {error && (
                  <div className="error-message mb-4">
                    <strong>Ошибка:</strong> {error}
                  </div>
                )}
                
                {searchResults && (
                  <div className="search-info mb-4">
                    <p>
                      Найдено: <strong>{searchResults.total}</strong> видео
                      {searchResults.total > 0 && (
                        <span> (показано {searchResults.items.length})</span>
                      )}
                    </p>
                  </div>
                )}
                
                <VideoList 
                  videos={searchResults?.items} 
                  isLoading={isLoading}
                  error={error}
                />
              </div>
            } 
          />
          <Route path="/video/:videoId" element={<VideoPlayer />} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="container">
          <p>&copy; 2026 MISISTUBE. Player & Searching Service</p>
        </div>
      </footer>
    </div>
  );
}

export default App;