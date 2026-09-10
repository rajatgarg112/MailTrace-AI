// MailTrace AI — Mock Email & Quarantine Dataset
// Pre-delivery Gateway security schema matching official data model specifications

export const INITIAL_MOCK_EMAILS = [
  {
    id: "msg-101",
    deliveryId: "del_89201",
    sender: "University Placement Cell",
    senderEmail: "placements@university.edu.in",
    recipient: "alex.dev@mailtrace.local",
    subject: "Campus Placement Drive 2026 — Schedule & Registration",
    preview: "Dear Students, The annual campus placement drive schedule for the 2026 batch has been finalized. Please submit your updated CVs...",
    body: `Dear Students,

We are pleased to announce the upcoming Campus Placement Drive 2026. Top tech organizations and research labs will be participating over the next three weeks.

Key Instructions:
1. Ensure your profile resume is updated in the placement portal.
2. Review the company eligibility criteria attached below.
3. Attend the mandatory pre-placement talk tomorrow at 10:00 AM IST in the Main Auditorium.

Attached is the detailed timetable and company registration links.

Best Regards,
Placement Office
University Technology Campus`,
    timestamp: "2026-09-10T11:45:00Z",
    date: "11:45 AM",
    folder: "inbox",
    status: "SAFE",
    riskScore: 0.04,
    isRead: false,
    isStarred: true,
    hasAttachment: true,
    attachments: [
      { name: "Placement_Drive_2026_Schedule.pdf", size: "1.4 MB", type: "pdf", isClean: true }
    ],
    authentication: {
      spf: "PASS",
      dkim: "PASS",
      dmarc: "PASS",
      domainAlignment: "MATCHED"
    },
    securityReasons: [
      "Sender verified",
      "Domain authenticated",
      "SPF passed",
      "DKIM passed",
      "DMARC passed",
      "No suspicious URLs",
      "No suspicious attachment"
    ],
    evidence: [
      {
        id: "EVD-101-A",
        type: "DKIM_CRYPTOGRAPHIC_VERIFICATION",
        sha256: "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        confidence: 0.99,
        explanation: "Cryptographic signature verified against published DNS key selector 's2026'",
        analyzer: "MailTrace-DKIM-Verifier-v1.4"
      },
      {
        id: "EVD-101-B",
        type: "ATTACHMENT_STATIC_SCAN",
        sha256: "8F9A2B4C6D8E0F1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F56",
        confidence: 0.98,
        explanation: "PDF document static analysis returned zero embedded malicious JavaScript or macros",
        analyzer: "MailTrace-Sandbox-Scanner-v3.0"
      }
    ],
    timing: {
      scanLatencyMs: 145,
      totalLatencyMs: 198
    }
  },
  {
    id: "msg-102",
    deliveryId: "del_89202",
    sender: "IT Support Department",
    senderEmail: "security-update@mailtrace-support.net",
    recipient: "alex.dev@mailtrace.local",
    subject: "URGENT: Password Expiration Notice & Credential Sync",
    preview: "Your organization password will expire in 4 hours. You must reset your password immediately to maintain mailbox access...",
    body: `ATTENTION MAILTRACE USER,

Your active directory account password is scheduled to expire in 4 hours due to compliance policy SEC-2026.

If you fail to update your credentials immediately, your access to MailTrace security services and internal repositories will be suspended.

Please click the secure link below to verify your current password and set a new password:
http://auth-sync-mailtrace.temp-update.net/login?id=alex.dev

Do not ignore this notice.

IT Helpdesk Support Team`,
    timestamp: "2026-09-10T10:15:00Z",
    date: "10:15 AM",
    folder: "inbox",
    status: "WARNING",
    riskScore: 0.68,
    isRead: true,
    isStarred: false,
    hasAttachment: false,
    attachments: [],
    authentication: {
      spf: "PASS",
      dkim: "FAIL",
      dmarc: "NEUTRAL",
      domainAlignment: "MISMATCH"
    },
    securityReasons: [
      "Sender characteristics suspicious",
      "Domain requires verification",
      "Suspicious link detected"
    ],
    evidence: [
      {
        id: "EVD-102-A",
        type: "DOMAIN_ALIGNMENT_MISMATCH",
        sha256: "7B2C4D6E8F0A1C3E5G7I9K1M3O5Q7S9U1W3Y5A7C9E1G3I5K7M9O1Q3S5U7W9Y1",
        confidence: 0.92,
        explanation: "Header From domain 'mailtrace-support.net' does not match internal MTA root domain",
        analyzer: "MailTrace-Header-Aligner-v2.1"
      },
      {
        id: "EVD-102-B",
        type: "URL_REPUTATION_FLAG",
        sha256: "1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F56789A0B1C2D3E4",
        confidence: 0.88,
        explanation: "Embedded link 'auth-sync-mailtrace.temp-update.net' resolves to newly registered untrusted domain",
        analyzer: "MailTrace-URL-Sandbox-v1.8"
      }
    ],
    timing: {
      scanLatencyMs: 230,
      totalLatencyMs: 310
    }
  },
  {
    id: "msg-103",
    deliveryId: "del_89203",
    sender: "Account Verification Service",
    senderEmail: "no-reply@verify-bank-security-center.com",
    recipient: "alex.dev@mailtrace.local",
    subject: "Urgent Account Verification Required — Action Locked",
    preview: "Suspicious login attempt detected on your corporate gateway account. Click here to confirm your identity...",
    body: `Security Alert!

We detected an unauthorized login attempt from IP 185.220.101.5 (Kyiv, Ukraine) targeting your primary account.

For your protection, outgoing mail capabilities have been temporarily locked until you verify your credentials.

Verification Portal:
https://verify-bank-security-center.com/auth/confirm?user=alex.dev

Note: This link will expire in 15 minutes.`,
    timestamp: "2026-09-10T08:30:00Z",
    date: "08:30 AM",
    folder: "quarantine",
    status: "QUARANTINED",
    riskScore: 0.94,
    isRead: false,
    isStarred: false,
    hasAttachment: true,
    attachments: [
      { name: "Verification_Instructions.scr", size: "340 KB", type: "exe", isClean: false }
    ],
    authentication: {
      spf: "FAIL",
      dkim: "FAIL",
      dmarc: "FAIL",
      domainAlignment: "FAILED"
    },
    securityReasons: [
      "Email blocked",
      "Phishing indicators detected",
      "Sender impersonation suspected",
      "Suspicious URL detected",
      "Attachment requires analysis"
    ],
    evidence: [
      {
        id: "EVD-103-A",
        type: "CREDENTIAL_HARVEST_VECTOR",
        sha256: "9C0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F56789A0B1C2D3E4F56789A0B1C2D3E4F",
        confidence: 0.97,
        explanation: "Heuristic NLP vector matches credential harvesting phishing template #884",
        analyzer: "MailTrace-NLP-Intent-v2.4"
      },
      {
        id: "EVD-103-B",
        type: "MALICIOUS_EXECUTABLE_PAYLOAD",
        sha256: "5F4E3D2C1B0A9F8E7D6C5B4A3F2E1D0C9B8A7F6E5D4C3B2A1F0E9D8C7B6A5F4",
        confidence: 0.99,
        explanation: "Attachment 'Verification_Instructions.scr' contains obfuscated Windows PE executable header",
        analyzer: "MailTrace-YARA-Engine-v4.2"
      }
    ],
    timing: {
      scanLatencyMs: 410,
      totalLatencyMs: 460
    }
  },
  {
    id: "msg-104",
    deliveryId: "del_89204",
    sender: "Global HR Department",
    senderEmail: "hr@mailtrace.io",
    recipient: "alex.dev@mailtrace.local",
    subject: "Q4 Engineering Internship & Mentorship Program",
    preview: "Applications are now open for the Q4 Mentorship Program. Find the stipend details and mentor list in the attached brochure...",
    body: `Hello Team,

We are excited to kick off the Q4 Engineering Internship & Mentorship Program!

This quarter, senior architects from our Gateway & Machine Learning teams will mentor junior developers in email security algorithms, distributed MTA architecture, and zero-trust proxy design.

Key Benefits:
- Hands-on pairing on production Rust & Python gateways
- Direct guidance on vulnerability analysis
- Monthly stipend increase for top contributors

Please find the eligibility handbook attached.

Warm regards,
HR Operations Team
MailTrace AI`,
    timestamp: "2026-09-09T16:20:00Z",
    date: "Sep 9",
    folder: "inbox",
    status: "SAFE",
    riskScore: 0.02,
    isRead: true,
    isStarred: true,
    hasAttachment: true,
    attachments: [
      { name: "Mentorship_Guide_Q4.pdf", size: "2.8 MB", type: "pdf", isClean: true }
    ],
    authentication: {
      spf: "PASS",
      dkim: "PASS",
      dmarc: "PASS",
      domainAlignment: "MATCHED"
    },
    securityReasons: [
      "Sender verified",
      "Domain authenticated",
      "SPF passed",
      "DKIM passed",
      "DMARC passed",
      "No suspicious URLs",
      "No suspicious attachment"
    ],
    evidence: [
      {
        id: "EVD-104-A",
        type: "INTERNAL_MTA_TRUST",
        sha256: "4A3F2E1D0C9B8A7F6E5D4C3B2A1F0E9D8C7B6A5F4E3D2C1B0A9F8E7D6C5B4A3",
        confidence: 1.0,
        explanation: "Authenticated loopback from internal MailTrace MTA corporate domain",
        analyzer: "MailTrace-Trust-Manager-v1.0"
      }
    ],
    timing: {
      scanLatencyMs: 95,
      totalLatencyMs: 130
    }
  },
  {
    id: "msg-105",
    deliveryId: "del_89205",
    sender: "AWS Billing Alert System",
    senderEmail: "no-reply-billing@amazon-aws-verify.co.uk",
    recipient: "alex.dev@mailtrace.local",
    subject: "Payment Overdue: AWS Infrastructure Instance Termination",
    preview: "Your monthly AWS cloud instance bill of $4,280.50 is overdue. Immediate payment required to avoid service termination...",
    body: `AWS Cloud Services Alert,

Invoice ID: INV-2026-889102
Amount Due: $4,280.50 USD

Your linked credit card was declined by the issuing bank. If payment is not updated within 24 hours, your EC2 gateway instances will be terminated.

Pay Invoice Online:
https://amazon-aws-verify.co.uk/billing/pay?inv=889102

Thank you,
AWS Finance Cloud Operations`,
    timestamp: "2026-09-09T14:10:00Z",
    date: "Sep 9",
    folder: "quarantine",
    status: "QUARANTINED",
    riskScore: 0.98,
    isRead: false,
    isStarred: false,
    hasAttachment: false,
    attachments: [],
    authentication: {
      spf: "FAIL",
      dkim: "FAIL",
      dmarc: "FAIL",
      domainAlignment: "FAILED"
    },
    securityReasons: [
      "Email blocked",
      "Phishing indicators detected",
      "Sender impersonation suspected",
      "Suspicious URL detected"
    ],
    evidence: [
      {
        id: "EVD-105-A",
        type: "BRAND_IMPERSONATION_FLAG",
        sha256: "3B2A1F0E9D8C7B6A5F4E3D2C1B0A9F8E7D6C5B4A3F2E1D0C9B8A7F6E5D4C3B2",
        confidence: 0.99,
        explanation: "Amazon Web Services brand name used on unauthorized registrar 'amazon-aws-verify.co.uk'",
        analyzer: "MailTrace-Brand-Intel-v1.2"
      }
    ],
    timing: {
      scanLatencyMs: 380,
      totalLatencyMs: 425
    }
  }
];

export const MOCK_SECURITY_METRICS = {
  totalScanned: 1248,
  safe: 1080,
  warnings: 96,
  quarantined: 58,
  rejected: 14,
  threatsDetected: 168,
  avgScanLatencyMs: 142,
  gatewayStatus: "ACTIVE_PROTECTION",
  threatTrends: [
    { day: "Mon", safe: 180, warnings: 12, quarantined: 8, rejected: 2 },
    { day: "Tue", safe: 165, warnings: 15, quarantined: 10, rejected: 3 },
    { day: "Wed", safe: 190, warnings: 18, quarantined: 12, rejected: 1 },
    { day: "Thu", safe: 175, warnings: 10, quarantined: 6, rejected: 2 },
    { day: "Fri", safe: 195, warnings: 22, quarantined: 14, rejected: 4 },
    { day: "Sat", safe: 90, warnings: 8, quarantined: 4, rejected: 1 },
    { day: "Sun", safe: 85, warnings: 11, quarantined: 4, rejected: 1 }
  ]
};
