import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Inbox from './pages/Inbox';
import Starred from './pages/Starred';
import Sent from './pages/Sent';
import Drafts from './pages/Drafts';
import Quarantine from './pages/Quarantine';
import Trash from './pages/Trash';
import SecurityDashboard from './pages/SecurityDashboard';
import EmailView from './pages/EmailView';

export function App() {
  return (
    <Router>
      <Routes>
        {/* Auth Route */}
        <Route path="/login" element={<Login />} />

        {/* Main Application Layout with Navigation */}
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/inbox" replace />} />
          <Route path="inbox" element={<Inbox />} />
          <Route path="starred" element={<Starred />} />
          <Route path="sent" element={<Sent />} />
          <Route path="drafts" element={<Drafts />} />
          <Route path="quarantine" element={<Quarantine />} />
          <Route path="trash" element={<Trash />} />
          <Route path="security" element={<SecurityDashboard />} />
          <Route path="email/:id" element={<EmailView />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/inbox" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
