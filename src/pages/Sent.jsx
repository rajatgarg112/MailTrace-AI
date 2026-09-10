import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Clock } from 'lucide-react';
import SecurityBadge from '../components/common/SecurityBadge';
import { emailService } from '../services/emailService';
import { useLayoutContext } from '../components/layout/Layout';
import './Sent.css';

export const Sent = () => {
  const navigate = useNavigate();
  const { searchQuery } = useLayoutContext() || {};
  const [sentEmails, setSentEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSent = async () => {
      setLoading(true);
      const data = await emailService.getEmails('sent');
      setSentEmails(data);
      setLoading(false);
    };
    fetchSent();
  }, []);

  const filteredSent = sentEmails.filter((item) => {
    if (searchQuery && searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      return (
        item.recipient.toLowerCase().includes(q) ||
        item.subject.toLowerCase().includes(q) ||
        item.preview.toLowerCase().includes(q) ||
        item.status.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="sent-page">
      <div className="page-header">
        <div className="header-title">
          <Send size={22} className="text-cyan" />
          <h2>Sent Mail</h2>
          <span className="count-badge">{filteredSent.length} Outbound Transactions</span>
        </div>
      </div>

      <div className="sent-table-card">
        {loading ? (
          <div className="sent-loading">Loading Sent Mail Log...</div>
        ) : filteredSent.length === 0 ? (
          <div className="sent-empty">
            <Send size={40} className="text-muted" />
            <h3>No Sent Emails Found</h3>
            <p>No outbound messages match your search query.</p>
          </div>
        ) : (
          <div className="email-rows-list">
            {filteredSent.map((email) => (
              <div 
                key={email.id}
                className="sent-row"
                onClick={() => navigate(`/email/${email.id}`)}
              >
                <div className="recipient-col">
                  <span className="recipient-prefix">To:</span>
                  <span className="recipient-text">{email.recipient}</span>
                </div>

                <div className="subject-col">
                  <span className="subject-text">{email.subject}</span>
                  <span className="preview-text">— {email.preview}</span>
                </div>

                <div className="status-col">
                  <SecurityBadge status={email.status} size="sm" />
                  
                  {email.timing?.totalLatencyMs && (
                    <span className="latency-chip" title="Total delivery latency">
                      <Clock size={12} />
                      {email.timing.totalLatencyMs}ms
                    </span>
                  )}

                  <span className="sent-date">{email.date}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sent;
