import React, { useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './AuthForm.scss';

interface AuthFormValues {
  email: string;
  password: string;
  username?: string;
}

const validationSchemas = {
  login: Yup.object({
    email: Yup.string()
      .email('Invalid email address')
      .required('Email is required'),
    password: Yup.string()
      .required('Password is required')
  }),
  register: Yup.object({
    username: Yup.string()
      .min(3, 'Username must be at least 3 characters')
      .required('Username is required'),
    email: Yup.string()
      .email('Invalid email address')
      .required('Email is required'),
    password: Yup.string()
      .min(8, 'Password must be at least 8 characters')
      .matches(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
        'Password must contain at least one uppercase letter, one lowercase letter, one number and one special character'
      )
      .required('Password is required')
  })
};

const AuthForm: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError(null);
  };

  const handleSubmit = async (values: AuthFormValues) => {
    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const response = await axios.post(`http://localhost:5000${endpoint}`, values);
      
      if (response.data.success) {
        const { access_token, refresh_token } = response.data.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        navigate('/dashboard');
      } else {
        setError(response.data.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'An error occurred');
    }
  };

  const initialValues: AuthFormValues = {
    email: '',
    password: '',
    ...(isLogin ? {} : { username: '' })
  };

  return (
    <div className="auth-form-container">
      <div className="auth-form-box">
        <h2>{isLogin ? 'Login' : 'Register'}</h2>
        
        <div className="auth-toggle">
          <button
            className={`toggle-btn ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button
            className={`toggle-btn ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Register
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <Formik
          initialValues={initialValues}
          validationSchema={isLogin ? validationSchemas.login : validationSchemas.register}
          onSubmit={handleSubmit}
          enableReinitialize
        >
          {({ isSubmitting }) => (
            <Form>
              {!isLogin && (
                <div className="form-group">
                  <label htmlFor="username">Username</label>
                  <Field
                    type="text"
                    name="username"
                    className="form-control"
                    placeholder="Enter username"
                  />
                  <ErrorMessage name="username" component="div" className="error" />
                </div>
              )}

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <Field
                  type="email"
                  name="email"
                  className="form-control"
                  placeholder="Enter email"
                />
                <ErrorMessage name="email" component="div" className="error" />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <Field
                  type="password"
                  name="password"
                  className="form-control"
                  placeholder="Enter password"
                />
                <ErrorMessage name="password" component="div" className="error" />
              </div>

              <button
                type="submit"
                className="submit-btn"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
              </button>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default AuthForm;
