import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api/users.js";
import StatusBadge from "../components/StatusBadge.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";

export default function UserDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showDelete, setShowDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError("");
    api
      .getUser(id)
      .then(setUser)
      .catch((err) => setError(err.detail || err.message || "Пользователь не найден"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.deleteUser(id);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.detail || err.message || "Ошибка удаления");
      setShowDelete(false);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <LoadingSpinner text="Загрузка пользователя..." />;

  if (error && !user) {
    return (
      <div className="fade-in">
        <ErrorAlert message={error} onClose={() => setError("")} />
        <Link to="/" className="btn btn-secondary">← Назад к списку</Link>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ maxWidth: "640px" }}>
      <Link to="/" className="btn btn-sm btn-secondary" style={{ marginBottom: "1rem" }}>
        ← Назад
      </Link>

      <ErrorAlert message={error} onClose={() => setError("")} />

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
            <span className="detail-label">Статус</span>
            <span className="detail-value"><StatusBadge status={user.status} /></span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Роли</span>
            <span className="detail-value">{(user.roles || []).join(", ") || "—"}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Создан</span>
            <span className="detail-value">
              {new Date(user.created_at).toLocaleString("ru-RU")}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Обновлён</span>
            <span className="detail-value">
              {new Date(user.updated_at).toLocaleString("ru-RU")}
            </span>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
          <Link to={`/users/${user.id}/edit`} className="btn btn-primary">
            Редактировать
          </Link>
          <button className="btn btn-outline" style={{ borderColor: "#EF4444", color: "#EF4444" }} onClick={() => setShowDelete(true)}>
            Удалить
          </button>
        </div>
      </div>

      {showDelete && (
        <ConfirmDialog
          title="Удалить пользователя"
          message={`Вы уверены, что хотите удалить ${user.username}?`}
          onConfirm={handleDelete}
          onCancel={() => setShowDelete(false)}
          loading={deleting}
        />
      )}
    </div>
  );
}
