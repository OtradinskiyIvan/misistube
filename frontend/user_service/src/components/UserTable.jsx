import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge.jsx";

export default function UserTable({ users, onDelete }) {
  if (!users || users.length === 0) {
    return (
      <div className="card" style={{ padding: "2rem", textAlign: "center" }}>
        <p style={{ opacity: 0.6 }}>Пользователи не найдены</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Статус</th>
            <th>Дата создания</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td className="user-table__id">{user.id.slice(0, 8)}…</td>
              <td>
                <Link to={`/users/${user.id}`} className="user-table__link">
                  {user.username}
                </Link>
              </td>
              <td>{user.email}</td>
              <td><StatusBadge status={user.status} /></td>
              <td className="user-table__date">
                {new Date(user.created_at).toLocaleDateString("ru-RU")}
              </td>
              <td className="user-table__actions">
                <Link
                  to={`/users/${user.id}/edit`}
                  className="btn btn-sm btn-secondary"
                >
                  Редактировать
                </Link>
                <button
                  className="btn btn-sm btn-outline"
                  style={{ borderColor: "#EF4444", color: "#EF4444" }}
                  onClick={() => onDelete(user)}
                >
                  Удалить
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
