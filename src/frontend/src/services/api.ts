import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add auth token to requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface InstagramAction {
  username: string;
  action_type: 'follow' | 'like' | 'comment';
  target_user_id?: string;
  media_id?: string;
  comment_text?: string;
}

const api = {
  // Session management
  createSession: (data: {
    username: string;
    session_id: string;
    cookies: any;
    user_agent: string;
  }) => {
    return axios.post('/api/instagram/session', data);
  },

  endSession: (username: string) => {
    return axios.delete(`/api/instagram/session/${username}`);
  },

  // Instagram actions
  followUser: (data: InstagramAction) => {
    return axios.post('/api/instagram/follow', data);
  },

  likePost: (data: InstagramAction) => {
    return axios.post('/api/instagram/like', data);
  },

  commentPost: (data: InstagramAction) => {
    return axios.post('/api/instagram/comment', data);
  },

  // Limits
  getLimits: (username: string) => {
    return axios.get(`/api/instagram/limits/${username}`);
  },

  // Auth
  login: (credentials: { username: string; password: string }) => {
    return axios.post('/api/auth/login', credentials);
  },

  register: (userData: { username: string; password: string; email: string }) => {
    return axios.post('/api/auth/register', userData);
  }
};

export default api;
