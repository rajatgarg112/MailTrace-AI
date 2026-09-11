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
  ShieldAlert
} from 'lucide-react';
import { emailService } from '../services/emailService';
import SecurityBadge from '../components/common/SecurityBadge';
import './SecurityDashboard.css';

export const SecurityDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [feedFilter, setFeedFilter] = useState('ALL'); // ALL | SAFE | WARNING | QUARANTINED

  const fetchMetrics = async () => {
    setLoading(true);
    const data = await emailService.getSecurityMetrics();
    setMetrics(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading || !metrics) {
    return (
      <div className="dashboard-loading">
        <RefreshCw size={28} className="spin-icon text-cyan" />
        <span>Calculating Dynamic Gateway Security Telemetry...</span>
      </div>
    );
  }

  // Filter recent email feed
  const filteredFeed = metrics.recentEmails.filter((item) => {
    if (feedFilter === 'SAFE') return item.status === 'SAFE';
    if (feedFilter === 'WARNING') return item.status === 'WARNING';
    if (feedFilter === 'QUARANTINED') return item.status === 'QUARANTINED' || item.folder === 'quarantine';
    return true;
  });

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
          </div>
          <h2 className="dashboard-title">MailTrace AI Threat Operations Center</h2>
          <p className="dashboard-sub">
            Real-time pre-delivery threat vector interception, cryptographic RFC audit, and telemetry analytics.
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

          <button className="btn-live-refresh" onClick={fetchMetrics} title="Refresh Telemetry">
            <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
            <span>Live Refresh</span>
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
          <div className="card-value">{metrics.totalScanned}</div>
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
          <div className="card-value text-emerald">{metrics.safe}</div>
          <div className="card-footer">
            <span className="text-emerald">{metrics.cleanRatePercentage}% Clean</span> Delivered safely
          </div>
        </div>

        {/* Card 3: POLICY WARNINGS */}
        <div className="metric-card card-warnings">
          <div className="card-top">
            <span className="card-label">POLICY WARNINGS</span>
            <AlertTriangle size={20} className="card-icon text-warning" />
          </div>
          <div className="card-value text-warning">{metrics.warnings}</div>
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
          <div className="card-value text-danger">{metrics.quarantined}</div>
          <div className="card-footer">
            <span>Threat holds isolated</span>
          </div>
        </div>

        {/* Card 5: HARD BLOCKED */}
        <div className="metric-card card-rejected">
          <div className="card-top">
            <span className="card-label">HARD BLOCKED</span>
            <XCircle size={20} className="card-icon text-rose" />
          </div>
          <div className="card-value text-rose">{metrics.rejected}</div>
          <div className="card-footer">
            <span>Blocked pre-delivery</span>
          </div>
        </div>

        {/* Card 6: THREATS MITIGATED */}
        <div className="metric-card card-threats">
          <div className="card-top">
            <span className="card-label">THREATS MITIGATED</span>
            <Zap size={20} className="card-icon text-purple" />
          </div>
          <div className="card-value text-purple">{metrics.threatsDetected}</div>
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
          {metrics.statusDistribution.map((item) => (
            <div 
              key={item.label}
              className={`overview-progress-segment ${item.class}`}
              style={{ width: `${item.percent}%` }}
              title={`${item.label}: ${item.count} (${item.percent.toFixed(1)}%)`}
            ></div>
          ))}
        </div>

        {/* Distribution Breakdown Cards Grid */}
        <div className="overview-distribution-grid">
          {metrics.statusDistribution.map((item) => (
            <div key={item.label} className="dist-item-box">
              <div className="dist-header">
                <span className="dist-dot" style={{ backgroundColor: item.color }}></span>
                <span className="dist-label">{item.label}</span>
              </div>
              <div className="dist-count">{item.count}</div>
              <div className="dist-percent">{item.percent.toFixed(1)}% of total traffic</div>
            </div>
          ))}
        </div>
      </div>

      {/* Visual Charts & Live Event Stream Row (2 Columns) */}
      <div className="dashboard-content-row">
        {/* Left Column: 7-Day Threat Vector Histogram */}
        <div className="chart-card">
          <div className="card-title-bar">
            <div className="title-left">
              <BarChart3 size={18} className="text-vibrant-blue" />
              <h3>7-Day Threat Vector Histogram</h3>
            </div>
            <span className="rolling-pill">7D ROLLING</span>
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
                ALL
              </button>
              <button 
                className={`feed-filter-btn ${feedFilter === 'SAFE' ? 'active' : ''}`}
                onClick={() => setFeedFilter('SAFE')}
              >
                SAFE
              </button>
              <button 
                className={`feed-filter-btn ${feedFilter === 'WARNING' ? 'active' : ''}`}
                onClick={() => setFeedFilter('WARNING')}
              >
                WARNING
              </button>
              <button 
                className={`feed-filter-btn ${feedFilter === 'QUARANTINED' ? 'active' : ''}`}
                onClick={() => setFeedFilter('QUARANTINED')}
              >
                QUARANTINED
              </button>
            </div>
          </div>

          <div className="feed-list">
            {filteredFeed.length === 0 ? (
              <div className="empty-feed-text">No gateway events match active filter</div>
            ) : (
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
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;



