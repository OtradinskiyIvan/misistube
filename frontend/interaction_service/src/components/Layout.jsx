import { Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Layout() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <>
      <header className="header">
        <div className="container">
          <span className="logo">MISIS Tube — Модерация</span>
          <nav className="nav">
            <a href="/user/profile" className="nav-link">Профиль</a>
            {isAuthenticated ? (
              <>
                <span className="nav-link">{user?.username}</span>
                <button className="btn btn-sm btn-outline" onClick={logout}>
                  Logout
                </button>
              </>
            ) : (
              <span className="nav-link">Not logged in</span>
            )}
          </nav>
        </div>
      </header>
      <main className="container" style={{ paddingTop: "2rem", paddingBottom: "2rem" }}>
        <Outlet />
      </main>
    </>
  );
}
