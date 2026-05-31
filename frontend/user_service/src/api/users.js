const BASE = "/api/v1";

class ApiError extends Error {
  constructor(code, detail, status) {
    super(detail);
    this.code = code;
    this.detail = detail;
    this.status = status;
  }
}

function getToken() {
  const stored = localStorage.getItem("auth_user");
  if (!stored) return null;
  try {
    return JSON.parse(stored).token;
  } catch {
    return null;
  }
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 204) return null;

  const body = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new ApiError(
      body.error || "UNKNOWN",
      Array.isArray(body.detail) ? body.detail.map((d) => d.msg || String(d)).join("; ") : body.detail || res.statusText,
      res.status,
    );
  }

  return body;
}

export const api = {
  decodeToken: (token) =>
    request("/auth/decode", { method: "POST", body: JSON.stringify({ token }) }),

  syncUser: (token) =>
    request("/auth/sync", { method: "POST", body: JSON.stringify({ token }) }),

  listUsers: (skip = 0, limit = 100) =>
    request(`/users?skip=${skip}&limit=${limit}`),

  searchUsers: (username, skip = 0, limit = 100) =>
    request(`/users?skip=${skip}&limit=${limit}&username=${encodeURIComponent(username)}`),

  getUser: (id) => request(`/users/${id}`),

  createUser: (data) =>
    request("/users", { method: "POST", body: JSON.stringify(data) }),

  updateUser: (id, data) =>
    request(`/users/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  deleteUser: (id) =>
    request(`/users/${id}`, { method: "DELETE" }),
};

export { ApiError };
