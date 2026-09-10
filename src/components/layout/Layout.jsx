import React, { useState, useEffect } from 'react';
import { Outlet, useOutletContext } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import ComposeModal from '../common/ComposeModal';
import { emailService } from '../../services/emailService';
import './Layout.css';

export const Layout = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [quarantineCount, setQuarantineCount] = useState(0);

  const refreshCounts = async () => {
    const inbox = await emailService.getEmails('inbox');
    const quarantine = await emailService.getQuarantineEmails();
    setUnreadCount(inbox.filter((e) => !e.isRead).length);
    setQuarantineCount(quarantine.length);
  };

  useEffect(() => {
    refreshCounts();
  }, []);

  const handleSendEmail = async (emailData) => {
    await emailService.sendEmail(emailData);
    refreshCounts();
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <Sidebar 
        onOpenCompose={() => setIsComposeOpen(true)}
        unreadCount={unreadCount}
        quarantineCount={quarantineCount}
      />

      {/* Main Content Viewport */}
      <div className="main-viewport">
        <Header 
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />

        <main className="content-area">
          <Outlet context={{ searchQuery, refreshCounts }} />
        </main>
      </div>

      {/* Compose Email Modal */}
      <ComposeModal 
        isOpen={isComposeOpen}
        onClose={() => setIsComposeOpen(false)}
        onSend={handleSendEmail}
      />
    </div>
  );
};

// Helper hook for pages to access layout context
export const useLayoutContext = () => useOutletContext();

export default Layout;
