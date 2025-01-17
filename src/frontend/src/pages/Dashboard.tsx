import React from 'react';
import { useSession } from '../context/SessionContext';
import { FaUser, FaHeart, FaComment, FaClock } from 'react-icons/fa';

const Dashboard: React.FC = () => {
  const { session } = useSession();

  if (!session) return null;

  return (
    <div>
      <h1 className="mb-4">Dashboard</h1>

      {/* Session Status */}
      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Session Status</h5>
          <div className="d-flex align-items-center">
            <div className={`status-indicator ${session.isValid ? 'bg-success' : 'bg-danger'}`}></div>
            <span className="ms-2">
              {session.isValid ? 'Active' : 'Inactive'}
            </span>
          </div>
          <p className="card-text mt-2">
            Logged in as: {session.username}
          </p>
        </div>
      </div>

      {/* Rate Limits */}
      <div className="row">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">
                <FaUser className="me-2" />
                Follow Limit
              </h5>
              <p className="card-text display-6">
                {session.limits?.follow || 0}
              </p>
              <div className="progress">
                <div
                  className="progress-bar"
                  role="progressbar"
                  style={{ width: `${(session.limits?.follow || 0) / 100 * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">
                <FaHeart className="me-2" />
                Like Limit
              </h5>
              <p className="card-text display-6">
                {session.limits?.like || 0}
              </p>
              <div className="progress">
                <div
                  className="progress-bar"
                  role="progressbar"
                  style={{ width: `${(session.limits?.like || 0) / 200 * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">
                <FaComment className="me-2" />
                Comment Limit
              </h5>
              <p className="card-text display-6">
                {session.limits?.comment || 0}
              </p>
              <div className="progress">
                <div
                  className="progress-bar"
                  role="progressbar"
                  style={{ width: `${(session.limits?.comment || 0) / 50 * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card mt-4">
        <div className="card-body">
          <h5 className="card-title">Quick Actions</h5>
          <div className="d-flex gap-2">
            <button
              className="btn btn-primary"
              onClick={() => window.location.href = '/actions'}
            >
              New Action
            </button>
            <button
              className="btn btn-outline-primary"
              onClick={() => window.location.href = '/sessions'}
            >
              Manage Sessions
            </button>
          </div>
        </div>
      </div>

      {/* Custom Styles */}
      <style>
        {`
          .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
          }
          
          .progress {
            height: 5px;
            margin-top: 10px;
          }
          
          .card {
            height: 100%;
            transition: transform 0.2s;
          }
          
          .card:hover {
            transform: translateY(-5px);
          }
        `}
      </style>
    </div>
  );
};

export default Dashboard;
