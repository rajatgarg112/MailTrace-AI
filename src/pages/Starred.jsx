import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Paperclip } from 'lucide-react';
import SecurityBadge from '../components/common/SecurityBadge';
import { emailService } from '../services/emailService';
import { useLayoutContext } from '../components/layout/Layout';
import './Inbox.css';

export const Starred = () => {
  const navigate = useNavigate();
  const { searchQuery } = useLayoutContext() || {};
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchStarred = async () => {
    setLoading(true);
    const data = await emailService.getEmails('starred');
    setEmails(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchStarred();
  }, []);

  const handleToggleStar = async (e, id) => {
    e.stopPropagation();
    await emailService.toggleStar(id);
    fetchStarred();
  };

  const filteredEmails = emails.filter((item) => {
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
      <div className="inbox-toolbar">
        <div className="toolbar-title">
          <Star size={20} className="text-warning fill-warning" />
          <h2>Starred Messages</h2>
          <span className="inbox-count-tag">{filteredEmails.length} Starred</span>
        </div>
      </div>

      <div className="inbox-table-card">
        {loading ? (
          <div className="inbox-state-box">Loading Starred Messages...</div>
        ) : filteredEmails.length === 0 ? (
          <div className="inbox-state-box">
            <Star size={40} className="text-muted" />
            <h3>No Starred Messages Found</h3>
            <p>No starred messages match your active search query.</p>
          </div>
        ) : (
          <div className="email-rows-list">
            {filteredEmails.map((email) => (
              <div 
                key={email.id} 
                className="email-row read"
                onClick={() => navigate(`/email/${email.id}`)}
              >
                <button 
                  className="btn-star starred"
                  onClick={(e) => handleToggleStar(e, email.id)}
                >
                  <Star size={16} fill="#f59e0b" />
                </button>

                <div className="email-sender-col">
                  <span className="sender-name">{email.sender}</span>
                  <span className="sender-email">{email.senderEmail}</span>
                </div>

                <div className="email-content-col">
                  <span className="email-subject">{email.subject}</span>
                  <span className="email-preview">— {email.preview}</span>
                </div>

                <div className="email-meta-col">
                  {email.hasAttachment && <Paperclip size={14} className="attachment-icon" />}
                  <SecurityBadge status={email.status} size="sm" />
                  <span className="email-date">{email.date}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Starred;
