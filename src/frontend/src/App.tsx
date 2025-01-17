import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SessionProvider } from './context/SessionContext';
import ProtectedLayout from './components/common/ProtectedLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ManualActions from './pages/ManualActions';
import Sessions from './pages/Sessions';
import Settings from './pages/Settings';

// Import custom styles
import './styles/global.scss';

const App: React.FC = () => {
  return (
    <SessionProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="actions" element={<ManualActions />} />
            <Route path="sessions" element={<Sessions />} />
            <Route path="settings" element={<Settings />} />
            {/* Other protected routes will be added here */}
          </Route>
        </Routes>
      </Router>
    </SessionProvider>
  );
};

export default App;
