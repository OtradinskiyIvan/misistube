import { useState, useEffect } from "react";

const STATUS_OPTIONS = ["active", "inactive", "banned", "suspended"];

export default function UserForm({ initialData, onSubmit, submitLabel = "Сохранить", loading }) {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    status: "active",
  });

  useEffect(() => {
    if (initialData) {
      setForm({
        username: initialData.username || "",
        email: initialData.email || "",
        password: "",
        status: initialData.status || "active",
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = { username: form.username, email: form.email, status: form.status };
    if (form.password.trim()) {
      payload.password = form.password;
    }
    onSubmit(payload);
  };

  const isEdit = !!initialData;

  return (
    <form onSubmit={handleSubmit} className="fade-in">
      <div className="form-group">
        <label className="label" htmlFor="username">
          Username
        </label>
        <input
          id="username"
          name="username"
          className="input"
          type="text"
          required
          value={form.username}
          onChange={handleChange}
          placeholder="Введите username"
        />
      </div>

      <div className="form-group">
        <label className="label" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          name="email"
          className="input"
          type="email"
          required
          value={form.email}
          onChange={handleChange}
          placeholder="user@example.com"
        />
      </div>

      <div className="form-group">
        <label className="label" htmlFor="password">
          {isEdit ? "Новый пароль (оставьте пустым, чтобы не менять)" : "Пароль"}
        </label>
        <input
          id="password"
          name="password"
          className="input"
          type="password"
          required={!isEdit}
          value={form.password}
          onChange={handleChange}
          placeholder={isEdit ? "Оставьте пустым без изменений" : "Минимум 8 символов"}
        />
      </div>

      <div className="form-group">
        <label className="label" htmlFor="status">
          Статус
        </label>
        <select
          id="status"
          name="status"
          className="input"
          value={form.status}
          onChange={handleChange}
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <p style={{ color: "var(--misis-light)", marginBottom: "0.75rem" }}>
          Сохранение...
        </p>
      )}

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {submitLabel}
        </button>
      </div>
    </form>
  );
}
