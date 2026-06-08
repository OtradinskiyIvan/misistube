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

async function handleResponse(res) {
  console.log(`[commentsService] ${res.status} ${res.url}`);
  const text = await res.text();
  if (!text) return {};
  try { return JSON.parse(text) } catch { console.error('[commentsService] parse error:', text); return {} }
}

async function authedFetch(url, options = {}) {
  let token = getToken();
  const headers = { ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res = await fetch(url, { ...options, headers });

  if (res.status === 401 && getRefreshToken()) {
    console.log('[commentsService] token expired, refreshing...');
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      res = await fetch(url, { ...options, headers });
    }
  }

  return res;
}

async function throwIfError(res) {
  const body = await handleResponse(res);
  if (!res.ok) {
    throw new Error(body?.detail || `HTTP ${res.status}`);
  }
  return body;
}

export const commentsService = {
  async getVideoComments(videoId, skip = 0, limit = 50) {
    const res = await fetch(`/api/v1/comments/video/${videoId}?skip=${skip}&limit=${limit}`);
    return handleResponse(res);
  },

  async createComment(videoId, content, parentId = null) {
    const res = await authedFetch('/api/v1/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: videoId, content, parent_id: parentId }),
    });
    return throwIfError(res);
  },
};
