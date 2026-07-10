import React, { useState, useEffect } from 'react';
import UrlForm from './components/UrlForm';
import UrlList from './components/UrlList';
import './App.css';

export default function App() {
  const [links, setLinks] = useState([]);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');

  const fetchLinks = async (silent = false, clear = false) => {
    if (clear) {
      setLinks([]); // Immediately clear the links so they disappear during refresh
    }
    if (silent) {
      setIsRefreshing(true);
    } else {
      setIsInitialLoading(true);
    }
    setError('');
    try {
      const fetchPromise = fetch(`http://localhost:8000/links?_t=${Date.now()}&clear=${clear}`);
      
      let response;
      if (silent) {
        // Wait for both the network fetch and a 500ms delay to make the transition visible
        const [res] = await Promise.all([
          fetchPromise,
          new Promise(resolve => setTimeout(resolve, 500))
        ]);
        response = res;
      } else {
        response = await fetchPromise;
      }

      if (!response.ok) {
        throw new Error('Failed to retrieve links list from server.');
      }
      const data = await response.json();
      setLinks(data);
    } catch (err) {
      setError(err.message || 'Could not connect to backend.');
    } finally {
      setIsInitialLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLinks(false, true); // Clear storage on initial load
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">SnapLink</h1>
        <p className="app-subtitle">A minimal, clean, and fast URL shortener service</p>
      </header>

      <main style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <UrlForm onUrlShortened={() => fetchLinks(true, false)} />
        <UrlList
          links={links}
          isLoading={isInitialLoading}
          isRefreshing={isRefreshing}
          error={error}
          onRefresh={() => fetchLinks(true, false)}
        />
      </main>
    </div>
  );
}
