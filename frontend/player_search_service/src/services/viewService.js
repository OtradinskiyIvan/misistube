import { apiClient } from '../api/client'

export const viewService = {
  recordView: async (videoId) => {
    const stored = localStorage.getItem('auth_user');
    if (!stored) return;
    return apiClient.recordView(videoId);
  },
};
