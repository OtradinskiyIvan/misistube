export const userService = {
  async getUserById(userId) {
    const url = `/api/v1/users/${userId}`
    console.log('Fetching user from:', url)
    
    try {
      const response = await fetch(url)
      console.log('Response status:', response.status)
      
      if (!response.ok) {
        if (response.status === 404) {
          console.warn('User not found:', userId)
          return null
        }
        throw new Error(`Failed to fetch user: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('User data received:', data)
      
      return {
        id: data.id,
        username: data.username,
        email: data.email,
        status: data.status,
        channelUrl: `/user/users/${data.id}`
      }
    } catch (error) {
      console.error('Error fetching user:', error)
      return null
    }
  }
}