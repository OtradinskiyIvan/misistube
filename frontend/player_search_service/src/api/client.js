const API_BASE_URL = '/api/v1';

function getToken() {
  const stored = localStorage.getItem('auth_user');
  if (!stored) return null;
  try { return JSON.parse(stored).token } catch { return null }
}

function getRefreshToken() {
  return localStorage.getItem('auth_refresh') || null;
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

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      if (response.status === 204) return null;
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async authedRequest(endpoint, options = {}) {
    let token = getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let res = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

    if (res.status === 401 && getRefreshToken()) {
      const newToken = await this.refreshToken(getRefreshToken());
      if (newToken) {
        headers['Authorization'] = `Bearer ${newToken}`;
        res = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
      }
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${res.status}`);
    }

    if (res.status === 204) return null;
    return res.json();
  }

  async searchVideos(query, offset = 0, limit = 20, tags = []) {
    const params = new URLSearchParams({
      q: query,
      offset: offset.toString(),
      limit: limit.toString(),
    });

    if (tags.length > 0) {
      tags.forEach(tag => params.append('tags', tag));
    }

    return this.request(`/search?${params}`);
  }

  async getPlaybackUrl(videoId) {
    return this.request(`/playback/${videoId}`);
  }

  async getVideoDetails(videoId) {
    return this.request(`/videos/${videoId}/details`);
  }

  async getComments(videoId, skip = 0, limit = 50) {
    return this.request(`/comments/video/${videoId}?skip=${skip}&limit=${limit}`);
  }

  async createComment(videoId, content, parentId = null) {
    return this.authedRequest('/comments', {
      method: 'POST',
      body: JSON.stringify({ video_id: videoId, content, parent_id: parentId }),
    });
  }

  async getUser(userId) {
    return this.request(`/users/${userId}`);
  }

  async toggleLike(data) {
    return this.authedRequest('/likes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async unlikeVideo(videoId) {
    return this.authedRequest(`/likes/video/${videoId}`, {
      method: 'DELETE',
    });
  }

  async getUserLike(videoId) {
    const token = getToken();
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    return this.request(`/likes/video/${videoId}`, { headers });
  }

  async getLikeCount(videoId) {
    return this.request(`/likes/video/${videoId}/count`);
  }

  async recordView(videoId) {
    return this.authedRequest('/views', {
      method: 'POST',
      body: JSON.stringify({ video_id: videoId }),
    });
  }

  async refreshToken(refreshToken) {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    if (data.access_token) {
      setToken(data.access_token);
      return data.access_token;
    }
    return null;
  }

  async healthCheck() {
    return this.request('/health', { baseURL: '' });
  }
}

export const apiClient = new ApiClient();
export default apiClient;
