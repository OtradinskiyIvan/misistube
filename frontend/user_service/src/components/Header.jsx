import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Header() {
  const { user, isAdmin, logout } = useAuth();

  return (
    <header className="header">
      <div className="container">
        <span className="logo">MISIS Tube</span>
        <nav className="nav">
          {user && (
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
                className="btn btn-sm btn-outline"
                onClick={logout}
                style={{ color: "white", borderColor: "white" }}
              >
                Выйти
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
