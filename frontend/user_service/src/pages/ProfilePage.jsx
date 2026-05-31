import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";

export default function ProfilePage() {
  const { user, isAdmin, isOwner, loginWithToken, logout } = useAuth();
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await loginWithToken(token.trim());
    } catch (err) {
      setError(err.detail || err.message || "Ошибка входа");
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto" }}>
        <div className="card" style={{ padding: "2rem" }}>
          <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>
            MISIS Tube
          </h2>
          <p style={{ textAlign: "center", marginBottom: "1.5rem", opacity: 0.7 }}>
            Введите JWT токен для входа
          </p>

          <ErrorAlert message={error} onClose={() => setError("")} />

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="label" htmlFor="token">JWT токен</label>
              <textarea
                id="token"
                className="textarea"
                rows={3}
                required
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Вставьте JWT токен..."
                style={{ fontFamily: "monospace", fontSize: "0.8rem" }}
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-lg"
              style={{ width: "100%" }}
              disabled={loading}
            >
              {loading ? "Вход..." : "Войти"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ maxWidth: "640px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Личный кабинет</h1>

      <div className="card" style={{ padding: "1.5rem" }}>
        <div className="detail-grid">
          <div className="detail-row">
            <span className="detail-label">ID</span>
            <span className="detail-value">{user.id}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Username</span>
            <span className="detail-value">{user.username}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Email</span>
            <span className="detail-value">{user.email}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Роли</span>
            <span className="detail-value">
              {user.roles.length > 0 ? user.roles.join(", ") : "—"}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Права</span>
            <span className="detail-value">
              {isAdmin && "Администратор"}
              {isOwner && (isAdmin ? ", Владелец" : "Владелец")}
              {!isAdmin && !isOwner && "Обычный пользователь"}
            </span>
          </div>
        </div>

        <div style={{ marginTop: "1.5rem" }}>
          <button className="btn btn-secondary" onClick={logout}>
            Выйти
          </button>
        </div>
      </div>
    </div>
  );
}
