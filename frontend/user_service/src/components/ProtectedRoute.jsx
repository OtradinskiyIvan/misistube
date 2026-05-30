import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function ProtectedRoute() {
  const { user, isAdmin } = useAuth();

  if (!user) return <Navigate to="/login" replace />;
  if (!isAdmin) {
    return (
      <div className="container" style={{ textAlign: "center", marginTop: "4rem" }}>
        <h1>403 — Доступ запрещён</h1>
        <p style={{ marginTop: "1rem" }}>Только администраторы могут управлять пользователями.</p>
      </div>
    );
  }

  return <Outlet />;
}
