import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Header() {
  const { user, isAdmin, logout } = useAuth();
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
        <Link to="/profile" style={{ textDecoration: "none", color: "inherit" }}>
          <span className="logo">MISIS Tube</span>
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
                <Link
                  to="/admin"
                  className="btn btn-sm btn-outline"
                  style={{ color: "white", borderColor: "white", marginRight: "0.5rem" }}
                >
                  Управление
                </Link>
              )}
              <Link
                to="/profile"
                className="btn btn-sm btn-outline"
                style={{ color: "white", borderColor: "white", marginRight: "0.5rem" }}
              >
                Профиль
              </Link>
              <button
                onClick={() => {
                  const token = user.token;
                  const refreshToken = localStorage.getItem('refresh_token') || '';
                  window.location.href = `http://localhost:5177/#access_token=${encodeURIComponent(token)}&refresh_token=${encodeURIComponent(refreshToken)}`;
                }}
                className="btn btn-sm btn-outline"
                style={{ color: "white", borderColor: "white", marginRight: "0.5rem" }}
              >
                Смотреть
              </button>
              <button
                className="btn btn-sm btn-outline"
                onClick={logout}
                style={{ color: "white", borderColor: "white" }}
              >
                Выйти
              </button>
            </>
          ) : (
            <a
              href="http://localhost:5174"
              className="btn btn-sm btn-outline"
              style={{ color: "white", borderColor: "white" }}
            >
              Войти
            </a>
          )}
        </nav>
      </div>
    </header>
  );
}
