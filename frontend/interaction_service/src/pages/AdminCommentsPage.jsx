import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../api/interactions.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

export default function AdminCommentsPage() {
  const { user, isAdmin } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("blocked");
  const [videoId, setVideoId] = useState("");

  const loadBlocked = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getBlockedComments(0, 200);
      setComments(data.comments || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAdmin) loadBlocked();
  }, [isAdmin, loadBlocked]);

  if (!user || !isAdmin) {
    return (
      <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto", textAlign: "center" }}>
        <div className="card" style={{ padding: "2rem" }}>
          <h2>Доступ запрещён</h2>
          <p style={{ opacity: 0.7 }}>Требуются права администратора</p>
        </div>
      </div>
    );
  }

  const handleUnblock = async (commentId) => {
    try {
      await api.unblockComment(commentId);
      await loadBlocked();
    } catch (err) {
      alert(err.detail || "Failed to unblock comment");
    }
  };

  const handleDelete = async (commentId) => {
    if (!window.confirm("Удалить комментарий?")) return;
    try {
      await api.deleteCommentAsAdmin(commentId);
      await loadBlocked();
    } catch (err) {
      alert(err.detail || "Failed to delete comment");
    }
  };

  return (
    <div className="fade-in">
      <h1 style={{ marginBottom: "1.5rem" }}>Модерация комментариев</h1>

      <div style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem" }}>
        <button
          className={`btn btn-sm ${tab === "blocked" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("blocked"); loadBlocked(); }}
        >
          Заблокированные
        </button>
        <button
          className="btn btn-sm btn-outline"
          onClick={loadBlocked}
        >
          Обновить
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", paddingTop: "2rem" }}>
          <LoadingSpinner />
        </div>
      ) : (
        <div className="card" style={{ padding: "1.5rem" }}>
          {comments.length === 0 ? (
            <p style={{ opacity: 0.6, textAlign: "center" }}>Нет заблокированных комментариев</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {comments.map((c) => (
                <div
                  key={c.id}
                  className="card"
                  style={{
                    padding: "1rem",
                    borderLeft: "3px solid #EF4444",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: "1rem",
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", gap: "0.75rem", marginBottom: "0.5rem", fontSize: "0.875rem", opacity: 0.7 }}>
                      <span>user: {c.user_id.slice(0, 8)}…</span>
                      <span>video: {c.video_id.slice(0, 8)}…</span>
                      <span>id: {c.id.slice(0, 8)}…</span>
                    </div>
                    <p style={{ wordBreak: "break-word" }}>{c.content}</p>
                    {c.blocked_at && (
                      <small style={{ opacity: 0.5 }}>
                        Заблокирован: {new Date(c.blocked_at).toLocaleString("ru-RU")}
                      </small>
                    )}
                  </div>
                  <div style={{ display: "flex", gap: "0.25rem", flexShrink: 0 }}>
                    <button
                      className="btn btn-sm"
                      style={{ background: "#10B981", color: "white", border: "none" }}
                      onClick={() => handleUnblock(c.id)}
                    >
                      Разблокировать
                    </button>
                    <button
                      className="btn btn-sm"
                      style={{ background: "#EF4444", color: "white", border: "none" }}
                      onClick={() => handleDelete(c.id)}
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
