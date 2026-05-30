import { useState, useEffect, useCallback } from "react";
import { api } from "../api/users.js";
import UserTable from "../components/UserTable.jsx";
import Pagination from "../components/Pagination.jsx";
import ErrorAlert from "../components/ErrorAlert.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";

const LIMIT = 20;

export default function UserListPage() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.listUsers(skip, LIMIT);
      let list = data.users || [];
      setTotal(data.total || list.length);

      if (search.trim()) {
        const q = search.trim().toLowerCase();
        list = list.filter((u) => u.username.toLowerCase().includes(q));
      }

      setUsers(list);
    } catch (err) {
      setError(err.detail || err.message || "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, [skip, search]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSearch = (e) => {
    e.preventDefault();
    setSkip(0);
    fetchUsers();
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await api.deleteUser(deleteTarget.id);
      setDeleteTarget(null);
      fetchUsers();
    } catch (err) {
      setError(err.detail || err.message || "Ошибка удаления");
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1>Пользователи</h1>
      </div>

      <ErrorAlert message={error} onClose={() => setError("")} />

      <form onSubmit={handleSearch} className="search-form">
        <input
          className="input"
          type="text"
          placeholder="Поиск по username..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ maxWidth: "320px" }}
        />
        <button type="submit" className="btn btn-primary btn-sm">
          Найти
        </button>
        {search && (
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={() => {
              setSearch("");
              setSkip(0);
            }}
          >
            Сбросить
          </button>
        )}
      </form>

      <Pagination skip={skip} limit={LIMIT} total={total} onSkipChange={setSkip} />

      {loading ? (
        <LoadingSpinner text="Загрузка пользователей..." />
      ) : (
        <UserTable users={users} onDelete={setDeleteTarget} />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Удалить пользователя"
          message={`Вы уверены, что хотите удалить ${deleteTarget.username}?`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          loading={deleting}
        />
      )}
    </div>
  );
}
