import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../api/users.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export default function UserPage() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { user: me } = useAuth();
  const [target, setTarget] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFollowing, setIsFollowing] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);

      if (!UUID_RE.test(userId)) {
        try {
          const results = await api.searchUsers(userId, 0, 10);
          const found = Array.isArray(results) && results.find(
            (u) => u.id === userId || u.username.toLowerCase() === userId.toLowerCase(),
          );
          if (found && !cancelled) {
            navigate(`/users/${found.id}`, { replace: true });
            return;
          }
        } catch { /* fall through to error */ }
        if (!cancelled) {
          setError(`Пользователь «${userId}» не найден`);
          setLoading(false);
        }
        return;
      }

      try {
        const data = await api.getUserBrief(userId);
        if (!cancelled) setTarget(data);
        const p = await api.getProfile(userId).catch(() => null);
        if (!cancelled) setProfile(p);
      } catch (err) {
        if (!cancelled) setError(err.detail || "Пользователь не найден");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [userId, navigate]);

  useEffect(() => {
    if (!me || !target || target.id === me.id) {
      if (me && !me.id) console.warn("UserPage: me exists but me.id is undefined", me);
      return;
    }
    (async () => {
      try {
        const res = await api.isFollowing(me.id, target.id);
        setIsFollowing(res.is_following);
      } catch { /* ignore */ }
    })();
  }, [me, target]);

  const handleFollow = async () => {
    if (!me || !target) return;
    try {
      await api.follow(me.id, target.id);
      setIsFollowing(true);
    } catch (err) {
      alert(err.detail || "Ошибка подписки");
    }
  };

  const handleUnfollow = async () => {
    if (!me || !target) return;
    try {
      await api.unfollow(me.id, target.id);
      setIsFollowing(false);
    } catch (err) {
      alert(err.detail || "Ошибка отписки");
    }
  };

  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.getUserStats(userId).then(setStats).catch(() => {});
  }, [userId]);

  const statsCards = [
    { label: "Подписчиков", value: stats?.total_subscribers ?? "—" },
    { label: "Просмотров", value: stats?.total_views ?? "—" },
    { label: "Лайков", value: stats?.total_likes_received ?? "—" },
    { label: "Комментариев", value: stats?.total_comments_received ?? "—" },
  ];

  if (loading) {
    return (
      <div className="fade-in" style={{ textAlign: "center", paddingTop: "4rem" }}>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto", textAlign: "center" }}>
        <div className="card" style={{ padding: "2rem" }}>
          <h2>Ошибка</h2>
          <p style={{ opacity: 0.7 }}>{error}</p>
          <Link to="/profile" className="btn btn-primary" style={{ marginTop: "1rem", display: "inline-block" }}>
            На главную
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ maxWidth: "640px", margin: "0 auto" }}>
      <div className="card" style={{ padding: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
          <div
            style={{
              width: 64, height: 64, borderRadius: "50%", overflow: "hidden",
              background: "var(--misis-gray-200)", flexShrink: 0,
            }}
          >
            {target.avatar_url ? (
              <img src={target.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <div
                style={{
                  width: "100%", height: "100%", display: "flex", alignItems: "center",
                  justifyContent: "center", fontSize: "1.5rem", fontWeight: 600, color: "var(--misis-text-dark)",
                }}
              >
                {target.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ margin: 0 }}>{target.username}</h2>
            <p style={{ margin: "0.25rem 0 0", opacity: 0.5, fontFamily: "monospace", fontSize: "0.8rem" }}>
              {target.id}
            </p>
          </div>
          <span className={`badge ${target.status === "active" ? "badge-success" : "badge-warning"}`}>
            {target.status}
          </span>
        </div>

        {(profile?.bio || profile?.location) && (
          <div style={{ marginBottom: "1rem", padding: "0.75rem", background: "var(--misis-gray-100)", borderRadius: "var(--misis-radius-md)" }}>
            {profile?.bio && <p style={{ margin: "0 0 0.25rem" }}>{profile.bio}</p>}
            {profile?.location && <p style={{ margin: 0, fontSize: "0.9rem", opacity: 0.7 }}>📍 {profile.location}</p>}
          </div>
        )}

        <div className="stats-grid">
          {statsCards.map((c) => (
            <div key={c.label} className="card stats-card">
              <div className="stats-card-value">{c.value}</div>
              <div className="stats-card-label">{c.label}</div>
            </div>
          ))}
        </div>

        <div className="detail-grid" style={{ marginTop: "1rem" }}>
          <div className="detail-row">
            <span className="detail-label">ID</span>
            <span className="detail-value">{target.id}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Username</span>
            <span className="detail-value">{target.username}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Статус</span>
            <span className="detail-value">{target.status}</span>
          </div>
        </div>

        {me && target.id !== me.id && (
          <div style={{ marginTop: "1.5rem" }}>
            {isFollowing ? (
              <button className="btn btn-secondary" onClick={handleUnfollow} style={{ width: "100%" }}>
                Отписаться
              </button>
            ) : (
              <button className="btn btn-primary" onClick={handleFollow} style={{ width: "100%" }}>
                Подписаться
              </button>
            )}
          </div>
        )}

        {me && target.id === me.id && (
          <div style={{ marginTop: "1.5rem" }}>
            <Link to="/profile" className="btn btn-primary" style={{ display: "block", textAlign: "center" }}>
              Мой профиль
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
