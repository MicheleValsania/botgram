import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import { Link } from 'react-router-dom';
import { 
  FaUser, FaEnvelope, FaInstagram, FaChartLine, FaCog, 
  FaRobot, FaHeart, FaComment, FaBookmark, FaHashtag,
  FaCalendarAlt, FaImage, FaChartBar, FaBell, FaUsers,
  FaRegClock, FaMedal, FaLightbulb
} from 'react-icons/fa';

const Dashboard: React.FC = () => {
  const { session } = useSession();
  const [activeTab, setActiveTab] = useState('activity');

  if (!session.isAuthenticated || !session.user) {
    return null;
  }

  const stats = {
    followers: 1234,
    following: 567,
    posts: 89,
    engagement: '4.5%',
    reach: '12.3K',
    impressions: '45.6K'
  };

  const quickActions = [
    {
      title: 'Automation',
      description: 'Configure your automation settings',
      icon: <FaRobot size={24} />,
      path: '/automation',
      color: 'primary'
    },
    {
      title: 'Analytics',
      description: 'View your performance metrics',
      icon: <FaChartLine size={24} />,
      path: '/analytics',
      color: 'success'
    },
    {
      title: 'Content Calendar',
      description: 'Schedule and plan your content',
      icon: <FaCalendarAlt size={24} />,
      path: '/calendar',
      color: 'info'
    },
    {
      title: 'Hashtag Manager',
      description: 'Organize and track hashtags',
      icon: <FaHashtag size={24} />,
      path: '/hashtags',
      color: 'warning'
    }
  ];

  const recentPosts = [
    {
      id: 1,
      image: 'https://picsum.photos/200',
      likes: 234,
      comments: 45,
      date: '2h ago'
    },
    {
      id: 2,
      image: 'https://picsum.photos/201',
      likes: 187,
      comments: 32,
      date: '4h ago'
    },
    {
      id: 3,
      image: 'https://picsum.photos/202',
      likes: 342,
      comments: 56,
      date: '6h ago'
    }
  ];

  return (
    <div className="dashboard-container">
      {/* Profile Overview */}
      <div className="row g-4 mb-4">
        <div className="col-lg-4">
          <div className="card shadow-sm h-100 border-0">
            <div className="card-body">
              <div className="d-flex align-items-center mb-4">
                <div className="profile-image me-3">
                  <img
                    src={`https://ui-avatars.com/api/?name=${session.user.username}&background=random`}
                    alt="Profile"
                    className="rounded-circle"
                    style={{ width: '80px', height: '80px' }}
                  />
                </div>
                <div>
                  <h4 className="mb-1">{session.user.username}</h4>
                  <p className="text-muted mb-0">
                    <FaEnvelope className="me-2" />
                    {session.user.email}
                  </p>
                </div>
              </div>
              <div className="row text-center g-3">
                <div className="col-4">
                  <div className="p-3 border rounded-3 bg-light">
                    <h5 className="mb-0">{stats.followers}</h5>
                    <small className="text-muted">Followers</small>
                  </div>
                </div>
                <div className="col-4">
                  <div className="p-3 border rounded-3 bg-light">
                    <h5 className="mb-0">{stats.following}</h5>
                    <small className="text-muted">Following</small>
                  </div>
                </div>
                <div className="col-4">
                  <div className="p-3 border rounded-3 bg-light">
                    <h5 className="mb-0">{stats.posts}</h5>
                    <small className="text-muted">Posts</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <div className="card shadow-sm h-100 border-0">
            <div className="card-body">
              <h5 className="card-title d-flex align-items-center mb-4">
                <FaLightbulb className="text-warning me-2" />
                Quick Actions
              </h5>
              <div className="row g-3">
                {quickActions.map((action, index) => (
                  <div key={index} className="col-md-6">
                    <Link to={action.path} className="text-decoration-none">
                      <div className="p-3 border rounded-3 bg-light d-flex align-items-center h-100 action-card">
                        <div className={`icon-wrapper bg-${action.color} text-white rounded-3 p-3 me-3`}>
                          {action.icon}
                        </div>
                        <div>
                          <h6 className="mb-1">{action.title}</h6>
                          <p className="mb-0 text-muted small">{action.description}</p>
                        </div>
                      </div>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="row g-4 mb-4">
        <div className="col-md-4">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <div className="d-flex align-items-center mb-3">
                <div className="icon-wrapper bg-primary text-white rounded-3 p-3 me-3">
                  <FaChartBar size={24} />
                </div>
                <div>
                  <h6 className="mb-1">Engagement Rate</h6>
                  <h4 className="mb-0">{stats.engagement}</h4>
                </div>
              </div>
              <div className="progress" style={{ height: '6px' }}>
                <div className="progress-bar bg-primary" style={{ width: '45%' }}></div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <div className="d-flex align-items-center mb-3">
                <div className="icon-wrapper bg-success text-white rounded-3 p-3 me-3">
                  <FaUsers size={24} />
                </div>
                <div>
                  <h6 className="mb-1">Total Reach</h6>
                  <h4 className="mb-0">{stats.reach}</h4>
                </div>
              </div>
              <div className="progress" style={{ height: '6px' }}>
                <div className="progress-bar bg-success" style={{ width: '65%' }}></div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <div className="d-flex align-items-center mb-3">
                <div className="icon-wrapper bg-info text-white rounded-3 p-3 me-3">
                  <FaRegClock size={24} />
                </div>
                <div>
                  <h6 className="mb-1">Impressions</h6>
                  <h4 className="mb-0">{stats.impressions}</h4>
                </div>
              </div>
              <div className="progress" style={{ height: '6px' }}>
                <div className="progress-bar bg-info" style={{ width: '75%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Tabs */}
      <div className="row g-4">
        <div className="col-lg-8">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <ul className="nav nav-tabs mb-4">
                <li className="nav-item">
                  <button 
                    className={`nav-link ${activeTab === 'activity' ? 'active' : ''}`}
                    onClick={() => setActiveTab('activity')}
                  >
                    <FaHeart className="me-2" />
                    Recent Activity
                  </button>
                </li>
                <li className="nav-item">
                  <button 
                    className={`nav-link ${activeTab === 'posts' ? 'active' : ''}`}
                    onClick={() => setActiveTab('posts')}
                  >
                    <FaImage className="me-2" />
                    Recent Posts
                  </button>
                </li>
              </ul>

              {activeTab === 'activity' ? (
                <div className="activity-timeline">
                  {[1, 2, 3].map((_, index) => (
                    <div key={index} className="activity-item d-flex mb-3">
                      <div className="activity-icon bg-light rounded-circle p-2 me-3">
                        <FaHeart className="text-danger" />
                      </div>
                      <div>
                        <p className="mb-1">Liked 3 posts from @user{index + 1}</p>
                        <small className="text-muted">{index + 1} hour ago</small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="row g-3">
                  {recentPosts.map(post => (
                    <div key={post.id} className="col-md-4">
                      <div className="card border-0 post-card">
                        <img src={post.image} className="card-img-top" alt="Post" />
                        <div className="card-body">
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <span className="me-3">
                                <FaHeart className="text-danger me-1" />
                                {post.likes}
                              </span>
                              <span>
                                <FaComment className="text-primary me-1" />
                                {post.comments}
                              </span>
                            </div>
                            <small className="text-muted">{post.date}</small>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card border-0 shadow-sm mb-4">
            <div className="card-body">
              <h5 className="card-title d-flex align-items-center mb-4">
                <FaMedal className="text-warning me-2" />
                Performance Highlights
              </h5>
              <div className="performance-item mb-3 p-3 border rounded-3 bg-light">
                <div className="d-flex justify-content-between mb-2">
                  <span>Best Performing Post</span>
                  <span className="badge bg-success">+324%</span>
                </div>
                <small className="text-muted">Your beach sunset photo reached 23K people</small>
              </div>
              <div className="performance-item mb-3 p-3 border rounded-3 bg-light">
                <div className="d-flex justify-content-between mb-2">
                  <span>Top Hashtag</span>
                  <span className="badge bg-primary">#photography</span>
                </div>
                <small className="text-muted">Used in 15 posts with high engagement</small>
              </div>
              <div className="performance-item p-3 border rounded-3 bg-light">
                <div className="d-flex justify-content-between mb-2">
                  <span>Best Time to Post</span>
                  <span className="badge bg-info">6:00 PM</span>
                </div>
                <small className="text-muted">Based on your audience activity</small>
              </div>
            </div>
          </div>

          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h5 className="card-title d-flex align-items-center mb-4">
                <FaBell className="text-danger me-2" />
                Upcoming Tasks
              </h5>
              <div className="task-item d-flex align-items-center mb-3">
                <div className="form-check">
                  <input type="checkbox" className="form-check-input" />
                  <label className="form-check-label">Schedule 3 posts for tomorrow</label>
                </div>
                <small className="text-muted ms-auto">Due today</small>
              </div>
              <div className="task-item d-flex align-items-center mb-3">
                <div className="form-check">
                  <input type="checkbox" className="form-check-input" />
                  <label className="form-check-label">Analyze last week's performance</label>
                </div>
                <small className="text-muted ms-auto">Due tomorrow</small>
              </div>
              <div className="task-item d-flex align-items-center">
                <div className="form-check">
                  <input type="checkbox" className="form-check-input" />
                  <label className="form-check-label">Update hashtag groups</label>
                </div>
                <small className="text-muted ms-auto">Due in 2 days</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Styles */}
      <style>
        {`
          .dashboard-container {
            padding: 1.5rem;
            background-color: #f8f9fa;
            min-height: calc(100vh - 64px);
          }
          
          .icon-wrapper {
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s;
          }
          
          .action-card {
            transition: all 0.3s ease;
            border: 1px solid #e9ecef;
          }
          
          .action-card:hover {
            transform: translateY(-5px);
            border-color: var(--bs-primary);
            background-color: #fff !important;
          }
          
          .activity-timeline .activity-item:not(:last-child) {
            border-left: 2px solid #e9ecef;
            padding-left: 1.5rem;
            margin-left: 1rem;
          }
          
          .activity-icon {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          
          .card {
            transition: transform 0.2s;
          }
          
          .card:hover {
            transform: translateY(-5px);
          }
          
          .post-card {
            overflow: hidden;
          }
          
          .post-card img {
            height: 200px;
            object-fit: cover;
            transition: transform 0.3s ease;
          }
          
          .post-card:hover img {
            transform: scale(1.1);
          }
          
          .nav-tabs .nav-link {
            border: none;
            color: #6c757d;
            padding: 0.5rem 1rem;
            margin-right: 1rem;
            font-weight: 500;
          }
          
          .nav-tabs .nav-link.active {
            color: var(--bs-primary);
            border-bottom: 2px solid var(--bs-primary);
            background: none;
          }
          
          .performance-item {
            transition: all 0.3s ease;
          }
          
          .performance-item:hover {
            background-color: #fff !important;
            transform: translateX(5px);
          }
          
          .task-item {
            padding: 0.5rem;
            border-radius: 0.375rem;
            transition: background-color 0.2s;
          }
          
          .task-item:hover {
            background-color: #f8f9fa;
          }
          
          .form-check-input:checked {
            background-color: var(--bs-primary);
            border-color: var(--bs-primary);
          }
        `}
      </style>
    </div>
  );
};

export default Dashboard;
