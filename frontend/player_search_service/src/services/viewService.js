export const viewService = {
  recordView: async (videoId) => {
    const stored = localStorage.getItem('auth_user');
    const token = stored ? (() => { try { return JSON.parse(stored).token } catch { return null } })() : null;
    if (!token) return;

    await fetch('/api/v1/views', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ video_id: videoId }),
    });
  },
};