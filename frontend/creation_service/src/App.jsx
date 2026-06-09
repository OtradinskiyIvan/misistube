import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { VideoListPage } from './pages/VideoListPage';
import { VideoDetailPage } from './pages/VideoDetailPage';
import { UploadPage } from './pages/UploadPage';
import '@shared/style_sample.css';

function Header() {
  return (
    <header className="header">
      <div className="container">
        <Link to="/" className="logo">MisisTube</Link>
        <nav className="nav">
          <Link to="/" className="nav-link">Главная</Link>
          <Link to="/upload" className="nav-link">Загрузить</Link>
        </nav>
      </div>
    </header>
  );
}

function App() {
  return (
    <BrowserRouter basename="/creation">
      <Header />
      <main className="container py-6">
        <Routes>
          <Route path="/" element={<VideoListPage />} />
          <Route path="/videos/upload" element={<Navigate to="/upload" replace />} />
          <Route path="/videos/:id" element={<VideoDetailPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="*" element={
            <div className="text-center py-20">
              <h1 className="text-4xl font-bold text-gray-300">404</h1>
              <p className="text-gray-500 mt-2">Страница не найдена</p>
              <Link to="/" className="btn btn-primary mt-4 inline-block">На главную</Link>
            </div>
          } />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;