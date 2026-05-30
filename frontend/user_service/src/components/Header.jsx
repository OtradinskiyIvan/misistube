import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Header() {
  const { user, isAdmin, logout } = useAuth();

  return (
    <header className="header">
      <div className="container">
        <Link to="/" className="logo">
          MISIS Tube
        </Link>
        <nav className="nav">
          {user ? (
            <>
              <span style={{ color: "white", opacity: 0.8, fontSize: "0.875rem" }}>
                {user.username}
              </span>
              {isAdmin && (
                <>
                  <Link to="/" className="nav-link">
                    Пользователи
                  </Link>
                  <Link to="/users/new" className="nav-link">
                    Создать
                  </Link>
                </>
              )}
              <button className="btn btn-sm btn-outline" onClick={logout} style={{ color: "white", borderColor: "white" }}>
                Выйти
              </button>
            </>
          ) : (
            <Link to="/login" className="nav-link">
              Войти
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
