import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import SearchPage from './pages/SearchPage'
import WatchPage from './pages/WatchPage'

function App() {
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