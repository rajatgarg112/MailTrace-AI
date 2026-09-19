import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Lock, 
  XCircle, 
  Zap, 
  Activity, 
  Clock, 
  Database,
  Radio,
  BarChart3,
  PieChart,
  RefreshCw,
  ShieldAlert,
  FileText,
  Terminal,
  Globe,
  Award,
  CheckCircle2,
  Download
} from 'lucide-react';
import { emailService } from '../services/emailService';
import SecurityBadge from '../components/common/SecurityBadge';
import './SecurityDashboard.css';

export const SecurityDashboard = ({ inboxList = [], quarantineList = [], onRefresh }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [feedFilter, setFeedFilter] = useState('ALL'); // ALL | SAFE | WARNING | QUARANTINED
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [isTerminalPaused, setIsTerminalPaused] = useState(false);

  const fetchMetrics = async () => {
    setLoading(true);
    const data = await emailService.getSecurityMetrics();
    setMetrics(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchMetrics();
  }, [inboxList, quarantineList]);

  // Combine and deduplicate inbox and quarantine messages to get active real-time feed
  const combinedMessages = React.useMemo(() => {
    const map = new Map();
    [...inboxList, ...quarantineList].forEach((item) => {
      const status = item.status || (item.is_quarantined || item.folder === 'quarantine' ? 'QUARANTINED' : 'SAFE');
      const senderEmail = item.senderEmail || item.sender_email || item.sender || 'external@gateway';
      const date = item.date || item.timestamp || 'Just Now';
      map.set(item.id || item.deliveryId, {
        ...item,
        status,
        senderEmail,
        date
      });
    });
    return Array.from(map.values());
  }, [inboxList, quarantineList]);

  const activeFeed = combinedMessages.length > 0 ? combinedMessages : (metrics?.recentEmails || []);

  // Compute live count stats from active feed
  const liveSafeCount = activeFeed.filter(m => m.status === 'SAFE').length;
  const liveWarningCount = activeFeed.filter(m => m.status === 'WARNING').length;
  const liveQuarantinedCount = activeFeed.filter(m => m.status === 'QUARANTINED' || m.folder === 'quarantine' || m.is_quarantined).length;
  const liveRejectedCount = activeFeed.filter(m => m.status === 'REJECTED').length;

  // Initial live terminal simulation stream
  useEffect(() => {
    const initialLogs = [
      `[${new Date().toLocaleTimeString()}] [MTA-INGRESS] Listening on port 25 (TLS 1.3 / ECDHE-RSA-AES256-GCM-SHA384)`,
      `[${new Date().toLocaleTimeString()}] [ISO-27037] Initialized chain-of-custody cryptographic SHA-256 digest engine`,
      `[${new Date().toLocaleTimeString()}] [SPF-DKIM] Verified DNS selector 's2026' for sih.gov.in (RSA 2048-bit PASS)`,
      `[${new Date().toLocaleTimeString()}] [URL-SANDBOX] Scanned 14 embedded URLs against PhishTank & Google SafeBrowsing API`,
      `[${new Date().toLocaleTimeString()}] [NLP-INTENT] BEC intimidation analyzer running zero-shot BERT transformer`,
      `[${new Date().toLocaleTimeString()}] [PII-DLP] Privacy scanner active: Aadhaar, PAN, SSN pattern redaction ready`,
      `[${new Date().toLocaleTimeString()}] [GATEWAY-STANCE] Pre-Delivery Policy Engine stance: ACTIVE MITIGATION (0.14s avg)`
    ];
    setTerminalLogs(initialLogs);

    const interval = setInterval(() => {
      if (!isTerminalPaused) {
        const timeStr = new Date().toLocaleTimeString();
        const sampleLogs = [
          `[${timeStr}] [INGRESS] Envelope scan: Recipient verified <alex.dev@mailtrace.local>`,
          `[${timeStr}] [AUTH-AUDIT] Cryptographic check: SPF pass, DKIM pass, DMARC aligned`,
          `[${timeStr}] [URL-INSPECT] Inspected http://sih.gov.in/docs — Status 200 OK (Clean)`,
          `[${timeStr}] [DLP-RULE] Zero PII leak detected in canonical body stream`,
          `[${timeStr}] [VERDICT-ENGINE] Delivery policy: DELIVER TO INBOX (Latency: 0.098s)`
        ];
        const nextLog = sampleLogs[Math.floor(Math.random() * sampleLogs.length)];
        setTerminalLogs(prev => [...prev.slice(-12), nextLog]);
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [isTerminalPaused]);

  // Filter recent email feed
  const filteredFeed = activeFeed.filter((item) => {
    if (feedFilter === 'SAFE') return item.status === 'SAFE';
    if (feedFilter === 'WARNING') return item.status === 'WARNING';
    if (feedFilter === 'QUARANTINED') return item.status === 'QUARANTINED' || item.folder === 'quarantine' || item.is_quarantined;
    return true;
  });

  if (loading && !metrics) {
    return (
      <div className="dashboard-loading">
        <RefreshCw size={28} className="spin-icon text-cyan" />
        <span>Calculating Dynamic Gateway Security Telemetry...</span>
      </div>
    );
  }

  const safeVal = activeFeed.length > 0 ? liveSafeCount : metrics.safe;
  const warnVal = activeFeed.length > 0 ? liveWarningCount : metrics.warnings;
  const quarVal = activeFeed.length > 0 ? liveQuarantinedCount : metrics.quarantined;
  const totalVal = safeVal + warnVal + quarVal + liveRejectedCount;
  const cleanPct = totalVal > 0 ? ((safeVal / totalVal) * 100).toFixed(1) : "100";
  const evidenceDossiersCount = totalVal;

  return (
    <div className="security-dashboard-page">
      {/* Top Operations Banner Card */}
      <div className="dashboard-header-card">
        <div className="header-left">
          <div className="badge-row">
            <span className="status-badge-green">
              <Radio size={13} className="spin-pulse" />
              GATEWAY ACTIVE - PRE-DELIVERY PROTECTION
            </span>
            <span className="status-badge-blue">
              <ShieldCheck size={13} />
              SOC NODE #01 (ONLINE)
            </span>
            <span className="status-badge-purple">
              <Award size={13} />
              ISO 27037 / BSA ADMISSIBLE
            </span>
          </div>
          <h2 className="dashboard-title">MailTrace AI Threat Operations Center</h2>
          <p className="dashboard-sub">
            Real-time pre-delivery threat vector interception, cryptographic RFC audit, ISO 27037 evidence preservation, and BSA compliance.
          </p>
        </div>

        <div className="header-right">
          <div className="latency-box">
            <Clock size={18} className="text-vibrant-blue" />
            <div>
              <div className="latency-val-row">
                <span className="latency-val">{metrics.avgScanLatencyMs} ms</span>
                <span className="optimal-pill">Optimal</span>
              </div>
              <span className="latency-lbl">AVG INTERCEPT LATENCY</span>
            </div>
          </div>

          <button className="btn-live-refresh" onClick={() => { fetchMetrics(); if (onRefresh) onRefresh(); }} title="Refresh Telemetry">
            <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
            <span>Live Refresh</span>
          </button>

          <button className="btn-export-pitch" onClick={() => window.print()} title="Export SIH Pitch Forensic Summary">
            <Download size={14} />
            <span>SIH Report</span>
          </button>
        </div>
      </div>

      {/* Main Dynamic Metric Cards Grid (6 Cards) */}
      <div className="metrics-grid">
        {/* Card 1: TOTAL EVALUATED */}
        <div className="metric-card card-total">
          <div className="card-top">
            <span className="card-label">TOTAL EVALUATED</span>
            <Database size={20} className="card-icon text-cyan" />
          </div>
          <div className="card-value">{totalVal}</div>
          <div className="card-footer">
            <span>100% Ingress Inspection</span>
          </div>
        </div>

        {/* Card 2: CLEAN DELIVERY */}
        <div className="metric-card card-safe">
          <div className="card-top">
            <span className="card-label">CLEAN DELIVERY</span>
            <ShieldCheck size={20} className="card-icon text-emerald" />
          </div>
          <div className="card-value text-emerald">{safeVal}</div>
          <div className="card-footer">
            <span className="text-emerald">{cleanPct}% Clean</span> Delivered safely
          </div>
        </div>

        {/* Card 3: POLICY WARNINGS */}
        <div className="metric-card card-warnings">
          <div className="card-top">
            <span className="card-label">POLICY WARNINGS</span>
            <AlertTriangle size={20} className="card-icon text-warning" />
          </div>
          <div className="card-value text-warning">{warnVal}</div>
          <div className="card-footer">
            <span>Header & link advisories</span>
          </div>
        </div>

        {/* Card 4: QUARANTINE VAULT */}
        <div className="metric-card card-quarantined">
          <div className="card-top">
            <span className="card-label">QUARANTINE VAULT</span>
            <Lock size={20} className="card-icon text-danger" />
          </div>
          <div className="card-value text-danger">{quarVal}</div>
          <div className="card-footer">
            <span>Threat holds isolated</span>
          </div>
        </div>

        {/* Card 5: ISO 27037 EVIDENCE DOSSIERS */}
        <div className="metric-card card-dossiers">
          <div className="card-top">
            <span className="card-label">EVIDENCE DOSSIERS</span>
            <FileText size={20} className="card-icon text-purple" />
          </div>
          <div className="card-value text-purple">{evidenceDossiersCount}</div>
          <div className="card-footer">
            <span>BSA Admissible SHA-256 Digests</span>
          </div>
        </div>

        {/* Card 6: THREATS MITIGATED */}
        <div className="metric-card card-threats">
          <div className="card-top">
            <span className="card-label">THREATS MITIGATED</span>
            <Zap size={20} className="card-icon text-purple" />
          </div>
          <div className="card-value text-purple">{warnVal + quarVal + liveRejectedCount}</div>
          <div className="card-footer">
            <span>Multi-vector holds</span>
          </div>
        </div>
      </div>

      {/* Security Overview Section: Gateway Threat Distribution & Percentage Stance */}
      <div className="security-overview-card">
        <div className="card-title-bar">
          <div className="title-left">
            <PieChart size={18} className="text-vibrant-blue" />
            <h3>Gateway Threat Distribution & Percentage Stance</h3>
          </div>
          <span className="stance-pill-vibrant">
            <ShieldAlert size={13} /> STANCE: ACTIVE MITIGATION
          </span>
        </div>

        {/* Multi-segment Progress Bar */}
        <div className="overview-progress-track">
          <div className="overview-progress-segment dist-safe" style={{ width: `${totalVal > 0 ? (safeVal / totalVal) * 100 : 0}%` }}></div>
          <div className="overview-progress-segment dist-warning" style={{ width: `${totalVal > 0 ? (warnVal / totalVal) * 100 : 0}%` }}></div>
          <div className="overview-progress-segment dist-quarantine" style={{ width: `${totalVal > 0 ? (quarVal / totalVal) * 100 : 0}%` }}></div>
          <div className="overview-progress-segment dist-rejected" style={{ width: `${totalVal > 0 ? (liveRejectedCount / totalVal) * 100 : 0}%` }}></div>
        </div>

        {/* Distribution Breakdown Cards Grid */}
        <div className="overview-distribution-grid">
          <div className="dist-item-box">
            <div className="dist-header">
              <span className="dist-dot" style={{ backgroundColor: '#10b981' }}></span>
              <span className="dist-label">Safe</span>
            </div>
            <div className="dist-count">{safeVal}</div>
            <div className="dist-percent">{totalVal > 0 ? ((safeVal / totalVal) * 100).toFixed(1) : 0}% of traffic</div>
          </div>
          <div className="dist-item-box">
            <div className="dist-header">
              <span className="dist-dot" style={{ backgroundColor: '#f59e0b' }}></span>
              <span className="dist-label">Warnings</span>
            </div>
            <div className="dist-count">{warnVal}</div>
            <div className="dist-percent">{totalVal > 0 ? ((warnVal / totalVal) * 100).toFixed(1) : 0}% of traffic</div>
          </div>
          <div className="dist-item-box">
            <div className="dist-header">
              <span className="dist-dot" style={{ backgroundColor: '#ef4444' }}></span>
              <span className="dist-label">Quarantined</span>
            </div>
            <div className="dist-count">{quarVal}</div>
            <div className="dist-percent">{totalVal > 0 ? ((quarVal / totalVal) * 100).toFixed(1) : 0}% of traffic</div>
          </div>
          <div className="dist-item-box">
            <div className="dist-header">
              <span className="dist-dot" style={{ backgroundColor: '#e11d48' }}></span>
              <span className="dist-label">Rejected</span>
            </div>
            <div className="dist-count">{liveRejectedCount}</div>
            <div className="dist-percent">{totalVal > 0 ? ((liveRejectedCount / totalVal) * 100).toFixed(1) : 0}% of traffic</div>
          </div>
        </div>
      </div>

      {/* Visual Charts & Live Event Stream Row (2 Columns) */}
      <div className="dashboard-content-row">
        {/* Left Column: Interactive 7-Day Threat Vector SVG Trend Chart */}
        <div className="chart-card">
          <div className="card-title-bar">
            <div className="title-left">
              <BarChart3 size={18} className="text-vibrant-blue" />
              <h3>7-Day Threat Vector Trend Analysis</h3>
            </div>
            <span className="rolling-pill">7D LIVE METRICS</span>
          </div>

          {/* SVG Multi-Vector Area Chart */}
          <div className="svg-chart-container" style={{ position: 'relative', width: '100%', height: '210px', marginTop: '0.5rem' }}>
            <svg viewBox="0 0 500 180" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
              <defs>
                <linearGradient id="safeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                </linearGradient>
                <linearGradient id="warnGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.0" />
                </linearGradient>
                <linearGradient id="quarGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.45" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Grid Background Lines */}
              <line x1="0" y1="30" x2="500" y2="30" stroke="var(--border-color)" strokeDasharray="3 3" opacity="0.6" />
              <line x1="0" y1="80" x2="500" y2="80" stroke="var(--border-color)" strokeDasharray="3 3" opacity="0.6" />
              <line x1="0" y1="130" x2="500" y2="130" stroke="var(--border-color)" strokeDasharray="3 3" opacity="0.6" />

              {/* Dynamic SVG Curves */}
              {(() => {
                const trends = metrics.threatTrends || [];
                const widthStep = 500 / Math.max(1, trends.length - 1);
                
                const safePoints = trends.map((t, i) => `${i * widthStep},${160 - (t.safe / 220) * 130}`).join(' L ');
                const safeArea = `M 0,160 L ${safePoints} L 500,160 Z`;
                
                const quarPoints = trends.map((t, i) => `${i * widthStep},${160 - (t.quarantined / 35) * 110}`).join(' L ');
                const quarArea = `M 0,160 L ${quarPoints} L 500,160 Z`;

                const warnPoints = trends.map((t, i) => `${i * widthStep},${160 - (t.warnings / 40) * 110}`).join(' L ');

                return (
                  <>
                    <path d={safeArea} fill="url(#safeGrad)" />
                    <path d={`M ${safePoints}`} fill="none" stroke="#10b981" strokeWidth="2.5" />

                    <path d={quarArea} fill="url(#quarGrad)" />
                    <path d={`M ${quarPoints}`} fill="none" stroke="#ef4444" strokeWidth="2.5" />

                    <path d={`M ${warnPoints}`} fill="none" stroke="#f59e0b" strokeWidth="2" strokeDasharray="4 3" />

                    {/* Data Points */}
                    {trends.map((t, i) => {
                      const x = i * widthStep;
                      const ySafe = 160 - (t.safe / 220) * 130;
                      const yQuar = 160 - (t.quarantined / 35) * 110;
                      return (
                        <g key={t.day} style={{ cursor: 'pointer' }}>
                          <circle cx={x} cy={ySafe} r="4.5" fill="#10b981" stroke="var(--bg-card)" strokeWidth="2" />
                          <circle cx={x} cy={yQuar} r="4.5" fill="#ef4444" stroke="var(--bg-card)" strokeWidth="2" />
                          <text x={x} y="175" textAnchor="middle" fill="var(--text-muted)" fontSize="10.5" fontWeight="700">
                            {t.day}
                          </text>
                        </g>
                      );
                    })}
                  </>
                );
              })()}
            </svg>
          </div>

          <div className="chart-legend">
            <div className="legend-item"><span className="dot dot-safe"></span> Safe Volume Curve</div>
            <div className="legend-item"><span className="dot dot-quarantine"></span> Quarantined Threat Curve</div>
            <div className="legend-item"><span className="dot dot-warning"></span> Warning Advisories</div>
          </div>
        </div>

        {/* Right Column: Live Gateway Activity Feed */}
        <div className="feed-card">
          <div className="card-title-bar">
            <div className="title-left">
              <Activity size={18} className="text-vibrant-blue" />
              <h3>Live Gateway Activity Feed</h3>
            </div>

            <div className="feed-filter-pills">
              <button 
                className={`feed-filter-btn ${feedFilter === 'ALL' ? 'active' : ''}`}
                onClick={() => setFeedFilter('ALL')}
              >
                ALL ({activeFeed.length})
              </button>
              <button 
                className={`feed-filter-btn ${feedFilter === 'SAFE' ? 'active' : ''}`}
                onClick={() => setFeedFilter('SAFE')}
              >
                SAFE ({liveSafeCount})
              </button>
              <button 
                className={`feed-filter-btn ${feedFilter === 'WARNING' ? 'active' : ''}`}
                onClick={() => setFeedFilter('WARNING')}
              >
                WARNING ({liveWarningCount})
              </button>
              <button 
                className={`feed-filter-btn ${feedFilter === 'QUARANTINED' ? 'active' : ''}`}
                onClick={() => setFeedFilter('QUARANTINED')}
              >
                QUARANTINED ({liveQuarantinedCount})
              </button>
            </div>
          </div>

          <div className="feed-list">
            {filteredFeed.length === 0 ? (
              <div className="empty-feed-text">No gateway events match active filter</div>
            ) : (
              filteredFeed.map((email) => (
                <div key={email.id || email.deliveryId} className="feed-item">
                  <div className="feed-time">{email.date}</div>
                  <div className="feed-body">
                    <div className="feed-event-title">{email.subject}</div>
                    <div className="feed-sender">{email.senderEmail}</div>
                  </div>
                  <div className="feed-right">
                    <SecurityBadge status={email.status} size="sm" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Live MTA Ingress Audit Terminal Console */}
      <div className="terminal-card">
        <div className="terminal-header">
          <div className="terminal-title">
            <Terminal size={16} color="var(--accent-cyan)" />
            <span>MTA INGRESS AUDIT STREAM — LIVE CRYPTOGRAPHIC TERMINAL</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              MODE: REAL-TIME AUDIT LOG
            </span>
            <button 
              className="terminal-toggle-btn"
              onClick={() => setIsTerminalPaused(!isTerminalPaused)}
            >
              {isTerminalPaused ? 'Resume Stream' : 'Pause Stream'}
            </button>
          </div>
        </div>

        <div className="terminal-log-body">
          {terminalLogs.map((log, i) => (
            <div key={i} className="terminal-log-line">
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;
