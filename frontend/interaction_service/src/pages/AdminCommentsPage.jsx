import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../api/interactions.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

export default function AdminCommentsPage() {
  const { user, isAdmin, canModerate } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 200;

  const loadComments = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getAllComments(skip, limit);
      setComments(data.comments || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [skip]);

  useEffect(() => {
    if (canModerate) loadComments();
  }, [canModerate, loadComments]);

  if (!user || !canModerate) {
    return (
      <div className="fade-in" style={{ maxWidth: "420px", margin: "0 auto", textAlign: "center" }}>
        <div className="card" style={{ padding: "2rem" }}>
          <h2>Доступ запрещён</h2>
          <p style={{ opacity: 0.7 }}>Требуются права модератора или администратора</p>
        </div>
      </div>
    );
  }

  const handleBlock = async (commentId) => {
    try {
      await api.blockComment(commentId);
      await loadComments();
    } catch (err) {
      alert(err.detail || "Failed to block comment");
    }
  };

  const handleUnblock = async (commentId) => {
    try {
      await api.unblockComment(commentId);
      await loadComments();
    } catch (err) {
      alert(err.detail || "Failed to unblock comment");
    }
  };

  if (loading) {
    return (
      <div className="fade-in" style={{ textAlign: "center", paddingTop: "4rem" }}>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1>Модерация комментариев</h1>
        <button className="btn btn-primary" onClick={loadComments}>
          Обновить
        </button>
      </div>

      <div className="card" style={{ padding: "1.5rem", overflowX: "auto" }}>
        {comments.length === 0 ? (
          <p style={{ opacity: 0.6, textAlign: "center" }}>Нет комментариев</p>
        ) : (
          <table className="user-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Video ID</th>
                <th>Комментарий</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {comments.map((c) => (
                <tr key={c.id}>
                  <td>
                    <small style={{ opacity: 0.7 }}>{c.user_id.slice(0, 8)}…</small>
                  </td>
                  <td>
                    <small style={{ opacity: 0.7 }}>{c.video_id.slice(0, 8)}…</small>
                  </td>
                  <td>
                    <div style={{ maxWidth: "300px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {c.content}
                    </div>
                  </td>
                  <td>
                    <span
                      className={`badge ${c.is_blocked ? "badge-danger" : "badge-success"}`}
                    >
                      {c.is_blocked ? "blocked" : "active"}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: "0.25rem" }}>
                      {canModerate && !c.is_blocked && (
                        <button
                          className="btn btn-sm btn-outline"
                          style={{ borderColor: "#EF4444", color: "#EF4444", fontSize: "0.75rem" }}
                          onClick={() => handleBlock(c.id)}
                        >
                          Заблокировать
                        </button>
                      )}
                      {canModerate && c.is_blocked && (
                        <button
                          className="btn btn-sm btn-outline"
                          style={{ borderColor: "#10B981", color: "#10B981", fontSize: "0.75rem" }}
                          onClick={() => handleUnblock(c.id)}
                        >
                          Разблокировать
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {total > limit && (
        <div className="pagination mt-4">
          <button
            className="btn btn-sm btn-secondary"
            disabled={skip === 0}
            onClick={() => setSkip((s) => Math.max(0, s - limit))}
          >
            Previous
          </button>
          <span className="pagination__info">
            {skip + 1}–{Math.min(skip + limit, total)} of {total}
          </span>
          <button
            className="btn btn-sm btn-secondary"
            disabled={skip + limit >= total}
            onClick={() => setSkip((s) => s + limit)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
