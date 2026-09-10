import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Star, 
  Paperclip, 
  Download, 
  Unlock, 
  AlertCircle,
  Network,
  FileCheck
} from 'lucide-react';
import SecurityBadge from '../components/common/SecurityBadge';
import SecurityAnalysisPanel from '../components/security/SecurityAnalysisPanel';
import { emailService } from '../services/emailService';
import './EmailView.css';

export const EmailView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [email, setEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isStarred, setIsStarred] = useState(false);
  const [activeTab, setActiveTab] = useState('BODY'); // BODY | ANALYSIS | RELAY

  useEffect(() => {
    const fetchEmail = async () => {
      setLoading(true);
      const data = await emailService.getEmailById(id);
      if (data) {
        setEmail(data);
        setIsStarred(data.isStarred);
      }
      setLoading(false);
    };
    fetchEmail();
  }, [id]);

  const handleToggleStar = async () => {
    if (!email) return;
    const updated = await emailService.toggleStar(email.id);
    setIsStarred(updated.isStarred);
  };

  const handleRelease = async () => {
    if (!email) return;
    await emailService.releaseQuarantine(email.id);
    navigate('/inbox');
  };

  if (loading) {
    return <div className="email-view-loading">Decrypting Gateway Telemetry & Email Content...</div>;
  }

  if (!email) {
    return (
      <div className="email-view-not-found">
        <AlertCircle size={48} className="text-danger" />
        <h3>Email Not Found</h3>
        <p>The requested message ID does not exist or has been purged from the gateway store.</p>
        <button className="btn-back" onClick={() => navigate(-1)}>
          <ArrowLeft size={16} /> Back to Mailbox
        </button>
      </div>
    );
  }

  const sha256Hash = `${email.id.toUpperCase()}8F9A2B4C6D8E0F1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F`;

  return (
    <div className="email-view-page">
      {/* Top Action Toolbar */}
      <div className="email-view-toolbar">
        <button className="btn-back-nav" onClick={() => navigate(-1)}>
          <ArrowLeft size={18} />
          <span>Back</span>
        </button>

        <div className="toolbar-right-actions">
          <button 
            className={`btn-toolbar-star ${isStarred ? 'starred' : ''}`}
            onClick={handleToggleStar}
            title={isStarred ? 'Unstar' : 'Star'}
          >
            <Star size={18} fill={isStarred ? '#f59e0b' : 'none'} />
          </button>

          {email.status === 'QUARANTINED' && (
            <button className="btn-release-inline" onClick={handleRelease}>
              <Unlock size={16} />
              <span>Release to Inbox</span>
            </button>
          )}

          <SecurityBadge status={email.status} size="md" />
        </div>
      </div>

      {/* Reusable Security Analysis Component Embedded */}
      <SecurityAnalysisPanel email={email} />

      {/* Email Header Card */}
      <div className="email-header-card">
        <h1 className="email-view-subject">{email.subject}</h1>

        <div className="email-metadata-grid">
          <div className="meta-left">
            <div className="sender-avatar-large">
              {email.sender.charAt(0)}
            </div>
            <div className="sender-full-details">
              <div className="sender-name-row">
                <span className="sender-name-text">{email.sender}</span>
                <span className="sender-email-text">&lt;{email.senderEmail}&gt;</span>
              </div>
              <div className="recipient-row">
                <span>To: <strong>{email.recipient}</strong></span>
              </div>
            </div>
          </div>

          <div className="meta-right">
            <span className="email-timestamp-text">{new Date(email.timestamp).toLocaleString()}</span>
            <span className="delivery-id-tag">Delivery ID: {email.deliveryId}</span>
          </div>
        </div>
      </div>

      {/* Navigation View Tabs */}
      <div className="email-view-tabs">
        <button 
          className={`tab-btn ${activeTab === 'BODY' ? 'active' : ''}`}
          onClick={() => setActiveTab('BODY')}
        >
          <FileCheck size={15} />
          <span>Email Content</span>
        </button>
        <button 
          className={`tab-btn ${activeTab === 'RELAY' ? 'active' : ''}`}
          onClick={() => setActiveTab('RELAY')}
        >
          <Network size={15} />
          <span>MTA Relay Telemetry</span>
        </button>
      </div>

      {/* Tab 1: Email Body & Attachments */}
      {activeTab === 'BODY' && (
        <>
          {email.attachments && email.attachments.length > 0 && (
            <div className="email-attachments-card">
              <div className="attachments-title">
                <Paperclip size={16} />
                <span>Payload Attachments ({email.attachments.length})</span>
              </div>
              <div className="attachments-grid">
                {email.attachments.map((att, idx) => (
                  <div key={idx} className={`attachment-box ${!att.isClean ? 'att-malicious' : ''}`}>
                    <div className="att-info">
                      <span className="att-name">{att.name}</span>
                      <span className="att-size">{att.size} • {att.isClean ? 'Static Scan: Clean' : 'Malware Payload'}</span>
                    </div>
                    <button className="btn-download-att" disabled={!att.isClean}>
                      <Download size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="email-body-card">
            <div className="email-body-text">
              {email.body.split('\n').map((paragraph, i) => (
                <p key={i}>{paragraph}</p>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Tab 2: MTA Relay Telemetry */}
      {activeTab === 'RELAY' && (
        <div className="email-relay-card">
          <h3>Pre-Delivery Gateway Intercept Trail</h3>
          <div className="relay-step">
            <div className="step-num">Hop 1</div>
            <div className="step-body">
              <strong>Source Ingress:</strong> {email.senderEmail}
              <div className="text-muted">Originating IP: 198.51.100.44 • Handshake: TLS 1.3</div>
            </div>
            <span className="step-time">0 ms</span>
          </div>

          <div className="relay-step">
            <div className="step-num">Hop 2</div>
            <div className="step-body">
              <strong>MailTrace Pre-Delivery Gateway Intercept</strong>
              <div className="text-muted">Analyzers: SPF, DKIM, DMARC, Deep NLP Phishing Scanner</div>
            </div>
            <span className="step-time">+{email.timing?.scanLatencyMs || 145} ms</span>
          </div>

          <div className="relay-step">
            <div className="step-num">Hop 3</div>
            <div className="step-body">
              <strong>Gateway Decision:</strong> <SecurityBadge status={email.status} size="sm" />
              <div className="text-muted">SHA-256 Digest: {sha256Hash.slice(0, 32)}...</div>
            </div>
            <span className="step-time">+{email.timing?.totalLatencyMs || 198} ms</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailView;
