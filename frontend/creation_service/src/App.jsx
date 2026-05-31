import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
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
    <BrowserRouter>
      <Header />
      <main className="container py-6">
        <Routes>
          <Route path="/" element={<VideoListPage />} />
          <Route path="/videos/:id" element={<VideoDetailPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;