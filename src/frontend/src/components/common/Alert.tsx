import React, { useState, useEffect } from 'react';
import { FaCheckCircle, FaExclamationCircle, FaTimes } from 'react-icons/fa';

interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  onClose?: () => void;
  autoClose?: boolean;
  duration?: number;
}

const Alert: React.FC<AlertProps> = ({
  type,
  message,
  onClose,
  autoClose = true,
  duration = 5000,
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (autoClose && isVisible) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [autoClose, duration, isVisible, onClose]);

  if (!isVisible) return null;

  const icons = {
    success: <FaCheckCircle />,
    error: <FaExclamationCircle />,
    warning: <FaExclamationCircle />,
    info: <FaExclamationCircle />,
  };

  return (
    <div
      className={`alert alert-${type} d-flex align-items-center fade-in`}
      role="alert"
    >
      <div className="me-2">{icons[type]}</div>
      <div className="flex-grow-1">{message}</div>
      {onClose && (
        <button
          type="button"
          className="btn-close"
          onClick={() => {
            setIsVisible(false);
            onClose();
          }}
        >
          <FaTimes />
        </button>
      )}
    </div>
  );
};

export default Alert;
