const BASE = "/api/v1";
const INTERACTION_BASE = "http://localhost:8002/api/v1";

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

  assignRole: (userId, role) =>
    request(`/users/${userId}/roles`, { method: "POST", body: JSON.stringify({ role }) }),

  revokeRole: (userId, role) =>
    request(`/users/${userId}/roles/${role}`, { method: "DELETE" }),

  updateUserStatus: (userId, status) =>
    request(`/users/${userId}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),

  follow: (followerId, followingId) =>
    request(`/users/${followerId}/follow/${followingId}`, { method: "POST" }),

  unfollow: (followerId, followingId) =>
    request(`/users/${followerId}/follow/${followingId}`, { method: "DELETE" }),

  getFollowing: (userId, skip = 0, limit = 100) =>
    request(`/users/${userId}/following?skip=${skip}&limit=${limit}`),

  getFollowers: (userId, skip = 0, limit = 100) =>
    request(`/users/${userId}/followers?skip=${skip}&limit=${limit}`),

  isFollowing: (followerId, followingId) =>
    request(`/users/${followerId}/is-following/${followingId}`),

  getLikedVideos: async (userId) => {
    const token = getToken();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${INTERACTION_BASE}/users/${userId}/liked-videos`, { headers });
    if (!res.ok) return { video_ids: [] };
    return res.json();
  },
};

export { ApiError };
