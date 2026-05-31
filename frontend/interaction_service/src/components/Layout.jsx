import { Outlet, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Layout() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <>
      <header className="header">
        <div className="container">
          <Link to="/" className="logo">MISIS Tube — Interactions</Link>
          <nav className="nav">
            <Link to="/video/1" className="nav-link">Video #1</Link>
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
