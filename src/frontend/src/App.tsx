import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SessionProvider } from './context/SessionContext';
import ProtectedLayout from './components/common/ProtectedLayout';
import Login from './pages/Login';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap JS
import 'bootstrap/dist/js/bootstrap.bundle.min';

const App: React.FC = () => {
  return (
    <SessionProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedLayout />}>
            {/* Protected routes will be added here */}
          </Route>
        </Routes>
      </Router>
    </SessionProvider>
  );
};

export default App;
