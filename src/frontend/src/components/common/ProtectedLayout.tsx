import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useSession } from '../../context/SessionContext';
import Navbar from './Navbar';

const ProtectedLayout: React.FC = () => {
  const { session, loading } = useSession();

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!session.isAuthenticated || !session.user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div>
      <Navbar />
      <main className="container py-4">
        <Outlet />
      </main>
    </div>
  );
};

export default ProtectedLayout;
