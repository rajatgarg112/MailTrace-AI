import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  Bell, 
  ShieldAlert, 
  User, 
  LogOut, 
  ChevronDown, 
  Activity,
  X
} from 'lucide-react';
import './Header.css';

export const Header = ({ searchQuery, setSearchQuery }) => {
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  const mockAlerts = [
    { id: 1, title: 'High Risk Email Quarantined', desc: 'Credential harvesting pattern blocked from bank-security-center.com', time: '10m ago', type: 'critical' },
    { id: 2, title: 'Gateway Rule Applied', desc: 'DMARC strict enforcement policy updated for external MTA', time: '1h ago', type: 'info' }
  ];

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <header className="header-container">
      {/* Search Input Bar */}
      <div className="header-search-wrapper">
        <Search className="search-icon" size={18} />
        <input 
          type="text"
          className="header-search-input"
          placeholder="Search emails, domain headers, risk scores, or status..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {searchQuery && (
          <button className="btn-search-clear" onClick={() => setSearchQuery('')}>
            <X size={14} />
          </button>
        )}
      </div>

      {/* Center Gateway Status */}
      <div className="gateway-live-banner">
        <Activity size={14} className="activity-pulse" />
        <span className="gateway-live-text">
          Gateway Active <span className="text-dim">• Pre-Delivery Zero-Trust Intercept</span>
        </span>
      </div>

      {/* Right Controls */}
      <div className="header-actions">
        {/* Notifications Popover */}
        <div className="popover-wrapper">
          <button 
            className="header-icon-btn"
            onClick={() => setShowNotifications(!showNotifications)}
            title="Gateway Alerts"
          >
            <Bell size={18} />
            <span className="notification-badge-dot"></span>
          </button>

          {showNotifications && (
            <div className="header-dropdown notifications-dropdown">
              <div className="dropdown-header">
                <ShieldAlert size={16} className="text-warning" />
                <span>Gateway Threat Alerts</span>
              </div>
              <div className="dropdown-body">
                {mockAlerts.map(alert => (
                  <div key={alert.id} className={`alert-item alert-${alert.type}`}>
                    <div className="alert-title">{alert.title}</div>
                    <div className="alert-desc">{alert.desc}</div>
                    <div className="alert-time">{alert.time}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Profile */}
        <div className="popover-wrapper">
          <button 
            className="user-profile-btn"
            onClick={() => setShowUserDropdown(!showUserDropdown)}
          >
            <div className="user-avatar">
              <User size={18} />
            </div>
            <div className="user-details">
              <span className="user-name">Alex Dev</span>
              <span className="user-role">SecOps Analyst</span>
            </div>
            <ChevronDown size={14} className="user-chevron" />
          </button>

          {showUserDropdown && (
            <div className="header-dropdown user-dropdown">
              <div className="dropdown-user-info">
                <div className="font-semibold text-white">Alex Dev</div>
                <div className="text-xs text-muted">alex.dev@mailtrace.local</div>
                <div className="user-status-pill">Gateway Administrator</div>
              </div>
              <div className="dropdown-divider"></div>
              <button className="dropdown-btn text-danger" onClick={handleLogout}>
                <LogOut size={15} />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
