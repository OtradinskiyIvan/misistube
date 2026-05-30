import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api/users.js";
import UserForm from "../components/UserForm.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

export default function UserEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    api
      .getUser(id)
      .then(setUser)
      .catch((err) => setError(err.detail || err.message || "Пользователь не найден"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (data) => {
    setSaving(true);
    setError("");
    try {
      await api.updateUser(id, data);
      navigate(`/users/${id}`, { replace: true });
    } catch (err) {
      setError(err.detail || err.message || "Ошибка обновления");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner text="Загрузка..." />;

  if (error && !user) {
    return (
      <div className="fade-in">
        <ErrorAlert message={error} onClose={() => setError("")} />
        <Link to="/" className="btn btn-secondary">← Назад к списку</Link>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ maxWidth: "560px" }}>
      <Link to={`/users/${id}`} className="btn btn-sm btn-secondary" style={{ marginBottom: "1rem" }}>
        ← Назад
      </Link>

      <h1 style={{ marginBottom: "1.5rem" }}>Редактировать {user.username}</h1>

      <ErrorAlert message={error} onClose={() => setError("")} />

      <UserForm initialData={user} onSubmit={handleSubmit} submitLabel="Сохранить" loading={saving} />
    </div>
  );
}
