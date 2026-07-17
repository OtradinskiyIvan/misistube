import { apiClient } from '../api/client'

export const commentsService = {
  async getVideoComments(videoId, skip = 0, limit = 50) {
    return apiClient.getComments(videoId, skip, limit);
  },

  async createComment(videoId, content, parentId = null) {
    return apiClient.createComment(videoId, content, parentId);
  },
};
