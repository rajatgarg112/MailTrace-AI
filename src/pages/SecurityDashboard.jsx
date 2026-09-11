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
  Sliders,
  Shield,
  CheckCircle2,
  Filter,
  ArrowUpRight,
  Cpu
} from 'lucide-react';
import { emailService } from '../services/emailService';
import SecurityBadge from '../components/common/SecurityBadge';
import './SecurityDashboard.css';

export const SecurityDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [feedFilter, setFeedFilter] = useState('ALL'); // ALL | SAFE | WARNING | QUARANTINED

  const fetchMetrics = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    else setLoading(true);

    const data = await emailService.getSecurityMetrics();
    setMetrics(data);

    if (isManual) {
      setTimeout(() => setRefreshing(false), 400);
    } else {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading || !metrics) {
    return (
      <div className="dashboard-loading">
        <RefreshCw size={28} className="spin text-cyan" />
        <span>Initializing MailTrace AI SOC Command Telemetry...</span>
      </div>
    );
  }

  const filteredFeed = metrics.recentEmails.filter((email) => {
    if (feedFilter === 'ALL') return true;
    return email.status === feedFilter;
  });

  return (
    <div className="security-dashboard-page">
      {/* Cyber SOC Top Header Banner */}
      <div className="dashboard-header-card">
        <div className="header-glow-bg"></div>
        <div className="header-left">
          <div className="header-badge-row">
            <div className="header-badge">
              <Radio size={13} className="pulse-icon" />
              <span>GATEWAY ACTIVE • PRE-DELIVERY PROTECTION</span>
            </div>
            <div className="header-badge badge-soc">
              <Cpu size={12} color="#06b6d4" />
              <span>SOC NODE #01 (ONLINE)</span>
            </div>
          </div>

          <h2 className="header-title">
            MailTrace AI <span className="title-highlight">Threat Operations Center</span>
          </h2>
          <p className="header-desc">
            Real-time pre-delivery threat vector interception, cryptographic RFC audit, and telemetry analytics.
          </p>
        </div>

        <div className="header-right">
          <div className="latency-box">
            <Clock size={18} className="text-cyan pulse" />
            <div>
              <div className="latency-val-group">
                <span className="latency-val">{metrics.avgScanLatencyMs} ms</span>
                <span className="latency-trend"><ArrowUpRight size={12} /> Optimal</span>
              </div>
              <span className="latency-lbl">Avg Intercept Latency</span>
            </div>
          </div>

          <button 
            className={`refresh-btn ${refreshing ? 'spinning' : ''}`}
            onClick={() => fetchMetrics(true)}
            title="Refresh Telemetry Data"
          >
            <RefreshCw size={15} className={refreshing ? 'spin' : ''} />
            <span>{refreshing ? 'Syncing...' : 'Live Refresh'}</span>
          </button>
        </div>
      </div>

      {/* Main Metric Cyber Cards Grid */}
      <div className="metrics-grid">
        {/* Card 1: Total Scanned */}
        <div className="metric-card card-total">
          <div className="card-top">
            <span className="card-label">Total Evaluated</span>
            <div className="icon-wrapper cyan">
              <Database size={18} />
            </div>
          </div>
          <div className="card-value">{metrics.totalScanned}</div>
          <div className="card-footer">
            <CheckCircle2 size={13} className="text-cyan" />
            <span>100% Ingress Inspection</span>
          </div>
        </div>

        {/* Card 2: Safe Emails */}
        <div className="metric-card card-safe">
          <div className="card-top">
            <span className="card-label">Clean Delivery</span>
            <div className="icon-wrapper emerald">
              <ShieldCheck size={18} />
            </div>
          </div>
          <div className="card-value text-emerald">{metrics.safe}</div>
          <div className="card-footer">
            <span className="rate-badge text-emerald">{metrics.cleanRatePercentage}% Clean</span>
            <span>Delivered safely</span>
          </div>
        </div>

        {/* Card 3: Warning Emails */}
        <div className="metric-card card-warnings">
          <div className="card-top">
            <span className="card-label">Policy Warnings</span>
            <div className="icon-wrapper amber">
              <AlertTriangle size={18} />
            </div>
          </div>
          <div className="card-value text-warning">{metrics.warnings}</div>
          <div className="card-footer">
            <span>Header & link advisories</span>
          </div>
        </div>

        {/* Card 4: Quarantined Emails */}
        <div className="metric-card card-quarantined">
          <div className="card-top">
            <span className="card-label">Quarantine Vault</span>
            <div className="icon-wrapper crimson">
              <Lock size={18} />
            </div>
          </div>
          <div className="card-value text-danger">{metrics.quarantined}</div>
          <div className="card-footer">
            <span>Threat holds isolated</span>
          </div>
        </div>

        {/* Card 5: Hard Rejected */}
        <div className="metric-card card-rejected">
          <div className="card-top">
            <span className="card-label">Hard Blocked</span>
            <div className="icon-wrapper rose">
              <XCircle size={18} />
            </div>
          </div>
          <div className="card-value text-rose">{metrics.rejected}</div>
          <div className="card-footer">
            <span>Blocked pre-delivery</span>
          </div>
        </div>

        {/* Card 6: Threats Neutralized */}
        <div className="metric-card card-threats">
          <div className="card-top">
            <span className="card-label">Threats Mitigated</span>
            <div className="icon-wrapper purple">
              <Zap size={18} />
            </div>
          </div>
          <div className="card-value text-purple">{metrics.threatsDetected}</div>
          <div className="card-footer">
            <span>Multi-vector holds</span>
          </div>
        </div>
      </div>

      {/* Security Status Overview Section */}
      <div className="security-overview-card">
        <div className="card-title-bar">
          <div className="title-group">
            <PieChart size={18} className="text-cyan" />
            <h3>Gateway Threat Distribution & Percentage Stance</h3>
          </div>
          <div className="status-pill-active">
            <span className="dot-pulse"></span>
            <span>STANCE: ACTIVE MITIGATION</span>
          </div>
        </div>

        {/* Multi-segment Neon Progress Track */}
        <div className="overview-progress-track">
          {metrics.statusDistribution.map((item) => (
            <div 
              key={item.label}
              className={`overview-progress-segment ${item.class}`}
              style={{ width: `${Math.max(item.percent, 3)}%` }}
              title={`${item.label}: ${item.count} messages (${item.percent.toFixed(1)}%)`}
            ></div>
          ))}
        </div>

        {/* Breakdown Items */}
        <div className="overview-distribution-grid">
          {metrics.statusDistribution.map((item) => (
            <div key={item.label} className="dist-item-box">
              <div className="dist-header">
                <span className="dist-dot" style={{ backgroundColor: item.color, boxShadow: `0 0 10px ${item.color}` }}></span>
                <span className="dist-label">{item.label}</span>
              </div>
              <div className="dist-count">{item.count}</div>
              <div className="dist-percent">{item.percent.toFixed(1)}% of total traffic</div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts & Activity Stream Dual Grid */}
      <div className="dashboard-content-row">
        {/* Left: 7-Day Histogram */}
        <div className="chart-card">
          <div className="card-title-bar">
            <div className="title-group">
              <BarChart3 size={18} className="text-cyan" />
              <h3>7-Day Threat Vector Histogram</h3>
            </div>
            <span className="tag-mono">7D ROLLING</span>
          </div>

          <div className="chart-bars-container">
            {metrics.threatTrends.map((trend) => (
              <div key={trend.day} className="chart-bar-group">
                <div className="bar-stacked">
                  <div 
                    className="bar-segment bar-safe" 
                    style={{ height: `${(trend.safe / 220) * 100}%` }}
                    title={`Safe: ${trend.safe}`}
                  ></div>
                  <div 
                    className="bar-segment bar-warning" 
                    style={{ height: `${(trend.warnings / 220) * 100}%` }}
                    title={`Warnings: ${trend.warnings}`}
                  ></div>
                  <div 
                    className="bar-segment bar-quarantine" 
                    style={{ height: `${(trend.quarantined / 220) * 100}%` }}
                    title={`Quarantined: ${trend.quarantined}`}
                  ></div>
                </div>
                <span className="chart-day-label">{trend.day}</span>
              </div>
            ))}
          </div>

          <div className="chart-legend">
            <div className="legend-item"><span className="dot dot-safe"></span> Verified Safe</div>
            <div className="legend-item"><span className="dot dot-warning"></span> Warnings</div>
            <div className="legend-item"><span className="dot dot-quarantine"></span> Quarantined</div>
          </div>
        </div>

        {/* Right: Live Gateway Feed */}
        <div className="feed-card">
          <div className="card-title-bar">
            <div className="title-group">
              <Activity size={18} className="text-cyan pulse" />
              <h3>Live Gateway Activity Feed</h3>
            </div>

            {/* Quick Feed Filters */}
            <div className="feed-filter-group">
              <Filter size={13} className="text-dim" />
              {['ALL', 'SAFE', 'WARNING', 'QUARANTINED'].map((f) => (
                <button
                  key={f}
                  className={`feed-filter-btn ${feedFilter === f ? 'active' : ''}`}
                  onClick={() => setFeedFilter(f)}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="feed-list">
            {filteredFeed.length > 0 ? (
              filteredFeed.map((email) => (
                <div key={email.id} className="feed-item">
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
            ) : (
              <div className="feed-empty">No activity events matching "{feedFilter}" filter.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;
