import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2 } from 'lucide-react';
import SecurityBadge from '../components/common/SecurityBadge';
import { emailService } from '../services/emailService';
import { useLayoutContext } from '../components/layout/Layout';
import './Inbox.css';

export const Trash = () => {
  const navigate = useNavigate();
  const { searchQuery } = useLayoutContext() || {};
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrash = async () => {
      setLoading(true);
      const data = await emailService.getEmails('trash');
      setEmails(data);
      setLoading(false);
    };
    fetchTrash();
  }, []);

  const filteredTrash = emails.filter((item) => {
    if (searchQuery && searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      return (
        item.sender.toLowerCase().includes(q) ||
        item.senderEmail.toLowerCase().includes(q) ||
        item.subject.toLowerCase().includes(q) ||
        item.preview.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="inbox-page">
      <div className="inbox-toolbar">
        <div className="toolbar-title">
          <Trash2 size={20} className="text-muted" />
          <h2>Trash Vault</h2>
          <span className="inbox-count-tag">{filteredTrash.length} Items</span>
        </div>
      </div>

      <div className="inbox-table-card">
        {loading ? (
          <div className="inbox-state-box">Loading Trash Items...</div>
        ) : filteredTrash.length === 0 ? (
          <div className="inbox-state-box">
            <Trash2 size={40} className="text-muted" />
            <h3>No Trash Items Found</h3>
            <p>No deleted emails match your search query.</p>
          </div>
        ) : (
          <div className="email-rows-list">
            {filteredTrash.map((email) => (
              <div 
                key={email.id} 
                className="email-row read"
                onClick={() => navigate(`/email/${email.id}`)}
              >
                <div className="email-sender-col">
                  <span className="sender-name">{email.sender}</span>
                  <span className="sender-email">{email.senderEmail}</span>
                </div>

                <div className="email-content-col">
                  <span className="email-subject">{email.subject}</span>
                  <span className="email-preview">— {email.preview}</span>
                </div>

                <div className="email-meta-col">
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

export default Trash;
