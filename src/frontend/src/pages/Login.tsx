import React from 'react';
import AuthForm from '../components/auth/AuthForm';
import { FaInstagram } from 'react-icons/fa';

const Login: React.FC = () => {
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

      {/* Right side - Auth form */}
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

          <AuthForm />
        </div>
      </div>
    </div>
  );
};

export default Login;