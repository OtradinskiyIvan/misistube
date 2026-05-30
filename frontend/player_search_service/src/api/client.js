const API_BASE_URL = '/api/v1';

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

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Search endpoints
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

  // Playback endpoint
  async getPlaybackUrl(videoId) {
    return this.request(`/playback/${videoId}`);
  }

  // Health check
  async healthCheck() {
    return this.request('/health', { baseURL: '' });
  }
}

export const apiClient = new ApiClient();
export default apiClient;