import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Eye, Unlock, Trash2, Flag, AlertTriangle, ShieldAlert, Check } from 'lucide-react';
import SecurityBadge from '../components/common/SecurityBadge';
import { emailService } from '../services/emailService';
import { useLayoutContext } from '../components/layout/Layout';
import './Quarantine.css';

export const Quarantine = () => {
  const navigate = useNavigate();
  const { searchQuery, refreshCounts } = useLayoutContext() || {};
  const [quarantineItems, setQuarantineItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState('');

  const fetchQuarantine = async () => {
    setLoading(true);
    const data = await emailService.getQuarantineEmails();
    setQuarantineItems(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchQuarantine();
  }, []);

  const showNotification = (msg) => {
    setActionMessage(msg);
    setTimeout(() => setActionMessage(''), 3000);
  };

  const handleRelease = async (e, id) => {
    e.stopPropagation();
    await emailService.releaseQuarantine(id);
    showNotification('Email released from quarantine and delivered to Inbox as Warning');
    fetchQuarantine();
    if (refreshCounts) refreshCounts();
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    await emailService.deleteQuarantine(id);
    showNotification('Quarantined threat permanently purged from gateway store');
    fetchQuarantine();
    if (refreshCounts) refreshCounts();
  };

  const handleReport = async (e, id) => {
    e.stopPropagation();
    await emailService.reportPhishing(id);
    showNotification('Threat vector reported to MailTrace AI global risk engine');
    fetchQuarantine();
  };

  const filteredQuarantine = quarantineItems.filter((item) => {
    if (searchQuery && searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      return (
        item.sender.toLowerCase().includes(q) ||
        item.senderEmail.toLowerCase().includes(q) ||
        item.subject.toLowerCase().includes(q) ||
        (item.securityReasons && item.securityReasons.some(r => r.toLowerCase().includes(q)))
      );
    }
    return true;
  });

  return (
    <div className="quarantine-page">
      {/* Page Header */}
      <div className="quarantine-header-card">
        <div className="header-icon-box">
          <Lock size={26} className="text-danger" />
        </div>
        <div className="header-info">
          <h2>Security Quarantine Vault</h2>
          <p>
            Isolated threat barrier for emails blocked prior to mailbox delivery due to phishing indicators, SPF/DKIM failures, or malicious payloads.
          </p>
        </div>
        <div className="header-stat">
          <span className="stat-value">{filteredQuarantine.length}</span>
          <span className="stat-label">Active Holds</span>
        </div>
      </div>

      {/* Action Notification Toast */}
      {actionMessage && (
        <div className="quarantine-toast">
          <Check size={16} />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Quarantine Table */}
      <div className="quarantine-table-card">
        {loading ? (
          <div className="quarantine-loading">Evaluating Quarantine Isolation...</div>
        ) : filteredQuarantine.length === 0 ? (
          <div className="quarantine-empty-state">
            <ShieldAlert size={48} className="text-emerald" />
            <h3>No Quarantined Threats Found</h3>
            <p>No isolated threat items match your active search query.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="quarantine-table">
              <thead>
                <tr>
                  <th>Sender</th>
                  <th>Subject</th>
                  <th>Detection Reason</th>
                  <th>Risk Score</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredQuarantine.map((item) => (
                  <tr key={item.id} className="quarantine-row">
                    {/* Sender */}
                    <td>
                      <div className="cell-sender">
                        <span className="sender-title">{item.sender}</span>
                        <span className="sender-sub">{item.senderEmail}</span>
                      </div>
                    </td>

                    {/* Subject */}
                    <td>
                      <div className="cell-subject" title={item.subject}>
                        {item.subject}
                      </div>
                    </td>

                    {/* Primary Reason */}
                    <td>
                      <div className="cell-reason">
                        <AlertTriangle size={14} className="text-warning flex-shrink-0" />
                        <span>{item.securityReasons?.[0] || 'Phishing indicators detected'}</span>
                      </div>
                    </td>

                    {/* Risk Level */}
                    <td>
                      <div className="cell-risk">
                        <div className="risk-bar-track">
                          <div 
                            className="risk-bar-fill" 
                            style={{ 
                              width: `${(item.riskScore || 0.9) * 100}%`,
                              backgroundColor: item.riskScore > 0.8 ? '#ef4444' : '#f59e0b' 
                            }}
                          ></div>
                        </div>
                        <span className="risk-number">
                          {((item.riskScore || 0.9) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>

                    {/* Status Badge */}
                    <td>
                      <SecurityBadge status={item.status} size="sm" />
                    </td>

                    {/* Date */}
                    <td>
                      <span className="cell-date">{item.date}</span>
                    </td>

                    {/* Action Controls */}
                    <td>
                      <div className="action-buttons-group">
                        <button 
                          className="btn-action btn-view" 
                          onClick={() => navigate(`/email/${item.id}`)}
                          title="Inspect Details"
                        >
                          <Eye size={14} />
                          <span>View</span>
                        </button>

                        <button 
                          className="btn-action btn-release" 
                          onClick={(e) => handleRelease(e, item.id)}
                          title="Release to Inbox"
                        >
                          <Unlock size={14} />
                          <span>Release</span>
                        </button>

                        <button 
                          className="btn-action btn-delete" 
                          onClick={(e) => handleDelete(e, item.id)}
                          title="Purge Threat"
                        >
                          <Trash2 size={14} />
                          <span>Delete</span>
                        </button>

                        <button 
                          className="btn-action btn-report" 
                          onClick={(e) => handleReport(e, item.id)}
                          title="Report to AI Model"
                        >
                          <Flag size={14} />
                          <span>Report</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Quarantine;
