// MailTrace AI — Email & Gateway Service Layer
// Serves mock dataset with in-memory state management. Easily replaceable by REST API endpoints.

import { INITIAL_MOCK_EMAILS, MOCK_SECURITY_METRICS } from '../data/mockEmails';

let emailsState = [...INITIAL_MOCK_EMAILS];

export const emailService = {
  // Fetch emails by folder (inbox, sent, drafts, starred, quarantine, trash)
  async getEmails(folder = 'inbox') {
    await new Promise((resolve) => setTimeout(resolve, 60));
    
    if (folder === 'starred') {
      return emailsState.filter((item) => item.isStarred && item.folder !== 'trash');
    }
    return emailsState.filter((item) => item.folder === folder);
  },

  // Fetch email detail by ID
  async getEmailById(id) {
    await new Promise((resolve) => setTimeout(resolve, 40));
    const email = emailsState.find((item) => item.id === id);
    if (email) {
      email.isRead = true; // Mark as read when opened
    }
    return email || null;
  },

  // Fetch quarantine items
  async getQuarantineEmails() {
    await new Promise((resolve) => setTimeout(resolve, 60));
    return emailsState.filter((item) => item.folder === 'quarantine' || item.status === 'QUARANTINED');
  },

  // Fetch security dashboard metrics dynamically calculated from emailsState
  async getSecurityMetrics() {
    await new Promise((resolve) => setTimeout(resolve, 50));
    
    const total = emailsState.length;
    const safeCount = emailsState.filter(e => e.status === 'SAFE').length;
    const warningCount = emailsState.filter(e => e.status === 'WARNING').length;
    const quarantinedCount = emailsState.filter(e => e.status === 'QUARANTINED' || e.folder === 'quarantine').length;
    const rejectedCount = emailsState.filter(e => e.status === 'REJECTED').length;
    const failedCount = emailsState.filter(e => e.status === 'FAILED').length;
    const threatsCount = warningCount + quarantinedCount + rejectedCount + failedCount;

    // Calculate clean delivery percentage
    const cleanRate = total > 0 ? ((safeCount / total) * 100).toFixed(1) : "100";

    return {
      totalScanned: total,
      safe: safeCount,
      warnings: warningCount,
      quarantined: quarantinedCount,
      rejected: rejectedCount,
      failed: failedCount,
      threatsDetected: threatsCount,
      cleanRatePercentage: cleanRate,
      avgScanLatencyMs: 142,
      gatewayStatus: "ACTIVE_PROTECTION",
      statusDistribution: [
        { label: 'Safe', count: safeCount, percent: total > 0 ? (safeCount / total) * 100 : 0, color: '#10b981', class: 'dist-safe' },
        { label: 'Warnings', count: warningCount, percent: total > 0 ? (warningCount / total) * 100 : 0, color: '#f59e0b', class: 'dist-warning' },
        { label: 'Quarantined', count: quarantinedCount, percent: total > 0 ? (quarantinedCount / total) * 100 : 0, color: '#ef4444', class: 'dist-quarantine' },
        { label: 'Rejected', count: rejectedCount, percent: total > 0 ? (rejectedCount / total) * 100 : 0, color: '#e11d48', class: 'dist-rejected' },
      ],
      threatTrends: MOCK_SECURITY_METRICS.threatTrends,
      recentEmails: emailsState.slice(0, 5)
    };
  },

  // Toggle starred status
  async toggleStar(id) {
    emailsState = emailsState.map((item) => 
      item.id === id ? { ...item, isStarred: !item.isStarred } : item
    );
    return emailsState.find((item) => item.id === id);
  },

  // Mark as read/unread
  async markAsRead(id, isRead = true) {
    emailsState = emailsState.map((item) =>
      item.id === id ? { ...item, isRead } : item
    );
  },

  // Quarantine Actions
  async releaseQuarantine(id) {
    emailsState = emailsState.map((item) =>
      item.id === id ? { ...item, folder: 'inbox', status: 'WARNING', securityReasons: [...item.securityReasons, 'Manually released by administrator'] } : item
    );
    return true;
  },

  async deleteQuarantine(id) {
    emailsState = emailsState.filter((item) => item.id !== id);
    return true;
  },

  async reportPhishing(id) {
    emailsState = emailsState.map((item) =>
      item.id === id ? { ...item, status: 'REJECTED', securityReasons: [...item.securityReasons, 'User reported as Phishing'] } : item
    );
    return true;
  },

  // Send new email (Simulate Gateway Pre-delivery Scan)
  async sendEmail({ recipient, subject, body, attachment }) {
    await new Promise((resolve) => setTimeout(resolve, 200));

    const fullText = (subject + ' ' + body).toLowerCase();
    
    // Check 1: Embedded links or 'click here' action prompts -> High Threat / QUARANTINED
    const hasLinkOrClickHere = /https?:\/\/|www\.|click\s+(?:here|this\s+link|link|below|to)|follow\s+link|open\s+link|verify\s+(?:here|account)|login\s+here/i.test(fullText);
    
    // Check 2: Simple friendly greeting ("hello", "hi", "hey") without links -> SAFE
    const isFriendlyGreeting = /^(?:hello|hi|hey|good\s+(?:morning|afternoon|evening))\b/i.test(fullText.trim()) || (/hello|hi|hey/i.test(fullText) && !hasLinkOrClickHere && fullText.length < 150);

    // Check 3: Other suspicious keywords -> WARNING
    const hasSuspiciousKeyword = /password|urgent|bank|wire|verify|account\s+suspended|mandate/i.test(fullText);

    let status = "SAFE";
    let folder = "sent";
    let riskScore = 0.05;
    let securityReasons = ["Pre-delivery envelope & content verified clean"];

    if (hasLinkOrClickHere) {
      status = "QUARANTINED";
      folder = "quarantine";
      riskScore = 0.88;
      securityReasons = ["Pre-delivery threat intercept: Embedded link or 'click here' call-to-action detected"];
    } else if (hasSuspiciousKeyword) {
      status = "WARNING";
      riskScore = 0.45;
      securityReasons = ["Pre-delivery policy warning: High-urgency keyword or verification request flagged"];
    }

    const newEmail = {
      id: `msg-${Date.now()}`,
      deliveryId: `del_${Math.floor(10000 + Math.random() * 90000)}`,
      sender: "Alex Dev",
      senderEmail: "alex.dev@mailtrace.local",
      recipient,
      subject,
      preview: body.slice(0, 100) + '...',
      body,
      timestamp: new Date().toISOString(),
      date: "Just Now",
      folder,
      status,
      riskScore,
      isRead: true,
      isStarred: false,
      hasAttachment: !!attachment,
      attachments: attachment ? [{ name: attachment.name, size: `${(attachment.size / 1024).toFixed(1)} KB`, type: 'file', isClean: true }] : [],
      authentication: {
        spf: status === "QUARANTINED" ? "FAIL" : "PASS",
        dkim: status === "QUARANTINED" ? "FAIL" : "PASS",
        dmarc: status === "QUARANTINED" ? "FAIL" : "PASS",
        domainAlignment: status === "QUARANTINED" ? "MISMATCH" : "MATCHED"
      },
      securityReasons,
      timing: {
        scanLatencyMs: Math.floor(80 + Math.random() * 60),
        totalLatencyMs: Math.floor(120 + Math.random() * 80)
      }
    };

    emailsState.unshift(newEmail);
    return newEmail;
  }
};
