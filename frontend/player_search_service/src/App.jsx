import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import Header from './components/Header'
import SearchPage from './pages/SearchPage'
import WatchPage from './pages/WatchPage'

function App() {
  useEffect(() => {
    const hash = window.location.hash;
    if (hash && hash.includes('access_token=')) {
      window.location.hash = '';
      const params = new URLSearchParams(hash.slice(1));
      const accessToken = params.get('access_token');
      const refreshToken = params.get('refresh_token');
      if (accessToken) {
        localStorage.setItem('auth_user', JSON.stringify({ token: accessToken }));
        if (refreshToken) {
          localStorage.setItem('auth_refresh', refreshToken);
        }
        window.location.reload();
      }
    }
  }, []);

  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Header />
        <main style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/watch/:id" element={<WatchPage />} />
            <Route path="/profile" element={<div className="container p-6">Страница профиля</div>} />
            <Route path="/upload" element={<div className="container p-6">Страница загрузки</div>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App