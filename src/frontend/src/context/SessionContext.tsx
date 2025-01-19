import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';

interface UserProfile {
  id: number;
  username: string;
  email: string;
}

interface Session {
  user: UserProfile | null;
  isAuthenticated: boolean;
}

interface SessionContextType {
  session: Session;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session>({ user: null, isAuthenticated: false });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already authenticated
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await api.getProfile();
          if (response.data.success) {
            setSession({
              user: response.data.data,
              isAuthenticated: true
            });
          }
        } catch (err) {
          // Token is invalid, remove it
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.login({ email, password });
      if (response.data.success) {
        const { access_token, refresh_token } = response.data.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        // Get user profile
        const profileResponse = await api.getProfile();
        if (profileResponse.data.success) {
          setSession({
            user: profileResponse.data.data,
            isAuthenticated: true
          });
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.register({ username, email, password });
      if (response.data.success) {
        // Auto login after registration
        await login(email, password);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await api.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setSession({ user: null, isAuthenticated: false });
      setLoading(false);
    }
  };

  return (
    <SessionContext.Provider
      value={{
        session,
        loading,
        error,
        login,
        logout,
        register
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};
