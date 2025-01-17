import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSession } from '../../context/SessionContext';
import { FaCog, FaSignOutAlt } from 'react-icons/fa';

const Navbar: React.FC = () => {
  const { session, logout } = useSession();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!session) return null;

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand d-flex align-items-center" to="/">
          <img
            src="/static/images/logo.svg"
            alt="Botgram Logo"
            height="30"
            className="me-2"
          />
          Botgram
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link className="nav-link" to="/">
                Dashboard
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/sessions">
                Sessions
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/actions">
                Actions
              </Link>
            </li>
          </ul>

          <ul className="navbar-nav">
            <li className="nav-item">
              <span className="nav-link">
                {session.username}
              </span>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/settings">
                <FaCog />
              </Link>
            </li>
            <li className="nav-item">
              <button
                className="nav-link btn btn-link"
                onClick={handleLogout}
              >
                <FaSignOutAlt />
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
