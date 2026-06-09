function getToken() {
  const stored = localStorage.getItem('auth_user');
  if (!stored) return null;
  try { return JSON.parse(stored).token } catch { return null }
}

function setToken(token) {
  const stored = localStorage.getItem('auth_user');
  if (!stored) return;
  try {
    const data = JSON.parse(stored);
    data.token = token;
    localStorage.setItem('auth_user', JSON.stringify(data));
  } catch {}
}

function getRefreshToken() {
  return localStorage.getItem('auth_refresh') || null;
}

async function refreshAccessToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;
  try {
    const res = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    const newToken = data.access_token;
    if (newToken) {
      setToken(newToken);
      return newToken;
    }
    return null;
  } catch {
    return null;
  }
}

async function authedFetch(url, options = {}) {
  let token = getToken();
  const headers = { ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res = await fetch(url, { ...options, headers });

  if (res.status === 401 && getRefreshToken()) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      res = await fetch(url, { ...options, headers });
    }
  }

  return res;
}

async function throwIfError(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const likeService = {
  likeVideo: async (videoId) => {
    const res = await authedFetch('/api/v1/likes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: videoId }),
    });
    return throwIfError(res);
  },

  unlikeVideo: async (videoId) => {
    const res = await authedFetch(`/api/v1/likes/video/${videoId}`, {
      method: 'DELETE',
    });
    return throwIfError(res);
  },

  isLiked: async (videoId) => {
    const token = getToken();
    if (!token) return { liked: false };
    const res = await fetch(`/api/v1/likes/video/${videoId}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    return throwIfError(res);
  },

  likesCount: async (videoId) => {
    const res = await fetch(`/api/v1/likes/video/${videoId}/count`);
    return throwIfError(res);
  },
};
