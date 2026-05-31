import { useAuth } from "../context/AuthContext.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

export default function ProfilePage() {
  const { user, isAdmin, isOwner, logout, authLoading } = useAuth();

  if (authLoading) {
    return (
      <div className="fade-in" style={{ textAlign: "center", paddingTop: "4rem" }}>
        <LoadingSpinner />
        <p style={{ marginTop: "1rem", opacity: 0.7 }}>Выполняется вход...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto" }}>
        <div className="card" style={{ padding: "2rem" }}>
          <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>
            MISIS Tube
          </h2>
          <p style={{ textAlign: "center", marginBottom: "1.5rem", opacity: 0.7 }}>
            Для доступа к личному кабинету необходимо авторизоваться
          </p>
          <a
            href="/auth/login"
            className="btn btn-primary btn-lg"
            style={{ display: "block", textAlign: "center" }}
          >
            Войти
          </a>
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
