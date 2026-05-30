import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/users.js";
import UserForm from "../components/UserForm.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";

export default function UserCreatePage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data) => {
    if (!data.password) {
      setError("Пароль обязателен");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const user = await api.createUser(data);
      navigate(`/users/${user.id}`, { replace: true });
    } catch (err) {
      setError(err.detail || err.message || "Ошибка создания");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in" style={{ maxWidth: "560px" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Создать пользователя</h1>

      <ErrorAlert message={error} onClose={() => setError("")} />

      <UserForm onSubmit={handleSubmit} submitLabel="Создать" loading={loading} />
    </div>
  );
}
