import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Header() {
  const { user, isAdmin, canModerate, logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
    const q = query.trim();
    if (q) navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <header className="header">
      <div className="container">
        <Link
          to="/profile"
          className="logo"
          style={{ transition: "opacity 0.2s" }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.2")}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
        >
          MISIS Tube
        </Link>
        {user && (
          <form className="header-search" onSubmit={handleSearch}>
            <input
              className="input"
              type="text"
              placeholder="Поиск пользователей..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.875rem", minWidth: "220px" }}
            />
          </form>
        )}
        <nav className="nav">
          {user ? (
            <>
              {isAdmin && (
                <Link to="/admin" className="nav-link" style={{ marginRight: "0.5rem" }}>
                  Управление
                </Link>
              )}
              {canModerate && (
                <a href="/interaction/admin/comments" className="nav-link" style={{ marginRight: "0.5rem" }}>
                  Модерация
                </a>
              )}
              <Link to="/profile" className="nav-link" style={{ marginRight: "0.5rem" }}>
                Профиль
              </Link>
              <a href="/player/" className="nav-link" style={{ marginRight: "0.5rem" }}>
                Смотреть
              </a>
              <button className="nav-link" onClick={logout} style={{ cursor: "pointer", border: "none", background: "none", fontFamily: "inherit", fontSize: "inherit", padding: 0 }}>
                Выйти
              </button>
            </>
          ) : (
            <a href="/auth/" className="nav-link">
              Войти
            </a>
          )}
        </nav>
      </div>
    </header>
  );
}
