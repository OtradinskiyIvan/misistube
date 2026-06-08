function getToken() {
  const stored = localStorage.getItem('auth_user');
  if (!stored) return null;
  try { return JSON.parse(stored).token } catch { return null }
}

async function handleResponse(res) {
  console.log(`[commentsService] ${res.status} ${res.url}`);
  const text = await res.text();
  if (!text) return {};
  try { return JSON.parse(text) } catch { console.error('[commentsService] parse error:', text); return {} }
}

export const commentsService = {
  async getVideoComments(videoId, skip = 0, limit = 50) {
    const res = await fetch(`/api/v1/comments/video/${videoId}?skip=${skip}&limit=${limit}`);
    return handleResponse(res);
  },

  async createComment(videoId, content, parentId = null) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch('/api/v1/comments', {
      method: 'POST',
      headers,
      body: JSON.stringify({ video_id: videoId, content, parent_id: parentId }),
    });
    return handleResponse(res);
  },
};
