import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add auth token to requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh the token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('/api/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          
          const { access_token } = response.data.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry the original request with the new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return axios(originalRequest);
        } catch (refreshError) {
          // If refresh fails, logout
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  username: string;
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
  followUser: (data: {
    username: string;
    action_type: 'follow' | 'like' | 'comment';
    target_user_id?: string;
    media_id?: string;
    comment_text?: string;
  }) => {
    return axios.post('/api/instagram/follow', data);
  },

  likePost: (data: {
    username: string;
    action_type: 'follow' | 'like' | 'comment';
    target_user_id?: string;
    media_id?: string;
    comment_text?: string;
  }) => {
    return axios.post('/api/instagram/like', data);
  },

  commentPost: (data: {
    username: string;
    action_type: 'follow' | 'like' | 'comment';
    target_user_id?: string;
    media_id?: string;
    comment_text?: string;
  }) => {
    return axios.post('/api/instagram/comment', data);
  },

  // Limits
  getLimits: (username: string) => {
    return axios.get(`/api/instagram/limits/${username}`);
  },

  // Auth
  login: (credentials: LoginCredentials) => {
    return axios.post('/api/auth/login', credentials);
  },

  register: (userData: RegisterData) => {
    return axios.post('/api/auth/register', userData);
  },

  logout: () => {
    return axios.post('/api/auth/logout');
  },

  refreshToken: () => {
    const refreshToken = localStorage.getItem('refresh_token');
    return axios.post('/api/auth/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    });
  },

  getProfile: () => {
    return axios.get('/api/auth/me');
  }
};

export default api;
