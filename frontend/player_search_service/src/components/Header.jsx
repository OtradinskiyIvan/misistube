import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="header">
      <div className="container">
        <Link to="/" className="logo">MISIS Tube</Link>
        <nav className="nav">
          <Link to="/" className="nav-link">Поиск</Link>
          <a href="/user/profile" className="nav-link">Профиль</a>
        </nav>
      </div>
    </header>
  )
}