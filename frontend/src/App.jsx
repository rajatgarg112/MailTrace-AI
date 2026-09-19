import React, { useState, useEffect } from 'react';
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  Inbox,
  AlertTriangle,
  Send,
  FileText,
  Search,
  Zap,
  CheckCircle2,
  XCircle,
  Activity,
  Server,
  Lock,
  Clock,
  Eye,
  Download,
  X,
  Play,
  FileCode,
  ArrowRight,
  RefreshCw,
  Unlock,
  AlertOctagon,
  Globe,
  Paperclip,
  Check
} from 'lucide-react';

import SecurityDashboard from '../../src/pages/SecurityDashboard';
import { emailService } from '../../src/services/emailService';

export default function App() {
  const [activeNav, setActiveNav] = useState('inbox'); // inbox | quarantine | forensics | dashboard
  const [inboxList, setInboxList] = useState([]);
  const [quarantineList, setQuarantineList] = useState([]);
  const [selectedMsg, setSelectedMsg] = useState(null);
  const [detailTab, setDetailTab] = useState('email'); // email | relay_map | forensics
  const [selectedPipelineStep, setSelectedPipelineStep] = useState(null);
  const [scenarios, setScenarios] = useState([]);

  // Helper to calculate stage status for selected message
  const getStepStatus = (stepIndex, msg) => {
    if (!msg) return { badge: 'PASSED', color: 'var(--status-safe)' };
    if (stepIndex === 2 && (msg.header_forensics?.is_spoofed_domain || msg.header_forensics?.domain_mismatch)) {
      return { badge: 'ANOMALY DETECTED', color: 'var(--status-warn)' };
    }
    if (stepIndex === 3 && (msg.authentication?.spf_status === 'FAIL' || msg.authentication?.dkim_status === 'FAIL')) {
      return { badge: 'AUTH FAILED', color: 'var(--status-danger)' };
    }
    if (stepIndex === 4 && (msg.url_analysis?.malicious_urls > 0 || msg.url_analysis?.url_risk_score > 30)) {
      return { badge: 'PHISHING DETECTED', color: 'var(--status-danger)' };
    }
    if (stepIndex === 5 && (msg.attachment_analysis?.malicious_count > 0 || msg.hasAttachment === false)) {
      return msg.hasAttachment ? { badge: 'MALWARE FLAG', color: 'var(--status-danger)' } : { badge: 'NO PAYLOAD', color: 'var(--text-muted)' };
    }
    if (stepIndex === 6 && (msg.nlp_threat?.urgency_score > 40 || msg.nlp_threat?.is_impersonation)) {
      return { badge: 'BEC INTENT', color: 'var(--status-warn)' };
    }
    if (stepIndex === 7 && msg.pii?.pii_detected) {
      return { badge: 'PII REDACTED', color: 'var(--accent-purple)' };
    }
    if (stepIndex === 8) {
      return {
        badge: msg.is_quarantined ? 'ISOLATED' : msg.requires_warning ? 'WARNED' : 'DELIVERED',
        color: msg.is_quarantined ? 'var(--status-danger)' : msg.requires_warning ? 'var(--status-warn)' : 'var(--status-safe)'
      };
    }
    return { badge: 'VERIFIED PASS', color: 'var(--status-safe)' };
  };
  
  // Modals
  const [showScenarioModal, setShowScenarioModal] = useState(false);
  const [showCustomModal, setShowCustomModal] = useState(false);
  const [reportModal, setReportModal] = useState(null);

  // Custom Email Input Form
  const [customSender, setCustomSender] = useState('sender@example.com');
  const [customSubject, setCustomSubject] = useState('Urgent Account Update Required');
  const [customRawEmail, setCustomRawEmail] = useState(
    "From: Support Team <support@nic-portal-update.xyz>\n" +
    "Subject: Urgent Password Expiration & Verification\n" +
    "Authentication-Results: spf=fail; dkim=fail\n\n" +
    "Your email account will be suspended within 2 hours. Log in immediately at http://198.51.100.99/login-nic to re-verify."
  );

  // Scanning Progress Overlay
  const [isScanning, setIsScanning] = useState(false);
  const [scanningProgress, setScanningProgress] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch initial data from FastAPI backend with emailService fallback
  const fetchMailbox = async () => {
    try {
      const [inboxRes, quarRes, scenRes] = await Promise.all([
        fetch('/api/mailbox/inbox').then(r => r.ok ? r.json() : null),
        fetch('/api/mailbox/quarantine').then(r => r.ok ? r.json() : null),
        fetch('/api/scenarios').then(r => r.ok ? r.json() : null),
      ]);

      if (inboxRes && quarRes) {
        setInboxList(inboxRes || []);
        setQuarantineList(quarRes || []);
        setScenarios(scenRes || []);
        if (!selectedMsg && inboxRes.length > 0) {
          setSelectedMsg(inboxRes[0]);
        }
      } else {
        throw new Error('API response empty');
      }
    } catch (err) {
      // Fallback to in-memory emailService
      const mockInbox = await emailService.getEmails('inbox');
      const mockQuarantine = await emailService.getQuarantineEmails();
      setInboxList(mockInbox);
      setQuarantineList(mockQuarantine);
      if (!selectedMsg && mockInbox.length > 0) {
        setSelectedMsg(mockInbox[0]);
      }
    }
  };

  useEffect(() => {
    fetchMailbox();
  }, []);

  // Handle Delivery Simulation with Scan Progress Animation
  const handleSimulateScenario = async (scenarioId) => {
    setShowScenarioModal(false);
    setIsScanning(true);
    setScanningProgress(15);

    const timer1 = setTimeout(() => setScanningProgress(50), 300);
    const timer2 = setTimeout(() => setScanningProgress(85), 650);

    try {
      const res = await fetch('/api/deliveries/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scenarioId }),
      });
      const data = await res.json();

      setScanningProgress(100);
      setTimeout(() => {
        setIsScanning(false);
        fetchMailbox();
        setSelectedMsg(data);
        if (data.is_quarantined) {
          setActiveNav('quarantine');
        } else {
          setActiveNav('inbox');
        }
      }, 400);
    } catch (err) {
      console.error('Error simulating delivery:', err);
      setIsScanning(false);
    }
  };

  // Handle Custom Email Simulation
  const handleCustomSimulate = async () => {
    setShowCustomModal(false);
    setIsScanning(true);
    setScanningProgress(20);

    setTimeout(() => setScanningProgress(65), 350);

    try {
      const res = await fetch('/api/deliveries/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: customSender,
          subject: customSubject,
          raw_email: customRawEmail,
        }),
      });
      if (!res.ok) throw new Error('API simulation failed');
      const data = await res.json();

      setScanningProgress(100);
      setTimeout(async () => {
        setIsScanning(false);
        await fetchMailbox();
        setSelectedMsg(data);
        if (data.is_quarantined) {
          setActiveNav('quarantine');
        } else {
          setActiveNav('inbox');
        }
      }, 400);
    } catch (err) {
      // Fallback to emailService send simulation
      const newEmail = await emailService.sendEmail({
        recipient: 'alex.dev@mailtrace.local',
        subject: customSubject,
        body: customRawEmail,
      });
      setScanningProgress(100);
      setTimeout(async () => {
        setIsScanning(false);
        await fetchMailbox();
        setSelectedMsg(newEmail);
        if (newEmail.status === 'QUARANTINED' || newEmail.folder === 'quarantine') {
          setActiveNav('quarantine');
        } else {
          setActiveNav('inbox');
        }
      }, 400);
    }
  };

  // Handle Release from Quarantine
  const handleReleaseQuarantine = async (msgId) => {
    try {
      const res = await fetch(`/api/messages/${msgId}/release`, { method: 'POST' });
      if (!res.ok) throw new Error('API release failed');
      await fetchMailbox();
    } catch (err) {
      await emailService.releaseQuarantine(msgId);
      await fetchMailbox();
    }
    if (selectedMsg && (selectedMsg.id === msgId || selectedMsg.deliveryId === msgId)) {
      setSelectedMsg({
        ...selectedMsg,
        status: 'SAFE',
        folder: 'inbox',
        is_quarantined: false,
        delivery_action: 'DELIVER',
        policy_summary: 'Manually released from Quarantine by Administrator.'
      });
    }
  };

  // Generate BSA Forensic Report
  const handleGenerateReport = async (msgId) => {
    try {
      const res = await fetch(`/api/messages/${msgId}/report`, { method: 'POST' });
      const report = await res.json();
      setReportModal(report);
    } catch (err) {
      console.error('Error generating report:', err);
    }
  };

  const currentList = activeNav === 'quarantine' ? quarantineList : inboxList;
  const filteredList = currentList.filter(
    (m) =>
      m.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.sender.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand-header">
          <div className="brand-logo">
            <Shield size={24} />
          </div>
          <div>
            <div className="brand-title">MailTrace AI</div>
            <div className="brand-subtitle">Security Gateway</div>
          </div>
        </div>

        <nav className="nav-menu">
          <div
            className={`nav-item ${activeNav === 'inbox' ? 'active' : ''}`}
            onClick={() => setActiveNav('inbox')}
          >
            <div className="nav-icon-group">
              <Inbox size={19} />
              <span>Delivered Inbox</span>
            </div>
            <span className="badge badge-safe">{inboxList.length}</span>
          </div>

          <div
            className={`nav-item ${activeNav === 'quarantine' ? 'active' : ''}`}
            onClick={() => setActiveNav('quarantine')}
          >
            <div className="nav-icon-group">
              <AlertOctagon size={19} />
              <span>Quarantine Vault</span>
            </div>
            <span className="badge badge-danger">{quarantineList.length}</span>
          </div>

          <div
            className={`nav-item ${activeNav === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveNav('dashboard')}
          >
            <div className="nav-icon-group">
              <ShieldCheck size={19} color="var(--accent-cyan)" />
              <span>Security Dashboard</span>
            </div>
            <span className="badge badge-cyan">SOC Live</span>
          </div>

          <div
            className={`nav-item ${activeNav === 'forensics' ? 'active' : ''}`}
            onClick={() => setActiveNav('forensics')}
          >
            <div className="nav-icon-group">
              <Activity size={19} />
              <span>Forensics & Audit</span>
            </div>
          </div>
        </nav>

        {/* Gateway Health Indicator Widget */}
        <div className="gateway-card">
          <div className="gateway-status-line">
            <div className="pulse-dot"></div>
            <span>Pre-Delivery Gateway Active</span>
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            Target Latency: <strong style={{ color: 'var(--accent-cyan)' }}>1–3s</strong>
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            Compliance: <strong style={{ color: 'var(--status-safe)' }}>ISO 27037 / BSA</strong>
          </div>
        </div>
      </aside>

      {/* Main Workspace Area */}
      <main className="main-wrapper">
        {/* Top Header Bar */}
        <header className="top-bar">
          <div className="search-box">
            <Search size={17} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search sender, subject, threat rule, IP..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="btn-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', marginRight: '0.5rem' }}>
              <Zap size={16} color="var(--accent-cyan)" />
              <span style={{ color: 'var(--text-muted)' }}>SLA Metric:</span>
              <span className="badge badge-cyan">1.18s Avg</span>
            </div>

            <button className="secondary-btn" onClick={() => setShowCustomModal(true)}>
              <FileCode size={16} color="var(--accent-cyan)" />
              <span>Test Custom Email</span>
            </button>

            <button className="action-btn" onClick={() => setShowScenarioModal(true)}>
              <Play size={16} />
              <span>Send Demo Scenario</span>
            </button>
          </div>
        </header>

        {/* Live Delivery Scanning Animation Overlay Bar */}
        {isScanning && (
          <div
            style={{
              backgroundColor: 'var(--bg-panel)',
              borderBottom: '1px solid var(--accent-cyan)',
              padding: '0.85rem 1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <RefreshCw size={19} className="spin" color="var(--accent-cyan)" />
              <span style={{ fontSize: '0.92rem', fontWeight: 600 }}>
                MailTrace Gateway running parallel pre-delivery threat analysis...
              </span>
            </div>
            <div style={{ width: '220px', backgroundColor: 'var(--bg-dark)', borderRadius: '6px', overflow: 'hidden', height: '8px' }}>
              <div
                style={{
                  width: `${scanningProgress}%`,
                  height: '100%',
                  backgroundColor: 'var(--accent-cyan)',
                  transition: 'width 0.3s ease',
                }}
              ></div>
            </div>
          </div>
        )}

        {/* Content View */}
        {activeNav === 'dashboard' ? (
          <div style={{ flexGrow: 1, overflowY: 'auto' }}>
            <SecurityDashboard inboxList={inboxList} quarantineList={quarantineList} onRefresh={fetchMailbox} />
          </div>
        ) : (
          <div className="content-grid">
          {/* Email List View Column */}
          <section className="mail-list-panel">
            <div className="list-header">
              <span className="list-title">
                {activeNav === 'quarantine' ? 'Quarantined Threat Store' : 'Delivered Mailbox'}
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                {filteredList.length} messages
              </span>
            </div>

            <div className="mail-items-container">
              {filteredList.map((item) => (
                <div
                  key={item.id || item.deliveryId}
                  className={`mail-card ${selectedMsg?.id === item.id ? 'selected' : ''}`}
                  onClick={() => setSelectedMsg(item)}
                >
                  <div className="mail-card-header">
                    <span className="sender-name">{item.sender || 'Sender'}</span>
                    <span className="mail-time">
                      {item.date || (item.timestamp && !isNaN(new Date(item.timestamp)) ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '11:45 AM')}
                    </span>
                  </div>

                  <div className="mail-subject">{item.subject}</div>

                  <div className="mail-meta-line">
                    {item.is_quarantined || item.status === 'QUARANTINED' || item.folder === 'quarantine' ? (
                      <span className="badge badge-danger">QUARANTINED</span>
                    ) : item.requires_warning || item.status === 'WARNING' ? (
                      <span className="badge badge-warn">WARN</span>
                    ) : (
                      <span className="badge badge-safe">SAFE</span>
                    )}

                    <span className="latency-tag">{item.latency_sec ? `${item.latency_sec}s` : item.timing?.scanLatencyMs ? `${item.timing.scanLatencyMs}ms` : '142ms'}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Detailed Message & Security Audit Viewer Pane */}
          <section className="mail-detail-panel">
            {selectedMsg ? (
              <>
                <div className="detail-header">
                  <div className="detail-subject-row">
                    <h2 className="detail-subject">{selectedMsg.subject}</h2>

                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                      {(selectedMsg.is_quarantined || selectedMsg.status === 'QUARANTINED' || selectedMsg.folder === 'quarantine') && (
                        <button
                          className="secondary-btn"
                          style={{ borderColor: 'var(--status-safe)', color: 'var(--status-safe)' }}
                          onClick={() => handleReleaseQuarantine(selectedMsg.id || selectedMsg.deliveryId)}
                        >
                          <Unlock size={15} />
                          <span>Release to Inbox</span>
                        </button>
                      )}

                      <button className="secondary-btn" onClick={() => handleGenerateReport(selectedMsg.id || selectedMsg.deliveryId)}>
                        <FileText size={15} color="var(--accent-cyan)" />
                        <span>BSA Certificate</span>
                      </button>
                    </div>
                  </div>

                  <div className="detail-sender-row">
                    <div className="sender-info">
                      <div className="avatar">
                        {(selectedMsg.sender || 'M').charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{selectedMsg.sender || selectedMsg.senderEmail}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          To: {selectedMsg.recipient || 'alex.dev@mailtrace.local'} • {selectedMsg.date || 'Today'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Pre-Delivery Security Verdict Banner */}
                  <div className={`verdict-banner ${(selectedMsg.delivery_action || selectedMsg.status || 'DELIVER').toLowerCase()}`}>
                    <div className="verdict-text-group">
                      <div className="verdict-title">
                        {selectedMsg.is_quarantined || selectedMsg.status === 'QUARANTINED' || selectedMsg.folder === 'quarantine' ? (
                          <>
                            <XCircle size={20} color="var(--status-danger)" />
                            <span>GATEWAY VERDICT: QUARANTINED (Threat Score: {selectedMsg.threat_score || Math.round((selectedMsg.riskScore || 0.88) * 100)}/100)</span>
                          </>
                        ) : selectedMsg.requires_warning || selectedMsg.status === 'WARNING' ? (
                          <>
                            <AlertTriangle size={20} color="var(--status-warn)" />
                            <span>GATEWAY VERDICT: DELIVER WITH WARNING (Threat Score: {selectedMsg.threat_score || Math.round((selectedMsg.riskScore || 0.45) * 100)}/100)</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle2 size={20} color="var(--status-safe)" />
                            <span>GATEWAY VERDICT: SAFE → DELIVERED TO INBOX (Threat Score: {selectedMsg.threat_score || Math.round((selectedMsg.riskScore || 0.04) * 100)}/100)</span>
                          </>
                        )}
                      </div>
                      <div className="verdict-desc">{selectedMsg.policy_summary || selectedMsg.securityReasons?.[0] || 'Envelope & payload verified clean pre-delivery.'}</div>
                    </div>

                    <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                      Latency: <span style={{ color: 'var(--accent-cyan)' }}>{selectedMsg.latency_sec ? `${selectedMsg.latency_sec}s` : selectedMsg.timing?.scanLatencyMs ? `${selectedMsg.timing.scanLatencyMs}ms` : '142ms'}</span>
                    </div>
                  </div>

                  {/* Advanced Multi-Vector Threat Risk Score Matrix */}
                  <div style={{ marginTop: '0.85rem', padding: '0.85rem 1rem', background: 'var(--bg-panel)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                    <div style={{ fontSize: '0.76rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.65rem' }}>
                      COMPOSITE MULTI-VECTOR RISK MATRIX BREAKDOWN
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
                      <div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '3px' }}>Header & Relay</div>
                        <div style={{ height: '6px', background: 'var(--bg-dark)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${Math.min(100, selectedMsg.header_forensics?.anomaly_score || 0)}%`, height: '100%', background: 'var(--status-warn)' }}></div>
                        </div>
                        <div style={{ fontSize: '0.72rem', fontWeight: 700, marginTop: '2px', color: 'var(--text-main)' }}>{selectedMsg.header_forensics?.anomaly_score || 0}/100</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '3px' }}>Auth Alignment</div>
                        <div style={{ height: '6px', background: 'var(--bg-dark)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${Math.max(0, 100 - (selectedMsg.authentication?.overall_auth_score || 100))}%`, height: '100%', background: 'var(--accent-cyan)' }}></div>
                        </div>
                        <div style={{ fontSize: '0.72rem', fontWeight: 700, marginTop: '2px', color: 'var(--text-main)' }}>{selectedMsg.authentication?.spf_status === 'PASS' ? '0/100 (Pass)' : '80/100 (Fail)'}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '3px' }}>URL Phishing</div>
                        <div style={{ height: '6px', background: 'var(--bg-dark)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${Math.min(100, selectedMsg.url_analysis?.url_risk_score || (selectedMsg.status === 'QUARANTINED' ? 85 : 0))}%`, height: '100%', background: 'var(--status-danger)' }}></div>
                        </div>
                        <div style={{ fontSize: '0.72rem', fontWeight: 700, marginTop: '2px', color: 'var(--text-main)' }}>{selectedMsg.url_analysis?.url_risk_score || (selectedMsg.status === 'QUARANTINED' ? 85 : 0)}/100</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '3px' }}>NLP BEC Urgency</div>
                        <div style={{ height: '6px', background: 'var(--bg-dark)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${Math.min(100, selectedMsg.nlp_threat?.urgency_score || (selectedMsg.status === 'WARNING' ? 60 : 10))}%`, height: '100%', background: 'var(--status-warn)' }}></div>
                        </div>
                        <div style={{ fontSize: '0.72rem', fontWeight: 700, marginTop: '2px', color: 'var(--text-main)' }}>{selectedMsg.nlp_threat?.urgency_score || (selectedMsg.status === 'WARNING' ? 60 : 10)}/100</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Interactive Real-Time Gateway Pre-Delivery Scan Pipeline */}
                <div className="timeline-card">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                    <div className="timeline-title" style={{ margin: 0 }}>
                      <Activity size={16} color="var(--accent-cyan)" />
                      <span>REAL-TIME GATEWAY PRE-DELIVERY SCAN PIPELINE</span>
                    </div>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                      Inline Zero-Trust Inspection Gate (Click step to inspect)
                    </span>
                  </div>

                  <div style={{ fontSize: '0.8rem', color: 'var(--text-sub)', marginBottom: '0.9rem', lineHeight: '1.4', background: 'var(--bg-panel)', padding: '0.6rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <strong>Architecture Purpose:</strong> Unlike legacy mailboxes that scan post-delivery, MailTrace AI acts as an inline MTA Security Gateway. Incoming emails are held in memory while 9 parallel inspection layers evaluate headers, authentication, links, payloads, and BEC intent before allowing inbox delivery.
                  </div>

                  <div className="timeline-steps">
                    {selectedMsg.scan_timeline?.map((st, i) => {
                      const statusInfo = getStepStatus(i, selectedMsg);
                      const isSelected = selectedPipelineStep === i;
                      return (
                        <div
                          key={i}
                          className={`timeline-step ${isSelected ? 'selected-step' : ''}`}
                          onClick={() => setSelectedPipelineStep(isSelected ? null : i)}
                          style={{ cursor: 'pointer', borderColor: isSelected ? 'var(--accent-cyan)' : undefined }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <span className="step-time">{st.duration}</span>
                            <span style={{ fontSize: '0.66rem', fontWeight: 800, color: statusInfo.color }}>
                              {statusInfo.badge}
                            </span>
                          </div>
                          <span className="step-label">{st.step}</span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Expanded Inspector Drawer for Selected Pipeline Step */}
                  {selectedPipelineStep !== null && selectedMsg.scan_timeline?.[selectedPipelineStep] && (
                    <div style={{ marginTop: '0.85rem', padding: '0.85rem', background: 'var(--bg-panel)', borderRadius: '8px', border: '1px solid var(--accent-cyan)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                        <strong style={{ fontSize: '0.86rem', color: 'var(--text-main)' }}>
                          Stage #{selectedPipelineStep + 1} Diagnostic Finding: {selectedMsg.scan_timeline[selectedPipelineStep].step}
                        </strong>
                        <X size={14} cursor="pointer" onClick={() => setSelectedPipelineStep(null)} />
                      </div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                        {selectedPipelineStep === 0 && "Canonicalized raw MIME headers and calculated standardized email body representation."}
                        {selectedPipelineStep === 1 && `Computed ISO 27037 compliant SHA-256 cryptographic digest: ${selectedMsg.evidence_sha256}`}
                        {selectedPipelineStep === 2 && `Analyzed ${selectedMsg.header_forensics?.total_hops || 2} header relay hops. Originating IP: ${selectedMsg.header_forensics?.originating_ip || '198.51.100.25'}`}
                        {selectedPipelineStep === 3 && `Authentication audit: SPF ${selectedMsg.authentication?.spf_status}, DKIM ${selectedMsg.authentication?.dkim_status}, DMARC ${selectedMsg.authentication?.dmarc_status}`}
                        {selectedPipelineStep === 4 && `URL inspection found ${selectedMsg.url_analysis?.total_urls || 0} links (${selectedMsg.url_analysis?.malicious_urls || 0} malicious)`}
                        {selectedPipelineStep === 5 && `Payload analysis checked ${selectedMsg.attachments?.length || 0} attachments for PE headers and macros.`}
                        {selectedPipelineStep === 6 && `NLP BEC engine evaluated urgency score (${selectedMsg.nlp_threat?.urgency_score || 0}/100) and executive titles.`}
                        {selectedPipelineStep === 7 && `PII Privacy DLP scan: ${selectedMsg.pii?.pii_detected ? 'Sensitive PII detected and masked' : 'Zero PII leak detected'}`}
                        {selectedPipelineStep === 8 && `Final verdict calculated: ${selectedMsg.delivery_action} (Threat Score: ${selectedMsg.threat_score}/100)`}
                      </div>
                    </div>
                  )}
                </div>

                {/* Navigation Tabs */}
                <div className="tab-row">
                  <button
                    className={`tab-button ${detailTab === 'email' ? 'active' : ''}`}
                    onClick={() => setDetailTab('email')}
                  >
                    📧 Email Message
                  </button>
                  <button
                    className={`tab-button ${detailTab === 'relay_map' ? 'active' : ''}`}
                    onClick={() => setDetailTab('relay_map')}
                  >
                    🌐 Route & Relay Map
                  </button>
                  <button
                    className={`tab-button ${detailTab === 'forensics' ? 'active' : ''}`}
                    onClick={() => setDetailTab('forensics')}
                  >
                    🛡️ Security & Forensics Audit
                  </button>
                </div>

                {/* Tab 1: Email Body Reader */}
                {detailTab === 'email' && (
                  <div className="detail-body-container">
                    {selectedMsg.body}
                  </div>
                )}

                {/* Tab 2: Visual Route & Relay Map */}
                {detailTab === 'relay_map' && (
                  <div className="forensics-grid">
                    <div className="forensics-card">
                      <div className="card-title">
                        <span>Header Hop Route & Origin Node Mapping</span>
                        <span style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)' }}>
                          Origin IP: {selectedMsg.header_forensics?.originating_ip || '198.51.100.25'}
                        </span>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
                        {selectedMsg.header_forensics?.relay_chain?.map((hop) => (
                          <div
                            key={hop.hop_number}
                            style={{
                              backgroundColor: 'var(--bg-dark)',
                              border: '1px solid var(--border-color)',
                              borderRadius: '10px',
                              padding: '1rem',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                              <div
                                style={{
                                  width: '32px',
                                  height: '32px',
                                  borderRadius: '8px',
                                  backgroundColor: 'rgba(6, 182, 212, 0.15)',
                                  color: 'var(--accent-cyan)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  fontWeight: '800',
                                  fontFamily: 'var(--font-mono)'
                                }}
                              >
                                #{hop.hop_number}
                              </div>
                              <div>
                                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>From: {hop.from_host || 'Direct Ingress'}</div>
                                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>By: {hop.by_host || 'MailTrace Node'}</div>
                              </div>
                            </div>

                            <div style={{ textAlign: 'right' }}>
                              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--accent-cyan)' }}>
                                {hop.ip_address || 'Internal Interface'}
                              </div>
                              <span className={`badge ${hop.is_private_ip ? 'badge-safe' : 'badge-danger'}`} style={{ marginTop: '0.2rem', display: 'inline-block' }}>
                                {hop.is_private_ip ? 'Internal / LAN' : 'Public Origin Node'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Tab 3: Forensics & Header Audit */}
                {detailTab === 'forensics' && (
                  <div className="forensics-grid">
                    {/* Auth Status Card */}
                    <div className="forensics-card">
                      <div className="card-title">
                        <span>Cryptographic Authentication (SPF / DKIM / DMARC)</span>
                        <span style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)' }}>
                          Auth Score: {selectedMsg.authentication?.overall_auth_score}/100
                        </span>
                      </div>

                      <div className="auth-badge-group">
                        <div className="auth-chip">
                          SPF: <strong style={{ color: selectedMsg.authentication?.spf_status === 'PASS' ? 'var(--status-safe)' : 'var(--status-danger)' }}>{selectedMsg.authentication?.spf_status}</strong>
                        </div>
                        <div className="auth-chip">
                          DKIM: <strong style={{ color: selectedMsg.authentication?.dkim_status === 'PASS' ? 'var(--status-safe)' : 'var(--status-danger)' }}>{selectedMsg.authentication?.dkim_status}</strong>
                        </div>
                        <div className="auth-chip">
                          DMARC: <strong style={{ color: selectedMsg.authentication?.dmarc_status === 'PASS' ? 'var(--status-safe)' : 'var(--status-danger)' }}>{selectedMsg.authentication?.dmarc_status}</strong>
                        </div>
                      </div>
                    </div>

                    {/* URL & Attachment Findings */}
                    <div className="forensics-card">
                      <div className="card-title">
                        <span>Deep Threat Vectors (URL Phishing & Attachment Inspection)</span>
                      </div>

                      {selectedMsg.url_analysis?.findings?.map((f, idx) => (
                        <div key={idx} style={{ fontSize: '0.82rem', color: 'var(--status-warn)' }}>
                          • {f}
                        </div>
                      ))}

                      {selectedMsg.attachment_analysis?.findings?.map((f, idx) => (
                        <div key={idx} style={{ fontSize: '0.82rem', color: 'var(--status-danger)' }}>
                          • {f}
                        </div>
                      ))}
                    </div>

                    {/* Cryptographic Evidence & ISO 27037 Digest */}
                    <div className="forensics-card">
                      <div className="card-title">
                        <span>ISO/IEC 27037 Cryptographic Evidence Digest</span>
                        <span style={{ fontSize: '0.8rem', color: 'var(--status-safe)' }}>BSA Admissible</span>
                      </div>

                      <div className="hash-box">
                        SHA-256 Digest: {selectedMsg.evidence_sha256}
                      </div>

                      {selectedMsg.rule_triggers?.length > 0 && (
                        <div>
                          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--status-danger)', marginBottom: '0.4rem' }}>
                            Engine Policy Triggers:
                          </div>
                          <ul style={{ paddingLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                            {selectedMsg.rule_triggers.map((trig, idx) => (
                              <li key={idx}>{trig}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-dim)' }}>
                Select an email from the list to inspect pre-delivery security status and audit details.
              </div>
            )}
          </section>
        </div>
        )}
      </main>

      {/* Scenario Trigger Modal */}
      {showScenarioModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <div className="modal-title">Select Gateway Test Scenario</div>
              <X size={20} cursor="pointer" onClick={() => setShowScenarioModal(false)} />
            </div>

            <div className="scenario-list">
              {scenarios.map((scen) => (
                <div
                  key={scen.id}
                  className="scenario-item"
                  onClick={() => handleSimulateScenario(scen.id)}
                >
                  <div className="scenario-name">{scen.title}</div>
                  <div className="scenario-sub">From: {scen.sender}</div>
                  <div className="scenario-sub" style={{ fontStyle: 'italic', marginTop: '0.2rem' }}>
                    "{scen.subject}"
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Custom Email Tester Modal */}
      {showCustomModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ width: '620px' }}>
            <div className="modal-header">
              <div className="modal-title">Test Custom Ingress Email</div>
              <X size={20} cursor="pointer" onClick={() => setShowCustomModal(false)} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>
                  Sender Display Name & Email:
                </label>
                <input
                  type="text"
                  style={{
                    width: '100%',
                    backgroundColor: 'var(--bg-dark)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.65rem',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem',
                    outline: 'none',
                  }}
                  value={customSender}
                  onChange={(e) => setCustomSender(e.target.value)}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>
                  Subject Line:
                </label>
                <input
                  type="text"
                  style={{
                    width: '100%',
                    backgroundColor: 'var(--bg-dark)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.65rem',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem',
                    outline: 'none',
                  }}
                  value={customSubject}
                  onChange={(e) => setCustomSubject(e.target.value)}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>
                  Raw Email String / Headers & Body:
                </label>
                <textarea
                  rows={7}
                  style={{
                    width: '100%',
                    backgroundColor: 'var(--bg-dark)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.65rem',
                    color: 'var(--text-main)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.82rem',
                    outline: 'none',
                  }}
                  value={customRawEmail}
                  onChange={(e) => setCustomRawEmail(e.target.value)}
                />
              </div>

              <button className="action-btn" style={{ justifyContent: 'center', marginTop: '0.5rem' }} onClick={handleCustomSimulate}>
                <Play size={16} />
                <span>Run Gateway Pre-Delivery Scan</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* BSA Forensic Report Certificate Modal */}
      {reportModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ width: '680px' }}>
            <div className="modal-header">
              <div className="modal-title">Digital Evidence Certificate ({reportModal.report_id})</div>
              <X size={20} cursor="pointer" onClick={() => setReportModal(null)} />
            </div>

            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div><strong>Standard:</strong> {reportModal.compliance_standard}</div>
              <div><strong>Generated At:</strong> {new Date(reportModal.generated_at).toLocaleString()}</div>
              <div><strong>Subject:</strong> {reportModal.subject}</div>
              <div><strong>Sender:</strong> {reportModal.sender}</div>
              <div>
                <strong>Verdict:</strong>{' '}
                <strong style={{ color: reportModal.verdict === 'QUARANTINE' ? 'var(--status-danger)' : 'var(--status-safe)' }}>
                  {reportModal.verdict}
                </strong>
              </div>

              <div className="hash-box" style={{ marginTop: '0.5rem' }}>
                SHA-256 Digest: {reportModal.evidence_sha256}
              </div>

              <div style={{ background: 'var(--bg-dark)', padding: '0.85rem', borderRadius: '8px', fontSize: '0.8rem', color: 'var(--text-main)', marginTop: '0.5rem', lineHeight: '1.5' }}>
                {reportModal.chain_of_custody}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
