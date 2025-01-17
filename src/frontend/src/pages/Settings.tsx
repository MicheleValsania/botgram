import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { FaSave, FaCog, FaShieldAlt, FaClock } from 'react-icons/fa';

interface RateLimits {
  follow: {
    max_per_day: number;
    delay_seconds: number;
  };
  like: {
    max_per_day: number;
    delay_seconds: number;
  };
  comment: {
    max_per_day: number;
    delay_seconds: number;
  };
}

interface SecuritySettings {
  enable_proxy: boolean;
  proxy_url?: string;
  user_agent?: string;
}

const Settings: React.FC = () => {
  const { session } = useSession();
  const [activeTab, setActiveTab] = useState('limits');
  const [status, setStatus] = useState<{ success?: string; error?: string }>({});

  const limitsFormik = useFormik({
    initialValues: {
      follow: {
        max_per_day: 100,
        delay_seconds: 30,
      },
      like: {
        max_per_day: 200,
        delay_seconds: 20,
      },
      comment: {
        max_per_day: 50,
        delay_seconds: 60,
      },
    } as RateLimits,
    validationSchema: Yup.object({
      follow: Yup.object({
        max_per_day: Yup.number()
          .required('Required')
          .min(1, 'Must be at least 1')
          .max(1000, 'Must be at most 1000'),
        delay_seconds: Yup.number()
          .required('Required')
          .min(10, 'Must be at least 10 seconds')
          .max(3600, 'Must be at most 1 hour'),
      }),
      like: Yup.object({
        max_per_day: Yup.number()
          .required('Required')
          .min(1, 'Must be at least 1')
          .max(1000, 'Must be at most 1000'),
        delay_seconds: Yup.number()
          .required('Required')
          .min(10, 'Must be at least 10 seconds')
          .max(3600, 'Must be at most 1 hour'),
      }),
      comment: Yup.object({
        max_per_day: Yup.number()
          .required('Required')
          .min(1, 'Must be at least 1')
          .max(500, 'Must be at most 500'),
        delay_seconds: Yup.number()
          .required('Required')
          .min(30, 'Must be at least 30 seconds')
          .max(3600, 'Must be at most 1 hour'),
      }),
    }),
    onSubmit: async (values, { setSubmitting }) => {
      setStatus({});
      try {
        // TODO: Implement API call to save rate limits
        setStatus({ success: 'Rate limits updated successfully' });
      } catch (err) {
        setStatus({ error: err instanceof Error ? err.message : 'Failed to update rate limits' });
      } finally {
        setSubmitting(false);
      }
    },
  });

  const securityFormik = useFormik({
    initialValues: {
      enable_proxy: false,
      proxy_url: '',
      user_agent: navigator.userAgent,
    } as SecuritySettings,
    validationSchema: Yup.object({
      enable_proxy: Yup.boolean(),
      proxy_url: Yup.string().when('enable_proxy', {
        is: true,
        then: schema => schema.required('Required when proxy is enabled')
          .matches(/^(http|https|socks[45]):\/\/.+:\d+$/, 'Invalid proxy URL format'),
      }),
      user_agent: Yup.string(),
    }),
    onSubmit: async (values, { setSubmitting }) => {
      setStatus({});
      try {
        // TODO: Implement API call to save security settings
        setStatus({ success: 'Security settings updated successfully' });
      } catch (err) {
        setStatus({ error: err instanceof Error ? err.message : 'Failed to update security settings' });
      } finally {
        setSubmitting(false);
      }
    },
  });

  if (!session) return null;

  return (
    <div className="container">
      <h1 className="mb-4">Settings</h1>

      {status.success && (
        <div className="alert alert-success" role="alert">
          {status.success}
        </div>
      )}

      {status.error && (
        <div className="alert alert-danger" role="alert">
          {status.error}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'limits' ? 'active' : ''}`}
                onClick={() => setActiveTab('limits')}
              >
                <FaClock className="me-2" />
                Rate Limits
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                <FaShieldAlt className="me-2" />
                Security
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {activeTab === 'limits' && (
            <form onSubmit={limitsFormik.handleSubmit}>
              <div className="row">
                <div className="col-md-4">
                  <h5>Follow Limits</h5>
                  <div className="mb-3">
                    <label htmlFor="follow.max_per_day" className="form-label">
                      Max Per Day
                    </label>
                    <input
                      type="number"
                      id="follow.max_per_day"
                      className={`form-control ${
                        limitsFormik.touched.follow?.max_per_day &&
                        limitsFormik.errors.follow?.max_per_day
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...limitsFormik.getFieldProps('follow.max_per_day')}
                    />
                    {limitsFormik.touched.follow?.max_per_day &&
                      limitsFormik.errors.follow?.max_per_day && (
                        <div className="invalid-feedback">
                          {limitsFormik.errors.follow.max_per_day}
                        </div>
                      )}
                  </div>
                  <div className="mb-3">
                    <label htmlFor="follow.delay_seconds" className="form-label">
                      Delay (seconds)
                    </label>
                    <input
                      type="number"
                      id="follow.delay_seconds"
                      className={`form-control ${
                        limitsFormik.touched.follow?.delay_seconds &&
                        limitsFormik.errors.follow?.delay_seconds
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...limitsFormik.getFieldProps('follow.delay_seconds')}
                    />
                    {limitsFormik.touched.follow?.delay_seconds &&
                      limitsFormik.errors.follow?.delay_seconds && (
                        <div className="invalid-feedback">
                          {limitsFormik.errors.follow.delay_seconds}
                        </div>
                      )}
                  </div>
                </div>

                <div className="col-md-4">
                  <h5>Like Limits</h5>
                  <div className="mb-3">
                    <label htmlFor="like.max_per_day" className="form-label">
                      Max Per Day
                    </label>
                    <input
                      type="number"
                      id="like.max_per_day"
                      className={`form-control ${
                        limitsFormik.touched.like?.max_per_day &&
                        limitsFormik.errors.like?.max_per_day
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...limitsFormik.getFieldProps('like.max_per_day')}
                    />
                    {limitsFormik.touched.like?.max_per_day &&
                      limitsFormik.errors.like?.max_per_day && (
                        <div className="invalid-feedback">
                          {limitsFormik.errors.like.max_per_day}
                        </div>
                      )}
                  </div>
                  <div className="mb-3">
                    <label htmlFor="like.delay_seconds" className="form-label">
                      Delay (seconds)
                    </label>
                    <input
                      type="number"
                      id="like.delay_seconds"
                      className={`form-control ${
                        limitsFormik.touched.like?.delay_seconds &&
                        limitsFormik.errors.like?.delay_seconds
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...limitsFormik.getFieldProps('like.delay_seconds')}
                    />
                    {limitsFormik.touched.like?.delay_seconds &&
                      limitsFormik.errors.like?.delay_seconds && (
                        <div className="invalid-feedback">
                          {limitsFormik.errors.like.delay_seconds}
                        </div>
                      )}
                  </div>
                </div>

                <div className="col-md-4">
                  <h5>Comment Limits</h5>
                  <div className="mb-3">
                    <label htmlFor="comment.max_per_day" className="form-label">
                      Max Per Day
                    </label>
                    <input
                      type="number"
                      id="comment.max_per_day"
                      className={`form-control ${
                        limitsFormik.touched.comment?.max_per_day &&
                        limitsFormik.errors.comment?.max_per_day
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...limitsFormik.getFieldProps('comment.max_per_day')}
                    />
                    {limitsFormik.touched.comment?.max_per_day &&
                      limitsFormik.errors.comment?.max_per_day && (
                        <div className="invalid-feedback">
                          {limitsFormik.errors.comment.max_per_day}
                        </div>
                      )}
                  </div>
                  <div className="mb-3">
                    <label htmlFor="comment.delay_seconds" className="form-label">
                      Delay (seconds)
                    </label>
                    <input
                      type="number"
                      id="comment.delay_seconds"
                      className={`form-control ${
                        limitsFormik.touched.comment?.delay_seconds &&
                        limitsFormik.errors.comment?.delay_seconds
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...limitsFormik.getFieldProps('comment.delay_seconds')}
                    />
                    {limitsFormik.touched.comment?.delay_seconds &&
                      limitsFormik.errors.comment?.delay_seconds && (
                        <div className="invalid-feedback">
                          {limitsFormik.errors.comment.delay_seconds}
                        </div>
                      )}
                  </div>
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={limitsFormik.isSubmitting}
              >
                {limitsFormik.isSubmitting ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" />
                    Saving...
                  </>
                ) : (
                  <>
                    <FaSave className="me-2" />
                    Save Rate Limits
                  </>
                )}
              </button>
            </form>
          )}

          {activeTab === 'security' && (
            <form onSubmit={securityFormik.handleSubmit}>
              <div className="mb-3">
                <div className="form-check form-switch">
                  <input
                    type="checkbox"
                    id="enable_proxy"
                    className="form-check-input"
                    {...securityFormik.getFieldProps('enable_proxy')}
                  />
                  <label htmlFor="enable_proxy" className="form-check-label">
                    Enable Proxy
                  </label>
                </div>
              </div>

              {securityFormik.values.enable_proxy && (
                <div className="mb-3">
                  <label htmlFor="proxy_url" className="form-label">
                    Proxy URL
                  </label>
                  <input
                    type="text"
                    id="proxy_url"
                    className={`form-control ${
                      securityFormik.touched.proxy_url &&
                      securityFormik.errors.proxy_url
                        ? 'is-invalid'
                        : ''
                    }`}
                    placeholder="http://proxy.example.com:8080"
                    {...securityFormik.getFieldProps('proxy_url')}
                  />
                  {securityFormik.touched.proxy_url &&
                    securityFormik.errors.proxy_url && (
                      <div className="invalid-feedback">
                        {securityFormik.errors.proxy_url}
                      </div>
                    )}
                </div>
              )}

              <div className="mb-3">
                <label htmlFor="user_agent" className="form-label">
                  User Agent
                </label>
                <input
                  type="text"
                  id="user_agent"
                  className="form-control"
                  {...securityFormik.getFieldProps('user_agent')}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={securityFormik.isSubmitting}
              >
                {securityFormik.isSubmitting ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" />
                    Saving...
                  </>
                ) : (
                  <>
                    <FaSave className="me-2" />
                    Save Security Settings
                  </>
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
