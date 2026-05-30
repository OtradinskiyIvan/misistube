import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await login(username.trim());
      if (user.roles.includes("admin")) {
        navigate("/", { replace: true });
      } else {
        navigate("/login", { replace: true });
        setError("Доступ разрешён только администраторам");
      }
    } catch (err) {
      setError(err.message || "Ошибка входа");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "60vh",
      }}
    >
      <div className="card" style={{ maxWidth: "420px", width: "100%", padding: "2rem" }}>
        <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>Вход</h2>

        <ErrorAlert message={error} onClose={() => setError("")} />

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label" htmlFor="username">
              Username или Email
            </label>
            <input
              id="username"
              className="input"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Введите ваш username или email"
            />
          </div>
          <button type="submit" className="btn btn-primary btn-lg" style={{ width: "100%" }} disabled={loading}>
            {loading ? "Вход..." : "Войти"}
          </button>
        </form>
      </div>
    </div>
  );
}
