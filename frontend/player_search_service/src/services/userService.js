import { apiClient } from '../api/client'

export const userService = {
  async getUserById(userId) {
    try {
      const data = await apiClient.getUser(userId)
      return {
        id: data.id,
        username: data.username,
        email: data.email,
        status: data.status,
        channelUrl: `${window.location.origin}/user/users/${data.id}`,
      }
    } catch (error) {
      console.error('Error fetching user:', error)
      return null
    }
  },
}
