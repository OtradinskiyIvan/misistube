import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../api/users.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

export default function AdminPage() {
  const { user, isAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingUser, setEditingUser] = useState(null);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [roleUser, setRoleUser] = useState(null);
  const [newRole, setNewRole] = useState("admin");
  const [hideInactive, setHideInactive] = useState(true);

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.listUsers(0, 100);
      setUsers(data.users || []);
    } catch (err) {
      console.error("AdminPage error:", err);
      setError(err.detail || "Failed to load users");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAdmin) loadUsers();
  }, [isAdmin, loadUsers]);

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

  const handleStatusChange = async (targetUser, newStatus) => {
    try {
      await api.updateUser(targetUser.id, { status: newStatus });
      await loadUsers();
    } catch (err) {
      alert(err.detail || "Failed to update status");
    }
  };

  const handleAssignRole = async () => {
    if (!roleUser || !newRole) return;
    try {
      await api.assignRole(roleUser.id, newRole);
      setShowRoleModal(false);
      setRoleUser(null);
      setNewRole("admin");
      await loadUsers();
    } catch (err) {
      alert(err.detail || "Failed to assign role");
    }
  };

  const handleRevokeRole = async (targetUser, role) => {
    if (!window.confirm(`Отозвать роль "${role}" у пользователя ${targetUser.username}?`)) return;
    try {
      await api.revokeRole(targetUser.id, role);
      await loadUsers();
    } catch (err) {
      alert(err.detail || "Failed to revoke role");
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
        <h1>Управление пользователями</h1>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9rem", cursor: "pointer", userSelect: "none" }}>
            <input
              type="checkbox"
              checked={hideInactive}
              onChange={(e) => setHideInactive(e.target.checked)}
            />
            Скрыть не активных
          </label>
          <button className="btn btn-primary" onClick={loadUsers}>
            Обновить
          </button>
        </div>
      </div>

      {error && (
        <div className="card" style={{ padding: "1rem", marginBottom: "1rem", borderLeft: "3px solid #EF4444" }}>
          <p style={{ color: "#EF4444" }}>{error}</p>
        </div>
      )}

      {hideInactive && users.filter(u => u.status === "inactive").length > 0 && (
        <p style={{ marginBottom: "0.75rem", opacity: 0.6, fontSize: "0.85rem" }}>
          Скрыто {users.filter(u => u.status === "inactive").length} неактивных пользователей
        </p>
      )}

      <div className="card" style={{ padding: "1.5rem", overflowX: "auto" }}>
        <table className="user-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Статус</th>
              <th>Роли</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.filter(u => !hideInactive || u.status !== "inactive").map((u) => (
              <tr key={u.id}>
                <td>
                  <strong>{u.username}</strong>
                  <br />
                  <small style={{ opacity: 0.5, fontSize: "0.75rem" }}>{u.id.slice(0, 8)}…</small>
                </td>
                <td>{u.email}</td>
                <td>
                  <span
                    className={`badge ${
                      u.status === "active" ? "badge-success" :
                      u.status === "banned" ? "badge-danger" :
                      "badge-warning"
                    }`}
                  >
                    {u.status}
                  </span>
                </td>
                <td>
                  {(u.roles || []).length > 0
                    ? u.roles.map((r) => (
                        <span key={r} style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", marginRight: "0.5rem" }}>
                          <span className="badge badge-info">{r}</span>
                          {r !== "owner" && (
                            <button
                              className="btn btn-sm"
                              style={{ padding: "0 0.25rem", fontSize: "0.75rem", color: "#EF4444", background: "none", border: "none", cursor: "pointer" }}
                              onClick={() => handleRevokeRole(u, r)}
                              title="Отозвать роль"
                            >
                              ×
                            </button>
                          )}
                        </span>
                      ))
                    : "—"}
                  <button
                    className="btn btn-sm btn-primary"
                    style={{ padding: "0.15rem 0.5rem", fontSize: "0.75rem" }}
                    onClick={() => { setRoleUser(u); setShowRoleModal(true); }}
                  >
                    + роль
                  </button>
                </td>
                <td>
                  <div style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                    {u.status !== "banned" && (
                      <button
                        className="btn btn-sm btn-outline"
                        style={{ borderColor: "#EF4444", color: "#EF4444", fontSize: "0.75rem" }}
                        onClick={() => handleStatusChange(u, "banned")}
                      >
                        Забанить
                      </button>
                    )}
                    {u.status === "banned" && (
                      <button
                        className="btn btn-sm btn-outline"
                        style={{ borderColor: "#10B981", color: "#10B981", fontSize: "0.75rem" }}
                        onClick={() => handleStatusChange(u, "active")}
                      >
                        Разбанить
                      </button>
                    )}

                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showRoleModal && roleUser && (
        <div
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)",
            display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100,
          }}
          onClick={() => { setShowRoleModal(false); setRoleUser(null); }}
        >
          <div
            className="card"
            style={{ padding: "2rem", maxWidth: "400px", width: "100%" }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ marginBottom: "1rem" }}>Назначить роль</h3>
            <p style={{ marginBottom: "1rem", opacity: 0.7 }}>
              Пользователь: <strong>{roleUser.username}</strong>
            </p>
            <select
              className="input"
              value={newRole}
              onChange={(e) => setNewRole(e.target.value)}
              style={{ width: "100%", marginBottom: "1rem" }}
            >
              <option value="admin">admin</option>
              <option value="moderator">moderator</option>
            </select>
            <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
              <button
                className="btn btn-secondary"
                onClick={() => { setShowRoleModal(false); setRoleUser(null); }}
              >
                Отмена
              </button>
              <button className="btn btn-primary" onClick={handleAssignRole}>
                Назначить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
