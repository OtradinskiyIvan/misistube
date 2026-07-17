import { apiClient } from '../api/client'

export const likeService = {
  async likeVideo(videoId) {
    return apiClient.toggleLike({ video_id: videoId });
  },

  async unlikeVideo(videoId) {
    return apiClient.unlikeVideo(videoId);
  },

  async isLiked(videoId) {
    const stored = localStorage.getItem('auth_user');
    if (!stored) return { liked: false };
    return apiClient.getUserLike(videoId);
  },

  async likesCount(videoId) {
    return apiClient.getLikeCount(videoId);
  },
};
