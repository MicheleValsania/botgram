import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useSession } from '../context/SessionContext';
import api from '../services/api';
import { FaUser, FaLock } from 'react-icons/fa';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useSession();
  const [error, setError] = useState<string | null>(null);

  const formik = useFormik({
    initialValues: {
      username: '',
      password: '',
    },
    validationSchema: Yup.object({
      username: Yup.string().required('Username is required'),
      password: Yup.string().required('Password is required'),
    }),
    onSubmit: async (values) => {
      try {
        setError(null);
        const response = await api.login(values);
        if (response.data && response.data.data && response.data.data.access_token) {
          localStorage.setItem('token', response.data.data.access_token);
          localStorage.setItem('refresh_token', response.data.data.refresh_token);
          await login(values.username, '', {});
          navigate('/');
        } else {
          setError('Login failed: Invalid response from server');
        }
      } catch (err) {
        console.error('Login error:', err);
        const errorMessage = err.response?.data?.message || (err instanceof Error ? err.message : 'Login failed');
        setError(errorMessage);
      }
    },
  });

  return (
    <div className="d-flex" style={{ height: '100vh' }}>
      {/* Left side - Logo and illustration */}
      <div className="d-none d-lg-flex flex-column justify-content-between bg-dark text-white p-5" style={{ width: '45%' }}>
        <div className="text-center">
          <img
            src="/static/images/pluto-logo-dog.jpg"
            alt="Pluto Logo"
            style={{ 
              width: '200px',
              borderRadius: '10px'
            }}
          />
        </div>
        
        <div className="text-center">
          <h1 className="display-5 mb-3" style={{ fontWeight: '600' }}>
            Forget the dog days of Instagram.
          </h1>
          <h2 className="h3 mb-4" style={{ color: '#405DE6' }}>
            Pluto is here to shake up your feed!
          </h2>
        </div>

        <div className="text-center mb-4">
          <img
            src="/static/images/smartphone_girl.jpg"
            alt="Instagram Automation"
            style={{ 
              maxWidth: '85%',
              borderRadius: '20px',
              boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
            }}
          />
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="flex-grow-1 d-flex align-items-center justify-content-center p-4" style={{ backgroundColor: '#f8f9fa' }}>
        <div style={{ width: '400px' }}>
          {/* Show logo only on mobile */}
          <div className="d-lg-none text-center mb-4">
            <img
              src="/static/images/pluto-logo-dog.jpg"
              alt="Pluto Logo"
              style={{ 
                width: '150px',
                borderRadius: '10px'
              }}
            />
            <h2 className="h4 mt-3 mb-4" style={{ color: '#405DE6' }}>
              Pluto is here to shake up your feed!
            </h2>
          </div>

          <div className="card border-0 shadow-sm">
            <div className="card-body p-4">
              <h2 className="card-title text-center mb-4">Sign In</h2>

              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}

              <form onSubmit={formik.handleSubmit}>
                <div className="mb-3">
                  <div className="input-group">
                    <span className="input-group-text">
                      <FaUser />
                    </span>
                    <input
                      id="username"
                      type="text"
                      placeholder="Instagram Username"
                      className={`form-control ${
                        formik.touched.username && formik.errors.username
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...formik.getFieldProps('username')}
                    />
                    {formik.touched.username && formik.errors.username && (
                      <div className="invalid-feedback">
                        {formik.errors.username}
                      </div>
                    )}
                  </div>
                </div>

                <div className="mb-4">
                  <div className="input-group">
                    <span className="input-group-text">
                      <FaLock />
                    </span>
                    <input
                      id="password"
                      type="password"
                      placeholder="Password"
                      className={`form-control ${
                        formik.touched.password && formik.errors.password
                          ? 'is-invalid'
                          : ''
                      }`}
                      {...formik.getFieldProps('password')}
                    />
                    {formik.touched.password && formik.errors.password && (
                      <div className="invalid-feedback">
                        {formik.errors.password}
                      </div>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 py-2"
                  disabled={formik.isSubmitting}
                >
                  {formik.isSubmitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" />
                      Signing in...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
