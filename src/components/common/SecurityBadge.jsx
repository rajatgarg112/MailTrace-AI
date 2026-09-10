import React from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Lock, 
  XCircle, 
  AlertOctagon, 
  HelpCircle, 
  RefreshCw 
} from 'lucide-react';
import './SecurityBadge.css';

/**
 * Reusable Security Status Badge Component
 * @param {string} status - SAFE | WARNING | QUARANTINED | REJECTED | FAILED | UNKNOWN | SCANNING
 * @param {string} size - 'sm' | 'md' | 'lg'
 * @param {boolean} showIcon - whether to display status icon
 */
export const SecurityBadge = ({ status = 'UNKNOWN', size = 'md', showIcon = true }) => {
  const normalizedStatus = (status || 'UNKNOWN').toUpperCase();

  const statusConfig = {
    SAFE: {
      label: 'Verified / Safe',
      shortLabel: 'SAFE',
      icon: ShieldCheck,
      badgeClass: 'badge-safe'
    },
    WARNING: {
      label: 'Security Warning',
      shortLabel: 'WARNING',
      icon: AlertTriangle,
      badgeClass: 'badge-warning'
    },
    QUARANTINED: {
      label: 'Quarantined',
      shortLabel: 'QUARANTINED',
      icon: Lock,
      badgeClass: 'badge-quarantined'
    },
    REJECTED: {
      label: 'Rejected',
      shortLabel: 'REJECTED',
      icon: XCircle,
      badgeClass: 'badge-rejected'
    },
    FAILED: {
      label: 'Delivery Failed',
      shortLabel: 'FAILED',
      icon: AlertOctagon,
      badgeClass: 'badge-failed'
    },
    UNKNOWN: {
      label: 'Under Review',
      shortLabel: 'UNKNOWN',
      icon: HelpCircle,
      badgeClass: 'badge-unknown'
    },
    SCANNING: {
      label: 'Scanning...',
      shortLabel: 'SCANNING',
      icon: RefreshCw,
      badgeClass: 'badge-scanning'
    }
  };

  const config = statusConfig[normalizedStatus] || statusConfig.UNKNOWN;
  const IconComponent = config.icon;

  return (
    <span 
      className={`security-badge ${config.badgeClass} badge-${size}`} 
      title={`MailTrace Security Status: ${config.label}`}
    >
      {showIcon && (
        <IconComponent 
          className={`badge-icon ${normalizedStatus === 'SCANNING' ? 'spin-icon' : ''}`} 
          size={size === 'sm' ? 13 : size === 'lg' ? 18 : 15} 
        />
      )}
      <span className="badge-text">{size === 'sm' ? config.shortLabel : config.label}</span>
    </span>
  );
};

export default SecurityBadge;
