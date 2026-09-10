import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Inbox, 
  Star, 
  Send, 
  FileText, 
  Lock, 
  Trash2, 
  Shield, 
  Plus, 
  CheckCircle2, 
  Sliders,
  Award,
  Zap
} from 'lucide-react';
import './Sidebar.css';

export const Sidebar = ({ onOpenCompose, unreadCount = 2, quarantineCount = 2 }) => {
  const navItems = [
    { label: 'Inbox', path: '/inbox', icon: Inbox, count: unreadCount, countClass: 'count-primary' },
    { label: 'Starred', path: '/starred', icon: Star },
    { label: 'Sent', path: '/sent', icon: Send },
    { label: 'Drafts', path: '/drafts', icon: FileText },
    { label: 'Quarantine', path: '/quarantine', icon: Lock, count: quarantineCount, countClass: 'count-warning' },
    { label: 'Trash', path: '/trash', icon: Trash2 },
  ];

  return (
    <aside className="sidebar-container">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-logo">
          <Shield className="brand-icon" />
          <span className="brand-pulse"></span>
        </div>
        <div className="brand-info">
          <h1 className="brand-title">
            MailTrace <span className="brand-badge">AI</span>
          </h1>
          <div className="brand-sih-tag">
            <Award size={11} className="text-cyan" />
            <span>SIH 26106 Gateway</span>
          </div>
        </div>
      </div>

      {/* Action Compose Button */}
      <div className="sidebar-action">
        <button className="btn-compose" onClick={onOpenCompose}>
          <Plus size={18} />
          <span>New Message</span>
        </button>
      </div>

      {/* Main Mail Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">Mailboxes</div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} className="nav-icon" />
              <span className="nav-label">{item.label}</span>
              {item.count !== undefined && item.count > 0 && (
                <span className={`nav-count ${item.countClass}`}>{item.count}</span>
              )}
            </NavLink>
          );
        })}

        {/* Security Operations Section */}
        <div className="nav-section-title">Gateway Ops</div>
        <NavLink
          to="/security"
          className={({ isActive }) => `nav-item nav-security ${isActive ? 'active' : ''}`}
        >
          <Shield size={18} className="nav-icon text-cyan" />
          <span className="nav-label font-semibold">Security Dashboard</span>
          <span className="status-dot-active" title="Gateway Active"></span>
        </NavLink>
      </nav>

      {/* Footer / Status Card */}
      <div className="sidebar-footer">
        <div className="gateway-status-card">
          <div className="status-header">
            <CheckCircle2 size={14} className="status-check-icon" />
            <span>Pre-Delivery Intercept</span>
          </div>
          <div className="status-latency-row">
            <Zap size={11} className="text-cyan" />
            <span>142ms Avg Latency</span>
          </div>
        </div>

        <button className="btn-settings-placeholder" title="Gateway Settings">
          <Sliders size={16} />
          <span>Gateway Settings</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
