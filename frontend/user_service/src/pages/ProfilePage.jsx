import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../api/users.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

function StatsCards({ userId }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.getUserStats(userId).then(setStats).catch(() => {});
  }, [userId]);

  const cards = [
    { label: "Подписчиков", value: stats?.total_subscribers ?? "—" },
    { label: "Просмотров", value: stats?.total_views ?? "—" },
    { label: "Лайков", value: stats?.total_likes_received ?? "—" },
    { label: "Комментариев", value: stats?.total_comments_received ?? "—" },
  ];

  return (
    <div className="stats-grid">
      {cards.map((c) => (
        <div key={c.label} className="card stats-card">
          <div className="stats-card-value">{c.value}</div>
          <div className="stats-card-label">{c.label}</div>
        </div>
      ))}
    </div>
  );
}

function InfoTab({ user, isAdmin, isOwner, logout }) {
  const [profile, setProfile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editBio, setEditBio] = useState("");
  const [editLocation, setEditLocation] = useState("");
  const fileRef = useRef(null);

  const loadProfile = () => {
    api.getProfile(user.id).then(setProfile).catch(() => {});
  };

  useEffect(() => {
    loadProfile();
  }, [user.id]);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await api.uploadAvatar(user.id, file);
      setProfile((p) => ({ ...p, avatar_url: res.avatar_url }));
    } catch (err) {
      alert(err.detail || "Ошибка загрузки");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleDeleteAvatar = async () => {
    if (!confirm("Удалить аватар?")) return;
    try {
      await api.deleteAvatar(user.id);
      setProfile((p) => ({ ...p, avatar_url: null }));
    } catch (err) {
      alert(err.detail || "Ошибка удаления");
    }
  };

  const startEdit = () => {
    setEditBio(profile?.bio || "");
    setEditLocation(profile?.location || "");
    setEditing(true);
  };

  const cancelEdit = () => {
    setEditing(false);
  };

  const saveProfile = async () => {
    try {
      const res = await api.updateProfile(user.id, {
        bio: editBio || null,
        location: editLocation || null,
      });
      setProfile(res);
      setEditing(false);
    } catch (err) {
      alert(err.detail || "Ошибка сохранения");
    }
  };

  const goToUpload = () => {
    window.location.href = '/creation/upload';
  };

  return (
    <>
      <StatsCards userId={user.id} />
      <div className="card" style={{ padding: "1.5rem", marginTop: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
          <div style={{ position: "relative", width: 80, height: 80, borderRadius: "50%", overflow: "hidden", background: "var(--misis-gray-200)", flexShrink: 0 }}>
            {profile?.avatar_url ? (
              <img src={profile.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "2rem", fontWeight: 600, color: "var(--misis-text-dark)" }}>
                {user.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div>
            <h3 style={{ margin: 0 }}>{user.username}</h3>
            <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem" }}>
              <button className="btn btn-sm btn-primary" onClick={() => fileRef.current?.click()} disabled={uploading}>
                {uploading ? "Загрузка…" : "Загрузить"}
              </button>
              {profile?.avatar_url && (
                <button className="btn btn-sm btn-outline" onClick={handleDeleteAvatar}>
                  Удалить
                </button>
              )}
            </div>
            <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/gif,image/webp" style={{ display: "none" }} onChange={handleFileChange} />
          </div>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <h4 style={{ margin: 0 }}>О себе</h4>
            {!editing && (
              <button className="btn btn-sm btn-outline" onClick={startEdit}>
                Редактировать
              </button>
            )}
          </div>
          {editing ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <textarea
                className="input"
                rows={3}
                placeholder="Расскажите о себе…"
                value={editBio}
                onChange={(e) => setEditBio(e.target.value)}
                style={{ resize: "vertical" }}
              />
              <input
                className="input"
                placeholder="Город / страна"
                value={editLocation}
                onChange={(e) => setEditLocation(e.target.value)}
              />
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button className="btn btn-primary btn-sm" onClick={saveProfile}>
                  Сохранить
                </button>
                <button className="btn btn-secondary btn-sm" onClick={cancelEdit}>
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p style={{ margin: "0 0 0.25rem", opacity: profile?.bio ? 1 : 0.4 }}>
                {profile?.bio || "Bio не указано"}
              </p>
              <p style={{ margin: 0, opacity: profile?.location ? 1 : 0.4, fontSize: "0.9rem" }}>
                {profile?.location ? `📍 ${profile.location}` : "Локация не указана"}
              </p>
            </div>
          )}
        </div>

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
        <div style={{ marginTop: "1.5rem", display: "flex", gap: "0.5rem" }}>
          <button className="btn btn-primary" onClick={goToUpload}>
            Загрузить видео
          </button>
          <button className="btn btn-secondary" onClick={logout}>
            Выйти
          </button>
        </div>
      </div>
    </>
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
            href="/auth/"
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
