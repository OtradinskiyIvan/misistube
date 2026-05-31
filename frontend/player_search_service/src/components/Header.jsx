import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="header">
      <div className="container">
        <Link to="/" className="logo">MISIS Tube</Link>
        <nav className="nav">
          <Link to="/search" className="nav-link">Поиск</Link>
          <Link to="/upload" className="nav-link">Загрузить</Link>
          <Link to="/profile" className="nav-link">Профиль</Link>
        </nav>
      </div>
    </header>
  )
}