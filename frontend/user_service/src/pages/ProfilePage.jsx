import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../api/users.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

function InfoTab({ user, isAdmin, isOwner, logout }) {
  return (
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
  );
}

function SubscriptionsTab({ userId }) {
  const [following, setFollowing] = useState([]);
  const [followers, setFollowers] = useState([]);
  const [userMap, setUserMap] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [followingRes, followersRes] = await Promise.all([
          api.getFollowing(userId),
          api.getFollowers(userId),
        ]);
        const f = Array.isArray(followingRes) ? followingRes : [];
        const fs = Array.isArray(followersRes) ? followersRes : [];
        setFollowing(f);
        setFollowers(fs);

        const ids = new Set();
        f.forEach((s) => ids.add(s.following_id));
        fs.forEach((s) => ids.add(s.follower_id));
        if (ids.size > 0) {
          const briefs = await api.getUsersBatch(Array.from(ids));
          const map = {};
          briefs.forEach((u) => { map[u.id] = u; });
          setUserMap(map);
        }
      } catch {
        setFollowing([]);
        setFollowers([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userId]);

  if (loading) return <LoadingSpinner />;

  const UserLink = ({ id }) => {
    const u = userMap[id];
    return (
      <Link to={`/users/${id}`} style={{ textDecoration: "none", color: "inherit" }}>
        {u ? u.username : id.slice(0, 8) + "…"}
      </Link>
    );
  };

  return (
    <div className="card" style={{ padding: "1.5rem" }}>
      <h3 style={{ marginBottom: "1rem" }}>Подписки ({following.length})</h3>
      {following.length === 0 ? (
        <p style={{ opacity: 0.6 }}>Нет подписок</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {following.map((s) => (
            <li key={s.id} style={{ padding: "0.5rem 0", borderBottom: "1px solid var(--misis-gray-200)" }}>
              <UserLink id={s.following_id} />
            </li>
          ))}
        </ul>
      )}

      <h3 style={{ margin: "1.5rem 0 1rem" }}>Подписчики ({followers.length})</h3>
      {followers.length === 0 ? (
        <p style={{ opacity: 0.6 }}>Нет подписчиков</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {followers.map((s) => (
            <li key={s.id} style={{ padding: "0.5rem 0", borderBottom: "1px solid var(--misis-gray-200)" }}>
              <UserLink id={s.follower_id} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function LikesTab({ userId }) {
  const [videoIds, setVideoIds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.getLikedVideos(userId);
        setVideoIds(res.video_ids || []);
      } catch {
        setVideoIds([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userId]);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="card" style={{ padding: "1.5rem" }}>
      <h3 style={{ marginBottom: "1rem" }}>Понравившиеся видео ({videoIds.length})</h3>
      {videoIds.length === 0 ? (
        <p style={{ opacity: 0.6 }}>Нет лайкнутых видео</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {videoIds.map((vid) => (
            <li key={vid} style={{ padding: "0.5rem 0", borderBottom: "1px solid var(--misis-gray-200)" }}>
              video_id: {vid}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function ProfilePage() {
  const { user, isAdmin, isOwner, logout, authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState("info");

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
            href="http://localhost:5174"
            className="btn btn-primary btn-lg"
            style={{ display: "block", textAlign: "center" }}
          >
            Войти
          </a>
        </div>
      </div>
    );
  }

  const tabs = [
    { key: "info", label: "Информация" },
    { key: "subscriptions", label: "Подписки" },
    { key: "likes", label: "Лайки" },
  ];

  return (
    <div className="fade-in" style={{ maxWidth: "640px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Личный кабинет</h1>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`btn btn-sm ${activeTab === tab.key ? "btn-primary" : "btn-outline"}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "info" && <InfoTab user={user} isAdmin={isAdmin} isOwner={isOwner} logout={logout} />}
      {activeTab === "subscriptions" && <SubscriptionsTab userId={user.id} />}
      {activeTab === "likes" && <LikesTab userId={user.id} />}
    </div>
  );
}
