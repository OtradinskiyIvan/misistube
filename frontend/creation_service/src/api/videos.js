import axios from 'axios';

function getToken() {
  const stored = localStorage.getItem('auth_user');
  if (!stored) return null;
  try {
    return JSON.parse(stored).token;
  } catch {
    return null;
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_user');
    }
    return Promise.reject(error);
  }
);

export const getUserIdFromToken = () => {
  const token = getToken();
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
