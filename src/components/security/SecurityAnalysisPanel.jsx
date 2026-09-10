import React from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Lock, 
  CheckCircle, 
  XCircle, 
  FileText, 
  Cpu, 
  Hash, 
  Percent, 
  Activity,
  Layers
} from 'lucide-react';
import SecurityBadge from '../common/SecurityBadge';
import './SecurityAnalysisPanel.css';

/**
 * Reusable Security Analysis Panel Component
 * Expects conceptually structured email/analysis object matching backend specs:
 * { status, riskScore, securityReasons, authentication, evidence, timing }
 */
export const SecurityAnalysisPanel = ({ email }) => {
  if (!email) return null;

  const status = (email.status || 'UNKNOWN').toUpperCase();
  const riskScore = email.riskScore !== null && email.riskScore !== undefined ? email.riskScore : 0.05;
  const riskPercentage = (riskScore * 100).toFixed(0);

  // Risk Classification Text & Class
  let riskCategory = 'Low Risk (Verified Clean)';
  let riskClass = 'risk-safe';
  if (riskScore >= 0.8) {
    riskCategory = 'Critical Threat (Phishing / Malicious)';
    riskClass = 'risk-critical';
  } else if (riskScore >= 0.5) {
    riskCategory = 'Medium Suspicion (Security Warning)';
    riskClass = 'risk-warning';
  }

  const authentication = email.authentication || { spf: 'PASS', dkim: 'PASS', dmarc: 'PASS', domainAlignment: 'MATCHED' };
  const securityReasons = email.securityReasons || [];
  const evidenceList = email.evidence || [];

  return (
    <div className={`security-analysis-panel panel-${status.toLowerCase()}`}>
      {/* Panel Header */}
      <div className="analysis-panel-header">
        <div className="header-left">
          <div className="panel-title-row">
            <Layers size={18} className="text-cyan" />
            <h3 className="panel-title">MailTrace Gateway Security Assessment</h3>
          </div>
          <p className="panel-subtitle">Pre-delivery zero-trust analysis telemetry & forensic evidence</p>
        </div>
        <div className="header-right">
          <SecurityBadge status={status} size="lg" />
        </div>
      </div>

      {/* Risk Score Gauge Bar */}
      <div className="risk-level-card">
        <div className="risk-header-row">
          <span className="risk-label">Computed Threat Score:</span>
          <span className={`risk-category-tag ${riskClass}`}>{riskCategory} ({riskPercentage}%)</span>
        </div>
        <div className="risk-track">
          <div 
            className={`risk-fill ${riskClass}`} 
            style={{ width: `${riskPercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Two Column Grid: Detection Reasons & Authentication Matrix */}
      <div className="analysis-details-grid">
        {/* Detection Reasons Checklist */}
        <div className="findings-card">
          <h4 className="card-section-title">
            <Activity size={15} className="text-cyan" />
            <span>Detection Reasons & Findings</span>
          </h4>
          <div className="reasons-list">
            {securityReasons.length === 0 ? (
              <div className="finding-check-item">
                <CheckCircle size={15} className="text-emerald" />
                <span>No security anomalies or risk indicators detected</span>
              </div>
            ) : (
              securityReasons.map((reason, idx) => {
                const isSafe = status === 'SAFE';
                const Icon = isSafe ? CheckCircle : status === 'WARNING' ? AlertTriangle : Lock;
                const iconColor = isSafe ? 'text-emerald' : status === 'WARNING' ? 'text-warning' : 'text-danger';
                return (
                  <div key={idx} className="finding-check-item">
                    <Icon size={15} className={`${iconColor} flex-shrink-0`} />
                    <span className="reason-text">{reason}</span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Authentication Matrix */}
        <div className="auth-matrix-card">
          <h4 className="card-section-title">
            <ShieldCheck size={15} className="text-emerald" />
            <span>Cryptographic Authentication</span>
          </h4>
          <div className="auth-spec-grid">
            <div className="auth-cell">
              <span className="cell-label">SPF Protocol</span>
              <span className={`cell-val val-${(authentication.spf || 'PASS').toLowerCase()}`}>
                {authentication.spf || 'PASS'}
              </span>
            </div>

            <div className="auth-cell">
              <span className="cell-label">DKIM Signature</span>
              <span className={`cell-val val-${(authentication.dkim || 'PASS').toLowerCase()}`}>
                {authentication.dkim || 'PASS'}
              </span>
            </div>

            <div className="auth-cell">
              <span className="cell-label">DMARC Policy</span>
              <span className={`cell-val val-${(authentication.dmarc || 'PASS').toLowerCase()}`}>
                {authentication.dmarc || 'PASS'}
              </span>
            </div>

            <div className="auth-cell">
              <span className="cell-label">Domain Alignment</span>
              <span className={`cell-val val-${(authentication.domainAlignment || 'MATCHED').toLowerCase()}`}>
                {authentication.domainAlignment || 'MATCHED'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Evidence Vault Table */}
      {evidenceList.length > 0 && (
        <div className="evidence-vault-card">
          <h4 className="card-section-title">
            <FileText size={15} className="text-purple" />
            <span>Security Evidence & SHA-256 Hashes</span>
          </h4>
          
          <div className="evidence-table-wrapper">
            <table className="evidence-table">
              <thead>
                <tr>
                  <th>Finding ID</th>
                  <th>Evidence Type</th>
                  <th>Explanation</th>
                  <th>Confidence</th>
                  <th>Analyzer Engine</th>
                  <th>SHA-256 Hash</th>
                </tr>
              </thead>
              <tbody>
                {evidenceList.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <span className="evidence-id">{item.id}</span>
                    </td>
                    <td>
                      <span className="evidence-type-pill">{item.type}</span>
                    </td>
                    <td className="explanation-text">{item.explanation}</td>
                    <td>
                      <span className="confidence-badge">
                        <Percent size={11} />
                        {(item.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td>
                      <span className="analyzer-tag">
                        <Cpu size={12} />
                        {item.analyzer}
                      </span>
                    </td>
                    <td>
                      <span className="hash-code" title={item.sha256}>
                        <Hash size={11} />
                        {item.sha256 ? `${item.sha256.slice(0, 12)}...` : 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityAnalysisPanel;
