import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

export const uploadVideo = async (title, description, file) => {
  const formData = new FormData();
  formData.append('title', title);
  formData.append('description', description);
  formData.append('file', file);
  const response = await api.post('/videos/upload', formData, {});
  return response.data;
};

export const fetchVideos = async (limit = 10, offset = 0) => {
  const response = await api.get(`/videos/?limit=${limit}&offset=${offset}`);
  return response.data; // { items: [], total: number }
};

export const fetchVideoById = async (id) => {
  const response = await api.get(`/videos/${id}`);
  return response.data;
};