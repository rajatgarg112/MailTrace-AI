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
  PieChart
} from 'lucide-react';
import { emailService } from '../services/emailService';
import SecurityBadge from '../components/common/SecurityBadge';
import './SecurityDashboard.css';

export const SecurityDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

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
    return <div className="dashboard-loading">Calculating Dynamic Gateway Security Telemetry...</div>;
  }

  return (
    <div className="security-dashboard-page">
      {/* Dashboard Top Banner */}
      <div className="dashboard-header-card">
        <div className="header-left">
          <div className="header-badge">
            <Radio size={14} className="pulse-icon" />
            <span>MTA GATEWAY ONLINE • DYNAMIC TELEMETRY</span>
          </div>
          <h2>MailTrace AI Threat Operations Center</h2>
          <p>Real-time threat vector mitigation and dynamically computed email security telemetry.</p>
        </div>
        <div className="header-right">
          <div className="latency-box">
            <Clock size={16} className="text-cyan" />
            <div>
              <span className="latency-val">{metrics.avgScanLatencyMs} ms</span>
              <span className="latency-lbl">Avg Intercept Latency</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Dynamic Metric Cards Grid */}
      <div className="metrics-grid">
        {/* Card 1: Total Emails */}
        <div className="metric-card card-total">
          <div className="card-top">
            <span className="card-label">Total Emails</span>
            <Database size={20} className="card-icon text-cyan" />
          </div>
          <div className="card-value">{metrics.totalScanned}</div>
          <div className="card-footer">
            <span>Evaluated by gateway pipeline</span>
          </div>
        </div>

        {/* Card 2: Safe Emails */}
        <div className="metric-card card-safe">
          <div className="card-top">
            <span className="card-label">Safe Emails</span>
            <ShieldCheck size={20} className="card-icon text-emerald" />
          </div>
          <div className="card-value text-emerald">{metrics.safe}</div>
          <div className="card-footer">
            <span>{metrics.cleanRatePercentage}% clean delivery rate</span>
          </div>
        </div>

        {/* Card 3: Warning Emails */}
        <div className="metric-card card-warnings">
          <div className="card-top">
            <span className="card-label">Warning Emails</span>
            <AlertTriangle size={20} className="card-icon text-warning" />
          </div>
          <div className="card-value text-warning">{metrics.warnings}</div>
          <div className="card-footer">
            <span>Header & link warnings</span>
          </div>
        </div>

        {/* Card 4: Quarantined Emails */}
        <div className="metric-card card-quarantined">
          <div className="card-top">
            <span className="card-label">Quarantined Emails</span>
            <Lock size={20} className="card-icon text-danger" />
          </div>
          <div className="card-value text-danger">{metrics.quarantined}</div>
          <div className="card-footer">
            <span>Isolated threat holds</span>
          </div>
        </div>

        {/* Card 5: Rejected Emails */}
        <div className="metric-card card-rejected">
          <div className="card-top">
            <span className="card-label">Rejected Emails</span>
            <XCircle size={20} className="card-icon text-rose" />
          </div>
          <div className="card-value text-rose">{metrics.rejected}</div>
          <div className="card-footer">
            <span>Hard-blocked pre-delivery</span>
          </div>
        </div>

        {/* Card 6: Threats Detected */}
        <div className="metric-card card-threats">
          <div className="card-top">
            <span className="card-label">Threats Detected</span>
            <Zap size={20} className="card-icon text-purple" />
          </div>
          <div className="card-value text-purple">{metrics.threatsDetected}</div>
          <div className="card-footer">
            <span>Combined threat vectors</span>
          </div>
        </div>
      </div>

      {/* Security Overview Section: Dynamic Status Breakdown */}
      <div className="security-overview-card">
        <div className="card-title-bar">
          <PieChart size={18} className="text-cyan" />
          <h3>Security Status Overview & Percentage Breakdown</h3>
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

        {/* Distribution Breakdown Cards */}
        <div className="overview-distribution-grid">
          {metrics.statusDistribution.map((item) => (
            <div key={item.label} className="dist-item-box">
              <div className="dist-header">
                <span className="dist-dot" style={{ backgroundColor: item.color }}></span>
                <span className="dist-label">{item.label}</span>
              </div>
              <div className="dist-count">{item.count} emails</div>
              <div className="dist-percent">{item.percent.toFixed(1)}% of total</div>
            </div>
          ))}
        </div>
      </div>

      {/* Visual Charts & Live Event Stream Row */}
      <div className="dashboard-content-row">
        {/* Left: Custom CSS Distribution Visualizer */}
        <div className="chart-card">
          <div className="card-title-bar">
            <BarChart3 size={18} className="text-cyan" />
            <h3>7-Day Gateway Threat Distribution</h3>
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

        {/* Right: Live Dynamic Gateway Event Feed */}
        <div className="feed-card">
          <div className="card-title-bar">
            <Activity size={18} className="text-cyan" />
            <h3>Live Gateway Activity Feed</h3>
          </div>

          <div className="feed-list">
            {metrics.recentEmails.map((email) => (
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
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;
