import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Header() {
  const location = useLocation();

  return (
    <header className="header">
      <div className="container">
        <Link to="/" className="logo">
          MISISTUBE
        </Link>
        <nav className="nav">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Поиск
          </Link>
          <a href="/docs" className="nav-link" target="_blank" rel="noopener noreferrer">
            API Docs
          </a>
        </nav>
      </div>
    </header>
  );
}

export default Header;