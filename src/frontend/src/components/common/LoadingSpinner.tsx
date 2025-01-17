import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  fullscreen?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  fullscreen = false,
}) => {
  const spinnerSize = {
    sm: '1rem',
    md: '2rem',
    lg: '3rem',
  }[size];

  if (fullscreen) {
    return (
      <div className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-white bg-opacity-75" style={{ zIndex: 1050 }}>
        <div
          className={`spinner-border text-${color}`}
          style={{ width: spinnerSize, height: spinnerSize }}
          role="status"
        >
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`spinner-border text-${color}`}
      style={{ width: spinnerSize, height: spinnerSize }}
      role="status"
    >
      <span className="visually-hidden">Loading...</span>
    </div>
  );
};

export default LoadingSpinner;
