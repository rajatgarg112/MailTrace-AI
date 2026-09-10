import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Paperclip, Shield, RefreshCw, Inbox as InboxIcon, ShieldCheck, Mail, MailOpen } from 'lucide-react';
import SecurityBadge from '../components/common/SecurityBadge';
import { emailService } from '../services/emailService';
import { useLayoutContext } from '../components/layout/Layout';
import './Inbox.css';

export const Inbox = () => {
  const navigate = useNavigate();
  const { searchQuery, refreshCounts } = useLayoutContext() || {};
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('ALL'); // ALL | UNREAD | SAFE | WARNING

  const fetchInbox = async () => {
    setLoading(true);
    const data = await emailService.getEmails('inbox');
    setEmails(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchInbox();
  }, []);

  const handleToggleStar = async (e, id) => {
    e.stopPropagation();
    await emailService.toggleStar(id);
    fetchInbox();
  };

  const handleToggleRead = async (e, id, currentReadState) => {
    e.stopPropagation();
    await emailService.markAsRead(id, !currentReadState);
    fetchInbox();
    if (refreshCounts) refreshCounts();
  };

  const handleEmailClick = async (id) => {
    await emailService.markAsRead(id, true);
    if (refreshCounts) refreshCounts();
    navigate(`/email/${id}`);
  };

  // Filter & Search Logic
  const filteredEmails = emails.filter((item) => {
    if (activeFilter === 'UNREAD' && item.isRead) return false;
    if (activeFilter === 'SAFE' && item.status !== 'SAFE') return false;
    if (activeFilter === 'WARNING' && item.status !== 'WARNING') return false;

    if (searchQuery && searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      return (
        item.sender.toLowerCase().includes(q) ||
        item.senderEmail.toLowerCase().includes(q) ||
        item.subject.toLowerCase().includes(q) ||
        item.preview.toLowerCase().includes(q) ||
        item.status.toLowerCase().includes(q)
      );
    }

    return true;
  });

  return (
    <div className="inbox-page">
      {/* Gateway Pre-Delivery Protective Banner */}
      <div className="gateway-notice-banner">
        <ShieldCheck size={18} className="text-emerald flex-shrink-0" />
        <div className="notice-text">
          <strong>Pre-Delivery Security Active:</strong> Emails are intercepted, cryptographically verified (SPF/DKIM/DMARC), and scanned for zero-day threats prior to landing in your mailbox.
        </div>
      </div>

      {/* Page Bar */}
      <div className="inbox-toolbar">
        <div className="toolbar-title">
          <InboxIcon size={20} className="text-cyan" />
          <h2>Gateway Mailbox</h2>
          <span className="inbox-count-tag">{emails.length} Verified Deliveries</span>
        </div>

        {/* Filter Pills */}
        <div className="inbox-filters">
          <button 
            className={`filter-pill ${activeFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setActiveFilter('ALL')}
          >
            All
          </button>
          <button 
            className={`filter-pill ${activeFilter === 'UNREAD' ? 'active' : ''}`}
            onClick={() => setActiveFilter('UNREAD')}
          >
            Unread ({emails.filter(e => !e.isRead).length})
          </button>
          <button 
            className={`filter-pill ${activeFilter === 'SAFE' ? 'active' : ''}`}
            onClick={() => setActiveFilter('SAFE')}
          >
            Verified Safe
          </button>
          <button 
            className={`filter-pill ${activeFilter === 'WARNING' ? 'active' : ''}`}
            onClick={() => setActiveFilter('WARNING')}
          >
            Security Warnings
          </button>
          <button className="btn-refresh" onClick={fetchInbox} title="Refresh Inbox">
            <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
          </button>
        </div>
      </div>

      {/* Email Table Container */}
      <div className="inbox-table-card">
        {loading ? (
          <div className="inbox-state-box">
            <RefreshCw size={32} className="spin-icon text-cyan" />
            <p>Evaluating Gateway Messages...</p>
          </div>
        ) : filteredEmails.length === 0 ? (
          <div className="inbox-state-box">
            <Shield size={36} className="text-muted" />
            <h3>No Messages Found</h3>
            <p>There are no messages matching your active gateway filters.</p>
          </div>
        ) : (
          <div className="email-rows-list">
            {filteredEmails.map((email) => {
              const domain = email.senderEmail.split('@')[1] || '';
              return (
                <div 
                  key={email.id} 
                  className={`email-row ${!email.isRead ? 'unread' : 'read'} status-${email.status.toLowerCase()}`}
                  onClick={() => handleEmailClick(email.id)}
                >
                  {/* Star Button */}
                  <button 
                    className={`btn-star ${email.isStarred ? 'starred' : ''}`}
                    onClick={(e) => handleToggleStar(e, email.id)}
                    title={email.isStarred ? 'Unstar' : 'Star message'}
                  >
                    <Star size={16} fill={email.isStarred ? '#f59e0b' : 'none'} />
                  </button>

                  {/* Mark Read/Unread Toggle Button */}
                  <button 
                    className="btn-mark-read"
                    onClick={(e) => handleToggleRead(e, email.id, email.isRead)}
                    title={email.isRead ? 'Mark as unread' : 'Mark as read'}
                  >
                    {email.isRead ? <MailOpen size={15} /> : <Mail size={15} className="text-cyan" />}
                  </button>

                  {/* Sender Information */}
                  <div className="email-sender-col">
                    <span className="sender-name">{email.sender}</span>
                    <span className="sender-domain-tag">@{domain}</span>
                  </div>

                  {/* Subject & Body Preview */}
                  <div className="email-content-col">
                    <span className="email-subject">{email.subject}</span>
                    <span className="email-preview">— {email.preview}</span>
                  </div>

                  {/* Indicators & Badge */}
                  <div className="email-meta-col">
                    {email.hasAttachment && (
                      <span className="att-pill" title="Verified Attachment">
                        <Paperclip size={12} />
                        <span>File</span>
                      </span>
                    )}

                    {email.riskScore !== null && email.riskScore !== undefined && (
                      <span 
                        className={`risk-score-pill ${email.riskScore > 0.5 ? 'risk-high' : 'risk-low'}`}
                        title="MailTrace Risk Score"
                      >
                        Risk {(email.riskScore * 100).toFixed(0)}%
                      </span>
                    )}
                    
                    <SecurityBadge status={email.status} size="sm" />

                    <span className="email-date">{email.date}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Inbox;
