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
              {canModerate && (
                <a
                  href="/interaction/admin/comments"
                  className="btn btn-sm btn-outline"
                  style={{ color: "white", borderColor: "white", marginRight: "0.5rem" }}
                >
                  Модерация
                </a>
              )}
              <Link
                to="/profile"
                className="btn btn-sm btn-outline"
                style={{ color: "white", borderColor: "white", marginRight: "0.5rem" }}
              >
                Профиль
              </Link>
              <a
                href="/player/"
                className="btn btn-sm btn-outline"
                style={{ color: "white", borderColor: "white", marginRight: "0.5rem" }}
              >
                Смотреть
              </a>
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
              href="/auth/"
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
