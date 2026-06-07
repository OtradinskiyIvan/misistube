import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";

const AUTH_API = "/api/v1/auth";

export default function LoginPage() {
  const { loginWithToken } = useAuth();
  const navigate = useNavigate();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${AUTH_API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login, password }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Ошибка входа");
      }

      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      await loginWithToken(data.access_token);
      navigate("/profile", { replace: true });
    } catch (err) {
      setError(err.message || "Не удалось выполнить вход");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto" }}>
      <div className="card" style={{ padding: "2rem" }}>
        <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          MISIS Tube
        </h2>
        <p style={{ textAlign: "center", marginBottom: "1.5rem", opacity: 0.7 }}>
          Войдите в свой аккаунт
        </p>

        <ErrorAlert message={error} onClose={() => setError("")} />

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label" htmlFor="login">
              Логин (username или email)
            </label>
            <input
              id="login"
              type="text"
              className="input"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder="ivan или ivan@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="password">
              Пароль
            </label>
            <input
              id="password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg"
            style={{ width: "100%", marginTop: "0.5rem" }}
            disabled={loading}
          >
            {loading ? "Вход..." : "Войти"}
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: "1rem" }}>
          Нет аккаунта?{" "}
          <Link to="/auth/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  );
}
