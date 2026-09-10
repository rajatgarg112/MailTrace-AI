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

export default function App() {
  const [activeNav, setActiveNav] = useState('inbox'); // inbox | quarantine | forensics
  const [inboxList, setInboxList] = useState([]);
  const [quarantineList, setQuarantineList] = useState([]);
  const [selectedMsg, setSelectedMsg] = useState(null);
  const [detailTab, setDetailTab] = useState('email'); // email | relay_map | forensics
  const [scenarios, setScenarios] = useState([]);
  
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

  // Fetch initial data from FastAPI backend
  const fetchMailbox = async () => {
    try {
      const [inboxRes, quarRes, scenRes] = await Promise.all([
        fetch('/api/mailbox/inbox').then(r => r.json()),
        fetch('/api/mailbox/quarantine').then(r => r.json()),
        fetch('/api/scenarios').then(r => r.json()),
      ]);

      setInboxList(inboxRes || []);
      setQuarantineList(quarRes || []);
      setScenarios(scenRes || []);

      if (!selectedMsg && inboxRes.length > 0) {
        setSelectedMsg(inboxRes[0]);
      }
    } catch (err) {
      console.error('Error fetching mailbox:', err);
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
      console.error('Error running custom scan:', err);
      setIsScanning(false);
    }
  };

  // Handle Release from Quarantine
  const handleReleaseQuarantine = async (msgId) => {
    try {
      await fetch(`/api/messages/${msgId}/release`, { method: 'POST' });
      fetchMailbox();
      if (selectedMsg && selectedMsg.id === msgId) {
        setSelectedMsg({
          ...selectedMsg,
          is_quarantined: false,
          delivery_action: 'DELIVER',
          policy_summary: 'Manually released from Quarantine by Administrator.'
        });
      }
    } catch (err) {
      console.error('Error releasing message:', err);
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

        {/* Content Split Grid */}
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
                  key={item.id}
                  className={`mail-card ${selectedMsg?.id === item.id ? 'selected' : ''}`}
                  onClick={() => setSelectedMsg(item)}
                >
                  <div className="mail-card-header">
                    <span className="sender-name">{item.sender}</span>
                    <span className="mail-time">
                      {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <div className="mail-subject">{item.subject}</div>

                  <div className="mail-meta-line">
                    {item.is_quarantined ? (
                      <span className="badge badge-danger">QUARANTINED</span>
                    ) : item.requires_warning ? (
                      <span className="badge badge-warn">WARN BADGE</span>
                    ) : (
                      <span className="badge badge-safe">SAFE</span>
                    )}

                    <span className="latency-tag">{item.latency_sec}s scan</span>
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
                      {selectedMsg.is_quarantined && (
                        <button
                          className="secondary-btn"
                          style={{ borderColor: 'var(--status-safe)', color: 'var(--status-safe)' }}
                          onClick={() => handleReleaseQuarantine(selectedMsg.id)}
                        >
                          <Unlock size={15} />
                          <span>Release to Inbox</span>
                        </button>
                      )}

                      <button className="secondary-btn" onClick={() => handleGenerateReport(selectedMsg.id)}>
                        <FileText size={15} color="var(--accent-cyan)" />
                        <span>BSA Certificate</span>
                      </button>
                    </div>
                  </div>

                  <div className="detail-sender-row">
                    <div className="sender-info">
                      <div className="avatar">
                        {selectedMsg.sender.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{selectedMsg.sender}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          To: {selectedMsg.recipient} • {new Date(selectedMsg.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Pre-Delivery Security Verdict Banner */}
                  <div className={`verdict-banner ${selectedMsg.delivery_action.toLowerCase()}`}>
                    <div className="verdict-text-group">
                      <div className="verdict-title">
                        {selectedMsg.is_quarantined ? (
                          <>
                            <XCircle size={20} color="var(--status-danger)" />
                            <span>GATEWAY VERDICT: QUARANTINED (Threat Score: {selectedMsg.threat_score}/100)</span>
                          </>
                        ) : selectedMsg.requires_warning ? (
                          <>
                            <AlertTriangle size={20} color="var(--status-warn)" />
                            <span>GATEWAY VERDICT: DELIVER WITH WARNING (Threat Score: {selectedMsg.threat_score}/100)</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle2 size={20} color="var(--status-safe)" />
                            <span>GATEWAY VERDICT: SAFE → DELIVERED TO INBOX (Threat Score: {selectedMsg.threat_score}/100)</span>
                          </>
                        )}
                      </div>
                      <div className="verdict-desc">{selectedMsg.policy_summary}</div>
                    </div>

                    <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                      Latency: <span style={{ color: 'var(--accent-cyan)' }}>{selectedMsg.latency_sec}s</span>
                    </div>
                  </div>
                </div>

                {/* Live Scan Timeline Visualizer */}
                <div className="timeline-card">
                  <div className="timeline-title">
                    <Activity size={16} color="var(--accent-cyan)" />
                    <span>Real-Time Gateway Pre-Delivery Scan Pipeline</span>
                  </div>

                  <div className="timeline-steps">
                    {selectedMsg.scan_timeline?.map((st, i) => (
                      <div key={i} className="timeline-step completed">
                        <span className="step-label">{st.step}</span>
                        <span className="step-time">{st.duration}</span>
                      </div>
                    ))}
                  </div>
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
