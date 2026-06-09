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
      body.detail || res.statusText,
      res.status,
    );
  }

  return body;
}

export const api = {
  likeVideo: (videoId) =>
    request("/likes", { method: "POST", body: JSON.stringify({ video_id: videoId }) }),

  unlikeVideo: (videoId) =>
    request(`/likes/video/${videoId}`, { method: "DELETE" }),

  isLiked: (videoId) =>
    request(`/likes/video/${videoId}`),

  likesCount: (videoId) =>
    request(`/likes/video/${videoId}/count`),

  createComment: (videoId, content, parentId = null) =>
    request("/comments", {
      method: "POST",
      body: JSON.stringify({ video_id: videoId, content, parent_id: parentId }),
    }),

  getComments: (videoId, skip = 0, limit = 50) =>
    request(`/comments/video/${videoId}?skip=${skip}&limit=${limit}`),

  updateComment: (commentId, content) =>
    request(`/comments/${commentId}`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    }),

  deleteComment: (commentId) =>
    request(`/comments/${commentId}`, { method: "DELETE" }),

  blockComment: (commentId) =>
    request(`/admin/comments/${commentId}/block`, { method: "POST" }),

  unblockComment: (commentId) =>
    request(`/admin/comments/${commentId}/unblock`, { method: "POST" }),

  deleteCommentAsAdmin: (commentId) =>
    request(`/admin/comments/${commentId}`, { method: "DELETE" }),

  getAllComments: (skip = 0, limit = 200) =>
    request(`/admin/comments?skip=${skip}&limit=${limit}`),

  getBlockedComments: (skip = 0, limit = 50) =>
    request(`/admin/comments/blocked?skip=${skip}&limit=${limit}`),

  follow: (userId) =>
    request(`/subscriptions/follow/${userId}`, { method: "POST" }),

  unfollow: (userId) =>
    request(`/subscriptions/follow/${userId}`, { method: "DELETE" }),

  isFollowing: (userId) =>
    request(`/subscriptions/is-following/${userId}`),
};

export { ApiError };
