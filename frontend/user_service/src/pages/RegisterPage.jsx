import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";

const AUTH_API = "/api/v1/auth";

export default function RegisterPage() {
  const { loginWithToken } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState("register");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [confirmCode, setConfirmCode] = useState("");
  const [debugCode, setDebugCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Пароли не совпадают");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${AUTH_API}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      const body = await res.json();
      if (body.debug_code) {
        setDebugCode(body.debug_code);
      }
      if (!res.ok) {
        throw new Error(body.detail || "Ошибка регистрации");
      }

      setStep("confirm");
    } catch (err) {
      setError(err.message || "Не удалось зарегистрироваться");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${AUTH_API}/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code: confirmCode }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Неверный код подтверждения");
      }

      const loginRes = await fetch(`${AUTH_API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login: username, password }),
      });

      if (!loginRes.ok) {
        navigate("/auth/login");
        return;
      }

      const data = await loginRes.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      await loginWithToken(data.access_token);
      navigate("/profile", { replace: true });
    } catch (err) {
      setError(err.message || "Ошибка подтверждения");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto" }}>
      <div className="card" style={{ padding: "2rem" }}>
        <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          {step === "register" ? "Регистрация" : "Подтвердите email"}
        </h2>

        <ErrorAlert message={error} onClose={() => setError("")} />

        {step === "register" ? (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label className="label" htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                className="input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="ivan"
                minLength={3}
                required
              />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ivan@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="password">Пароль</label>
              <input
                id="password"
                type="password"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                minLength={8}
                required
              />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="confirmPassword">Подтвердите пароль</label>
              <input
                id="confirmPassword"
                type="password"
                className="input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                minLength={8}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              style={{ width: "100%", marginTop: "0.5rem" }}
              disabled={loading}
            >
              {loading ? "Регистрация..." : "Зарегистрироваться"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirm}>
            <p style={{ marginBottom: "1rem", opacity: 0.7 }}>
              На ваш email <strong>{email}</strong> отправлен 6-значный код
              подтверждения{debugCode ? "." : ""}
            </p>
            {debugCode && (
              <p style={{ marginBottom: "1rem", fontSize: "0.85rem", color: "#888" }}>
                (dev) Код из логов: <strong>{debugCode}</strong>
              </p>
            )}

            <div className="form-group">
              <label className="label" htmlFor="code">Код подтверждения</label>
              <input
                id="code"
                type="text"
                className="input"
                value={confirmCode}
                onChange={(e) => setConfirmCode(e.target.value)}
                placeholder="000000"
                minLength={6}
                maxLength={6}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              style={{ width: "100%", marginTop: "0.5rem" }}
              disabled={loading}
            >
              {loading ? "Подтверждение..." : "Подтвердить"}
            </button>
          </form>
        )}

        <p style={{ textAlign: "center", marginTop: "1rem" }}>
          {step === "register" ? (
            <>Уже есть аккаунт? <Link to="/auth/login">Войти</Link></>
          ) : (
            <button
              type="button"
              className="btn btn-sm btn-outline"
              onClick={() => setStep("register")}
            >
              Назад
            </button>
          )}
        </p>
      </div>
    </div>
  );
}
