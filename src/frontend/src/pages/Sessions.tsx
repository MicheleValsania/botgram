import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { FaPlus, FaTrash, FaCheck, FaTimes } from 'react-icons/fa';

interface SessionFormData {
  username: string;
  session_id: string;
  cookies: {
    sessionid: string;
    csrftoken: string;
  };
}

const Sessions: React.FC = () => {
  const { session, login, logout } = useSession();
  const [showNewSession, setShowNewSession] = useState(false);
  const [status, setStatus] = useState<{ success?: string; error?: string }>({});

  const formik = useFormik<SessionFormData>({
    initialValues: {
      username: '',
      session_id: '',
      cookies: {
        sessionid: '',
        csrftoken: '',
      },
    },
    validationSchema: Yup.object({
      username: Yup.string().required('Required'),
      session_id: Yup.string().required('Required'),
      cookies: Yup.object({
        sessionid: Yup.string().required('Required'),
        csrftoken: Yup.string().required('Required'),
      }),
    }),
    onSubmit: async (values, { setSubmitting, resetForm }) => {
      setStatus({});
      try {
        await login(values.username, values.session_id, values.cookies);
        setStatus({ success: 'Session created successfully' });
        resetForm();
        setShowNewSession(false);
      } catch (err) {
        setStatus({ error: err instanceof Error ? err.message : 'Failed to create session' });
      } finally {
        setSubmitting(false);
      }
    },
  });

  const handleEndSession = async () => {
    if (!session) return;
    
    try {
      await logout();
      setStatus({ success: 'Session ended successfully' });
    } catch (err) {
      setStatus({ error: err instanceof Error ? err.message : 'Failed to end session' });
    }
  };

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Sessions</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowNewSession(!showNewSession)}
        >
          <FaPlus className="me-2" />
          New Session
        </button>
      </div>

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

      {/* Current Session */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Current Session</h5>
        </div>
        <div className="card-body">
          {session ? (
            <div>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="mb-1">
                    <strong>Username:</strong> {session.username}
                  </p>
                  <p className="mb-1">
                    <strong>Status:</strong>{' '}
                    <span
                      className={`badge ${
                        session.isValid ? 'bg-success' : 'bg-danger'
                      }`}
                    >
                      {session.isValid ? 'Active' : 'Inactive'}
                    </span>
                  </p>
                  {session.limits && (
                    <p className="mb-0">
                      <strong>Limits:</strong> Follow: {session.limits.follow},{' '}
                      Like: {session.limits.like}, Comment: {session.limits.comment}
                    </p>
                  )}
                </div>
                <button
                  className="btn btn-danger"
                  onClick={handleEndSession}
                >
                  <FaTrash className="me-2" />
                  End Session
                </button>
              </div>
            </div>
          ) : (
            <p className="text-muted mb-0">No active session</p>
          )}
        </div>
      </div>

      {/* New Session Form */}
      {showNewSession && (
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">New Session</h5>
          </div>
          <div className="card-body">
            <form onSubmit={formik.handleSubmit}>
              <div className="mb-3">
                <label htmlFor="username" className="form-label">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  className={`form-control ${
                    formik.touched.username && formik.errors.username
                      ? 'is-invalid'
                      : ''
                  }`}
                  {...formik.getFieldProps('username')}
                />
                {formik.touched.username && formik.errors.username && (
                  <div className="invalid-feedback">{formik.errors.username}</div>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="session_id" className="form-label">
                  Session ID
                </label>
                <input
                  type="text"
                  id="session_id"
                  className={`form-control ${
                    formik.touched.session_id && formik.errors.session_id
                      ? 'is-invalid'
                      : ''
                  }`}
                  {...formik.getFieldProps('session_id')}
                />
                {formik.touched.session_id && formik.errors.session_id && (
                  <div className="invalid-feedback">{formik.errors.session_id}</div>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="cookies.sessionid" className="form-label">
                  Session Cookie
                </label>
                <input
                  type="text"
                  id="cookies.sessionid"
                  className={`form-control ${
                    formik.touched.cookies?.sessionid && formik.errors.cookies?.sessionid
                      ? 'is-invalid'
                      : ''
                  }`}
                  {...formik.getFieldProps('cookies.sessionid')}
                />
                {formik.touched.cookies?.sessionid && formik.errors.cookies?.sessionid && (
                  <div className="invalid-feedback">
                    {formik.errors.cookies.sessionid}
                  </div>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="cookies.csrftoken" className="form-label">
                  CSRF Token
                </label>
                <input
                  type="text"
                  id="cookies.csrftoken"
                  className={`form-control ${
                    formik.touched.cookies?.csrftoken && formik.errors.cookies?.csrftoken
                      ? 'is-invalid'
                      : ''
                  }`}
                  {...formik.getFieldProps('cookies.csrftoken')}
                />
                {formik.touched.cookies?.csrftoken && formik.errors.cookies?.csrftoken && (
                  <div className="invalid-feedback">
                    {formik.errors.cookies.csrftoken}
                  </div>
                )}
              </div>

              <div className="d-flex gap-2">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={formik.isSubmitting}
                >
                  {formik.isSubmitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <FaCheck className="me-2" />
                      Create Session
                    </>
                  )}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowNewSession(false)}
                >
                  <FaTimes className="me-2" />
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sessions;
