import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../api/users.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

export default function SearchPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [input, setInput] = useState(query);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [followStatus, setFollowStatus] = useState({});

  useEffect(() => {
    setInput(query);
    if (!query) {
      setResults([]);
      return;
    }

    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.searchUsers(query);
        if (!cancelled) setResults(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setError(err.detail || "Ошибка поиска");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const q = input.trim();
    if (q) setSearchParams({ q });
  };

  const handleFollow = async (followingId) => {
    if (!user) return;
    try {
      await api.follow(user.id, followingId);
      setFollowStatus((prev) => ({ ...prev, [followingId]: true }));
    } catch (err) {
      alert(err.detail || "Ошибка подписки");
    }
  };

  const handleUnfollow = async (followingId) => {
    if (!user) return;
    try {
      await api.unfollow(user.id, followingId);
      setFollowStatus((prev) => ({ ...prev, [followingId]: false }));
    } catch (err) {
      alert(err.detail || "Ошибка отписки");
    }
  };

  useEffect(() => {
    if (!user || !user.id || results.length === 0) {
      if (user && !user.id) console.warn("SearchPage: user exists but user.id is undefined", user);
      return;
    }
    (async () => {
      const statuses = {};
      await Promise.all(
        results
          .filter((r) => r.id !== user.id)
          .map(async (r) => {
            try {
              const res = await api.isFollowing(user.id, r.id);
              statuses[r.id] = res.is_following;
            } catch { /* ignore */ }
          }),
      );
      setFollowStatus(statuses);
    })();
  }, [user, results]);

  if (!user) {
    return (
      <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto", textAlign: "center" }}>
        <div className="card" style={{ padding: "2rem" }}>
          <h2>Авторизация</h2>
          <p style={{ opacity: 0.7 }}>Войдите для поиска пользователей</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ maxWidth: "640px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Поиск пользователей</h1>

      <form className="search-form" onSubmit={handleSubmit}>
        <input
          className="input"
          type="text"
          placeholder="Введите username или UUID..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ flex: 1 }}
        />
        <button className="btn btn-primary" type="submit" disabled={!input.trim()}>
          Найти
        </button>
      </form>

      {loading && (
        <div style={{ textAlign: "center", paddingTop: "2rem" }}>
          <LoadingSpinner />
        </div>
      )}

      {error && (
        <div className="card" style={{ padding: "1rem", marginBottom: "1rem", borderLeft: "3px solid #EF4444" }}>
          <p style={{ color: "#EF4444" }}>{error}</p>
        </div>
      )}

      {!loading && query && results.length === 0 && !error && (
        <p style={{ opacity: 0.6, textAlign: "center", paddingTop: "2rem" }}>
          Ничего не найдено по запросу «{query}»
        </p>
      )}

      {results.length > 0 && (
        <div className="card" style={{ padding: "1rem" }}>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {results.map((u) => (
              <li
                key={u.id}
                style={{
                  display: "flex", alignItems: "center", gap: "0.75rem",
                  padding: "0.75rem 0.5rem", borderBottom: "1px solid var(--misis-gray-200)",
                }}
              >
                <div
                  style={{
                    width: 40, height: 40, borderRadius: "50%", overflow: "hidden",
                    background: "var(--misis-gray-200)", flexShrink: 0,
                  }}
                >
                  {u.avatar_url ? (
                    <img src={u.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    <div
                      style={{
                        width: "100%", height: "100%", display: "flex", alignItems: "center",
                        justifyContent: "center", fontSize: "1rem", fontWeight: 600, color: "var(--misis-text-dark)",
                      }}
                    >
                      {u.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <Link
                    to={`/users/${u.id}`}
                    style={{ fontWeight: 600, textDecoration: "none", color: "inherit" }}
                  >
                    {u.username}
                  </Link>
                  <div style={{ fontSize: "0.8rem", opacity: 0.5, fontFamily: "monospace" }}>
                    {u.id.slice(0, 8)}…
                  </div>
                </div>
                {u.id !== user.id && (
                  followStatus[u.id] ? (
                    <button className="btn btn-sm btn-outline" onClick={() => handleUnfollow(u.id)}>
                      Отписаться
                    </button>
                  ) : (
                    <button className="btn btn-sm btn-primary" onClick={() => handleFollow(u.id)}>
                      Подписаться
                    </button>
                  )
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
