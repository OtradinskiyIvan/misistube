import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

export const getUserIdFromToken = () => {
  const token = localStorage.getItem('token');
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub || null;
  } catch {
    return null;
  }
};

export const uploadVideo = async (title, description, file) => {
  const formData = new FormData();
  formData.append('title', title);
  formData.append('description', description || '');
  formData.append('file', file);
  const response = await api.post('/videos/upload', formData);
  return response.data;
};

export const fetchVideos = async (limit = 10, offset = 0, signal) => {
  const response = await api.get(`/videos/?limit=${limit}&offset=${offset}`, { signal });
  return response.data;
};

export const fetchVideoById = async (id, signal) => {
  const response = await api.get(`/videos/${id}`, { signal });
  return response.data;
};
