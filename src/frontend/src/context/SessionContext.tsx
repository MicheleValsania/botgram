import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface Session {
  username: string;
  isValid: boolean;
  limits?: {
    follow: number;
    like: number;
    comment: number;
  };
}

interface SessionContextType {
  session: Session | null;
  loading: boolean;
  error: string | null;
  login: (username: string, sessionId: string, cookies: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshLimits: () => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (username: string, sessionId: string, cookies: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/instagram/session', {
        username,
        session_id: sessionId,
        cookies,
        user_agent: navigator.userAgent
      });

      if (response.data.success) {
        setSession({
          username,
          isValid: true
        });
        await refreshLimits();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
      setSession(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    if (!session) return;

    setLoading(true);
    setError(null);
    try {
      await axios.delete(`/api/instagram/session/${session.username}`);
      setSession(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end session');
    } finally {
      setLoading(false);
    }
  };

  const refreshLimits = async () => {
    if (!session) return;

    try {
      const response = await axios.get(`/api/instagram/limits/${session.username}`);
      if (response.data.success) {
        setSession(prev => prev ? {
          ...prev,
          limits: response.data.data.limits
        } : null);
      }
    } catch (err) {
      console.error('Failed to refresh limits:', err);
    }
  };

  // Refresh limits periodically
  useEffect(() => {
    if (session) {
      const interval = setInterval(refreshLimits, 60000); // Every minute
      return () => clearInterval(interval);
    }
  }, [session]);

  return (
    <SessionContext.Provider value={{ session, loading, error, login, logout, refreshLimits }}>
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
