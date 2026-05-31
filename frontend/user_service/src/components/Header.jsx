import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div className="container">
        <span className="logo">MISIS Tube</span>
        <nav className="nav">
          {user && (
            <button
              className="btn btn-sm btn-outline"
              onClick={logout}
              style={{ color: "white", borderColor: "white" }}
            >
              Выйти
            </button>
          )}
        </nav>
      </div>
    </header>
  );
}
