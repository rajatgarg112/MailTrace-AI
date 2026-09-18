import uuid
from typing import Dict, List, Any
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, emails, deliveries, quarantine

app = FastAPI(
    title=settings.APP_NAME,
    description="MailTrace AI Backend Foundation API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

# Register routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(emails.router, prefix=settings.API_PREFIX)
app.include_router(deliveries.router, prefix=settings.API_PREFIX)
app.include_router(quarantine.router, prefix=settings.API_PREFIX)


DEFAULT_SCAN_TIMELINE = [
    {"step": "1. Ingress & Canonicalization", "status": "COMPLETED", "duration": "0.008s"},
    {"step": "2. ISO 27037 SHA-256 Digest", "status": "COMPLETED", "duration": "0.004s"},
    {"step": "3. RFC Header Forensics & Relay Audit", "status": "COMPLETED", "duration": "0.032s"},
    {"step": "4. Cryptographic Authentication", "status": "COMPLETED", "duration": "0.025s"},
    {"step": "5. URL Phishing & Homoglyph Engine", "status": "COMPLETED", "duration": "0.018s"},
    {"step": "6. Attachment Payload Inspection", "status": "COMPLETED", "duration": "0.012s"},
    {"step": "7. NLP BEC & Intimidation Detection", "status": "COMPLETED", "duration": "0.022s"},
    {"step": "8. Security Policy Engine Decision", "status": "COMPLETED", "duration": "0.005s"},
]

# ── Mock Data Store ───────────────────────────────────────────────────────────
MOCK_INBOX = [
    {
        "id": "msg_001",
        "sender": "GitHub Notifications",
        "senderEmail": "noreply@github.com",
        "recipient": "user@mailtrace.local",
        "subject": "Your pull request was merged",
        "body": "Your pull request #42 has been successfully merged into main.",
        "timestamp": "2026-09-10T10:30:00Z",
        "status": "DELIVERED",
        "riskScore": 2.5,
        "threat_score": 2.5,
        "delivery_action": "DELIVER",
        "requires_warning": False,
        "latency_sec": 0.126,
        "policy_summary": "All SPF, DKIM, and DMARC checks passed. Verified GitHub origin.",
        "scan_timeline": DEFAULT_SCAN_TIMELINE,
        "securityReasons": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "signals": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "attachments": [],
        "verdict": "SAFE",
        "is_quarantined": False,
        "relay_map": ["smtp.github.com", "gateway.mailtrace.local"],
        "authentication": {
            "spf_status": "PASS",
            "dkim_status": "PASS",
            "dmarc_status": "PASS",
            "overall_auth_score": 100,
            "is_authenticated": True,
            "details": "SPF, DKIM, and DMARC aligned and verified by GitHub MTA"
        },
        "url_analysis": {
            "total_urls": 1,
            "malicious_urls": 0,
            "url_risk_score": 0.0,
            "findings": ["github.com: Legitimate verified corporate domain", "Zero deceptive URL tokens"]
        },
        "attachment_analysis": {
            "total_attachments": 0,
            "malicious_count": 0,
            "findings": ["Clean MIME structure; no attachments"]
        },
        "rule_triggers": ["AUTH_SPF_PASS", "AUTH_DKIM_PASS", "RFC_5322_COMPLIANT"],
        "evidence_sha256": "4f9d3b8e7a1c2d5e6f8a0b1c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e",
    },
    {
        "id": "msg_002",
        "sender": "LinkedIn",
        "senderEmail": "messages-noreply@linkedin.com",
        "recipient": "user@mailtrace.local",
        "subject": "You have 3 new connection requests",
        "body": "Priya Sharma and 2 others want to connect with you on LinkedIn.",
        "timestamp": "2026-09-10T09:15:00Z",
        "status": "WARNING",
        "riskScore": 28.0,
        "threat_score": 28.0,
        "delivery_action": "WARN",
        "requires_warning": True,
        "latency_sec": 0.142,
        "policy_summary": "Delivered with warning banner: SPF softfail from freemail relay.",
        "scan_timeline": DEFAULT_SCAN_TIMELINE,
        "securityReasons": ["SPF: softfail", "DKIM: pass", "Freemail sender detected"],
        "signals": ["SPF: softfail", "DKIM: pass", "Freemail sender detected"],
        "attachments": [],
        "verdict": "SUSPICIOUS",
        "is_quarantined": False,
        "relay_map": ["smtp.linkedin.com", "gateway.mailtrace.local"],
        "authentication": {
            "spf_status": "SOFTFAIL",
            "dkim_status": "PASS",
            "dmarc_status": "PASS",
            "overall_auth_score": 65,
            "is_authenticated": True,
            "details": "SPF softfail: relay IP in transition"
        },
        "url_analysis": {
            "total_urls": 2,
            "malicious_urls": 0,
            "url_risk_score": 20.0,
            "findings": ["External redirect tracking link present", "URL uses tracking parameters"]
        },
        "attachment_analysis": {
            "total_attachments": 0,
            "malicious_count": 0,
            "findings": ["No suspicious attachments"]
        },
        "rule_triggers": ["SPF_SOFTFAIL_WARNING", "EXTERNAL_TRACKING_REDIRECT"],
        "evidence_sha256": "7c8b9a0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c",
    },
    {
        "id": "msg_003",
        "sender": "Google Workspace",
        "senderEmail": "workspace-noreply@google.com",
        "recipient": "user@mailtrace.local",
        "subject": "Security alert: New sign-in on your account",
        "body": "A new sign-in to your account was detected from Windows, Chrome.",
        "timestamp": "2026-09-10T08:00:00Z",
        "status": "DELIVERED",
        "riskScore": 5.0,
        "threat_score": 5.0,
        "delivery_action": "DELIVER",
        "requires_warning": False,
        "latency_sec": 0.118,
        "policy_summary": "Clean delivery: Google Workspace enterprise authentication fully aligned.",
        "scan_timeline": DEFAULT_SCAN_TIMELINE,
        "securityReasons": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "signals": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "attachments": [],
        "verdict": "SAFE",
        "is_quarantined": False,
        "relay_map": ["smtp.google.com", "gateway.mailtrace.local"],
        "authentication": {
            "spf_status": "PASS",
            "dkim_status": "PASS",
            "dmarc_status": "PASS",
            "overall_auth_score": 100,
            "is_authenticated": True,
            "details": "Google enterprise SPF, DKIM, and DMARC passing"
        },
        "url_analysis": {
            "total_urls": 1,
            "malicious_urls": 0,
            "url_risk_score": 0.0,
            "findings": ["google.com: Verified security notification origin"]
        },
        "attachment_analysis": {
            "total_attachments": 0,
            "malicious_count": 0,
            "findings": ["No attachments"]
        },
        "rule_triggers": ["AUTH_ALL_PASS", "TRUSTED_REPUTATION_DOMAIN"],
        "evidence_sha256": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
    },
]

MOCK_QUARANTINE = [
    {
        "id": "msg_q01",
        "sender": "NIC Portal Support",
        "senderEmail": "support@nic-portal-update.xyz",
        "recipient": "user@mailtrace.local",
        "subject": "URGENT: Verify Your NIC Account Now",
        "body": "Your NIC account will be suspended in 2 hours. Login at http://198.51.100.99/login-nic immediately.",
        "timestamp": "2026-09-10T07:45:00Z",
        "status": "QUARANTINED",
        "riskScore": 91.5,
        "threat_score": 91.5,
        "delivery_action": "QUARANTINE",
        "requires_warning": False,
        "latency_sec": 0.185,
        "policy_summary": "Direct IP phishing URL and spoofed lookalike domain detected. Quarantined under ISO/IEC 27037.",
        "scan_timeline": DEFAULT_SCAN_TIMELINE,
        "securityReasons": [
            "SPF: FAIL",
            "DKIM: FAIL",
            "DMARC: FAIL",
            "Lookalike domain detected: nic-portal-update.xyz",
            "Malicious IP URL: http://198.51.100.99/login-nic",
            "Credential harvesting language detected",
            "High urgency pressure: 'account suspended', '2 hours'",
        ],
        "signals": [
            "SPF: FAIL", "DKIM: FAIL", "DMARC: FAIL",
            "Lookalike domain detected", "Malicious IP URL", "Credential harvesting language",
        ],
        "attachments": [],
        "verdict": "MALICIOUS",
        "is_quarantined": True,
        "evidence_sha256": "a3f5c2e1b4d6f8a0c2e4f6a8b0d2e4f6a8c0e2f4a6b8d0e2f4c6a8b0d2e4f6a8",
        "chain_of_custody": "Received at gateway → Security scan → ML analysis → Risk Engine → QUARANTINED",
        "relay_map": ["smtp.nic-portal-update.xyz", "relay.hostingprovider.net", "gateway.mailtrace.local"],
        "authentication": {
            "spf_status": "FAIL",
            "dkim_status": "FAIL",
            "dmarc_status": "FAIL",
            "overall_auth_score": 0,
            "is_authenticated": False,
            "details": "Sender IP 198.51.100.99 not in SPF record; DKIM signature invalid; DMARC policy reject"
        },
        "url_analysis": {
            "total_urls": 1,
            "malicious_urls": 1,
            "url_risk_score": 90.0,
            "findings": [
                "Direct IP-hosted URL: http://198.51.100.99/login-nic (Malicious)",
                "Lookalike domain detected: nic-portal-update.xyz",
                "Credential harvesting login endpoint"
            ]
        },
        "attachment_analysis": {
            "total_attachments": 0,
            "malicious_count": 0,
            "findings": ["No payload attachment; web-based credential harvester"]
        },
        "rule_triggers": [
            "SPF_FAIL_UNAUTHORIZED_IP",
            "DKIM_SIGNATURE_MISSING",
            "DMARC_POLICY_REJECT",
            "MALICIOUS_IP_HOSTED_URL",
            "CREDENTIAL_HARVESTING_URGENCY"
        ]
    },
    {
        "id": "msg_q02",
        "sender": "IT Helpdesk",
        "senderEmail": "helpdesk@company-internal.tk",
        "recipient": "user@mailtrace.local",
        "subject": "Password Reset Required - Action Needed",
        "body": "Click here to reset your password: http://bit.ly/3xR9mP2. Link expires in 1 hour.",
        "timestamp": "2026-09-10T06:30:00Z",
        "status": "QUARANTINED",
        "riskScore": 78.0,
        "threat_score": 78.0,
        "delivery_action": "QUARANTINE",
        "requires_warning": False,
        "latency_sec": 0.162,
        "policy_summary": "SPF failure with suspicious .tk TLD and obfuscated bit.ly link. Delivery blocked.",
        "scan_timeline": DEFAULT_SCAN_TIMELINE,
        "securityReasons": [
            "SPF: FAIL",
            "Suspicious TLD: .tk",
            "URL shortener detected",
            "Credential harvesting language",
        ],
        "signals": ["SPF: FAIL", "Suspicious TLD: .tk", "URL shortener detected", "Credential harvesting language"],
        "attachments": [],
        "verdict": "MALICIOUS",
        "is_quarantined": True,
        "evidence_sha256": "b4e6d0f2a8c4e0f6b2d8a4c0e6f2b8d4a0e6c2f8b4d0a6e2c8f4b0d6a2e8c4f0",
        "chain_of_custody": "Received at gateway → Security scan → Risk Engine → QUARANTINED",
        "relay_map": ["mail.company-internal.tk", "gateway.mailtrace.local"],
        "authentication": {
            "spf_status": "FAIL",
            "dkim_status": "FAIL",
            "dmarc_status": "FAIL",
            "overall_auth_score": 10,
            "is_authenticated": False,
            "details": "SPF failure on suspicious .tk domain; unauthenticated origin"
        },
        "url_analysis": {
            "total_urls": 1,
            "malicious_urls": 1,
            "url_risk_score": 75.0,
            "findings": [
                "URL shortener detected: http://bit.ly/3xR9mP2 (Obfuscated target)",
                "Suspicious free TLD: .tk"
            ]
        },
        "attachment_analysis": {
            "total_attachments": 0,
            "malicious_count": 0,
            "findings": ["Clean MIME structure"]
        },
        "rule_triggers": [
            "SPF_AUTHENTICATION_FAIL",
            "URL_SHORTENER_OBFUSCATION",
            "SUSPICIOUS_TOP_LEVEL_DOMAIN"
        ]
    },
]

MOCK_SCENARIOS = [
    {
        "id": "phishing_nic",
        "title": "🚨 NIC Portal Credential Phishing",
        "sender": "NIC Support <support@nic-portal-update.xyz>",
        "subject": "CRITICAL: Verify Your Government NIC Account",
        "description": "Lookalike government domain with direct IP link and fake suspension deadline.",
    },
    {
        "id": "bec_attack",
        "title": "💸 BEC / CEO Wire Transfer Fraud",
        "sender": "Directorate Office <director@aicte-gov-portal.co>",
        "subject": "URGENT MANDATE: Institutional Wire Transfer Required",
        "description": "Executive impersonation demanding emergency fund transfer with artificial authority.",
    },
    {
        "id": "malicious_attachment",
        "title": "☣️ Weaponized Attachment (.pdf.exe)",
        "sender": "Finance Accounts <invoicing@vendor-delivery.online>",
        "subject": "Overdue Settlement Notice: INV-2026-9921",
        "description": "Disguised executable payload (mandate_invoice.pdf.exe) bypassing standard filters.",
    },
    {
        "id": "spf_fail",
        "title": "⚠️ Unauthorized Server Relay (SPF Fail)",
        "sender": "Internal IT Helpdesk <support@mailtrace.local>",
        "subject": "Security Notice: Mandatory Password Expiration",
        "description": "Spoofed internal helpdesk sent from an unauthorized third-party public relay.",
    },
    {
        "id": "benign_newsletter",
        "title": "✅ Verified Clean Enterprise Email (Full Pass)",
        "sender": "Engineering Team <updates@github.com>",
        "subject": "SIH 2026 Milestone Review & Deliverables Merged",
        "description": "Clean engineering update with 100% verified SPF, DKIM, and DMARC alignment.",
    },
]


# ── Mailbox Routes (Frontend expects these) ────────────────────────────────────

@app.get("/api/mailbox/inbox", tags=["Mailbox"])
def get_inbox() -> List[Dict]:
    """Return inbox emails (delivered + warning status)."""
    return MOCK_INBOX


@app.get("/api/mailbox/quarantine", tags=["Mailbox"])
def get_quarantine() -> List[Dict]:
    """Return quarantined emails."""
    return MOCK_QUARANTINE


@app.get("/api/scenarios", tags=["Scenarios"])
def get_scenarios() -> List[Dict]:
    """Return available email simulation scenarios."""
    return MOCK_SCENARIOS


@app.post("/api/deliveries/simulate", tags=["Simulate"])
async def simulate_delivery(payload: Dict[str, Any]) -> Dict:
    """
    Intelligent pre-delivery simulation analyzer.
    Inspects scenario_id, raw_email content, headers, IP URLs,
    and linguistic urgency patterns to calculate real threat scores.
    """
    import re
    import hashlib

    scenario_id = payload.get("scenario_id", "")

    # Map scenario presets to rich demo payloads
    scenario_map = {
        "phishing_nic": {
            "sender": "NIC Support <support@nic-portal-update.xyz>",
            "subject": "CRITICAL: Verify Your Government NIC Account",
            "raw_email": (
                "From: NIC Support <support@nic-portal-update.xyz>\n"
                "Subject: CRITICAL: Verify Your Government NIC Account\n"
                "Authentication-Results: spf=fail; dkim=fail; dmarc=fail\n\n"
                "Your government NIC account will be suspended in 2 hours.\n"
                "Log in immediately at http://198.51.100.99/login-nic to re-verify your credentials."
            ),
        },
        "bec_attack": {
            "sender": "Directorate Office <director@aicte-gov-portal.co>",
            "subject": "URGENT MANDATE: Institutional Wire Transfer Required",
            "raw_email": (
                "From: Directorate Office <director@aicte-gov-portal.co>\n"
                "Subject: URGENT MANDATE: Institutional Wire Transfer Required\n"
                "Authentication-Results: spf=fail; dkim=fail; dmarc=fail\n\n"
                "ATTENTION INSTITUTION HEAD:\n"
                "Immediate wire transfer of ₹450,000 is mandatory for SIH registration compliance.\n"
                "Transfer funds to bank account details attached immediately or portal access will be suspended within 2 hours."
            ),
        },
        "malicious_attachment": {
            "sender": "Finance Accounts <invoicing@vendor-delivery.online>",
            "subject": "Overdue Settlement Notice: INV-2026-9921",
            "raw_email": (
                "From: Finance Accounts <invoicing@vendor-delivery.online>\n"
                "Subject: Overdue Settlement Notice: INV-2026-9921\n"
                "Authentication-Results: spf=fail; dkim=fail\n\n"
                "Please find attached overdue invoice document: mandate_invoice.pdf.exe.\n"
                "Double click attachment to open and execute payment settlement."
            ),
        },
        "spf_fail": {
            "sender": "Internal IT Helpdesk <support@mailtrace.local>",
            "subject": "Security Notice: Mandatory Password Expiration",
            "raw_email": (
                "From: Internal IT Helpdesk <support@mailtrace.local>\n"
                "Subject: Security Notice: Mandatory Password Expiration\n"
                "Authentication-Results: spf=fail; dkim=pass\n\n"
                "Your workstation corporate password will expire in 24 hours.\n"
                "Please verify your credentials at the internal helpdesk portal."
            ),
        },
        "benign_newsletter": {
            "sender": "Engineering Team <updates@github.com>",
            "subject": "SIH 2026 Milestone Review & Deliverables Merged",
            "raw_email": (
                "From: Engineering Team <updates@github.com>\n"
                "Subject: SIH 2026 Milestone Review & Deliverables Merged\n"
                "Authentication-Results: spf=pass; dkim=pass; dmarc=pass\n\n"
                "Hi Team,\n\n"
                "All security modules for feature/security-foundation have passed validation and merged successfully.\n"
                "Official repository links: https://github.com/mailtrace-ai\n\n"
                "Best regards,\nAlice Developer"
            ),
        },
    }

    if scenario_id in scenario_map:
        scen = scenario_map[scenario_id]
        sender = payload.get("sender") or scen["sender"]
        subject = payload.get("subject") or scen["subject"]
        raw_email = payload.get("raw_email") or scen["raw_email"]
    else:
        sender = payload.get("sender", "") or "test@example.com"
        subject = payload.get("subject", "") or "Simulated Message"
        raw_email = payload.get("raw_email", "") or ""
    full_text = f"{sender} {subject} {raw_email}".lower()

    # ── Signal Extraction ─────────────────────────────────────────────────────
    signals = []
    reasons = []
    threat_score = 0.0

    # 1. Authentication header checks
    has_spf_fail = bool(re.search(r'spf\s*=\s*(fail|softfail)', full_text))
    has_dkim_fail = bool(re.search(r'dkim\s*=\s*fail', full_text))
    has_dmarc_fail = bool(re.search(r'dmarc\s*=\s*fail', full_text))

    if has_spf_fail or has_dkim_fail or has_dmarc_fail or scenario_id == "spf_fail":
        auth_details = []
        if has_spf_fail or scenario_id == "spf_fail":
            auth_details.append("SPF: FAIL")
            threat_score += 35.0
        if has_dkim_fail:
            auth_details.append("DKIM: FAIL")
            threat_score += 30.0
        if has_dmarc_fail:
            auth_details.append("DMARC: FAIL")
            threat_score += 30.0
        reason_str = f"Authentication Failure: {', '.join(auth_details)}"
        signals.extend(auth_details)
        reasons.append(reason_str)

    # 2. Raw IP URL checks (e.g. http://198.51.100.99)
    ip_url_match = re.search(r'http[s]?://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[^\s]*', raw_email)
    if ip_url_match:
        ip_found = ip_url_match.group(0)
        signals.append("Malicious IP URL")
        reasons.append(f"Direct IP-hosted URL detected: {ip_found}")
        threat_score += 45.0

    # 3. Urgency & Psychological Pressure Triggers
    urgency_patterns = [
        (r'\b(suspend|suspended|suspension)\b', "Account suspension threat"),
        (r'\b(expire|expires|expired|expiration)\b', "Artificial deadline pressure"),
        (r'\b(urgent|immediately|action required)\b', "Urgency exploitation"),
        (r'\b(re-verify|verify your|password reset|credential)\b', "Credential harvesting pattern"),
        (r'\b(unauthorized|compromised|security alert)\b', "Fear-inducing security alert"),
    ]
    urgency_hits = []
    for pattern, label in urgency_patterns:
        if re.search(pattern, full_text):
            urgency_hits.append(label)
    if urgency_hits:
        signals.append("Urgency/BEC Pressure")
        reasons.append(f"Linguistic threat triggers: {', '.join(urgency_hits[:3])}")
        threat_score += min(len(urgency_hits) * 15.0, 35.0)

    # 4. Suspicious Domains / TLDs
    suspicious_domain_match = re.search(r'(@|//)([a-zA-Z0-9\-\.]+\.(xyz|tk|ml|top|gq|cf|online|click|xyz))', full_text)
    if suspicious_domain_match or "nic-portal" in full_text or "evil" in full_text:
        dom = suspicious_domain_match.group(2) if suspicious_domain_match else "suspicious-relay.net"
        signals.append("Untrusted/Lookalike Domain")
        reasons.append(f"Lookalike / Untrusted domain detected: {dom}")
        threat_score += 25.0

    # 5. Scenario overrides
    if scenario_id in ("phishing_nic", "bec_attack", "malicious_attachment"):
        threat_score = max(threat_score, 88.0)
        if not reasons:
            reasons.append("High-confidence threat scenario detected")
            signals.append("Gateway Threat Rule Triggered")

    # ── Calculate Final Verdict ───────────────────────────────────────────────
    final_score = min(max(threat_score, 5.0), 98.5) if (signals or reasons) else 6.5
    is_quarantined = final_score >= 55.0
    requires_warning = 25.0 <= final_score < 55.0

    # Generate deterministic SHA-256 evidence digest
    msg_id = f"msg_{uuid.uuid4().hex[:6]}"
    sha_digest = hashlib.sha256(f"{msg_id}{sender}{raw_email}".encode()).hexdigest()

    # ── Forensic Data Objects for UI ──────────────────────────────────────────
    if has_spf_fail or has_dkim_fail or has_dmarc_fail or scenario_id == "spf_fail":
        spf_val = "FAIL" if (has_spf_fail or scenario_id == "spf_fail") else "PASS"
        dkim_val = "FAIL" if has_dkim_fail else "PASS"
        dmarc_val = "FAIL"
        auth_score_val = 0 if (spf_val == "FAIL" and dkim_val == "FAIL") else 30
    elif requires_warning:
        spf_val = "SOFTFAIL"
        dkim_val = "PASS"
        dmarc_val = "PASS"
        auth_score_val = 65
    else:
        spf_val = "PASS"
        dkim_val = "PASS"
        dmarc_val = "PASS"
        auth_score_val = 100

    auth_payload = {
        "spf_status": spf_val,
        "dkim_status": dkim_val,
        "dmarc_status": dmarc_val,
        "overall_auth_score": auth_score_val,
        "is_authenticated": auth_score_val >= 70,
        "details": f"SPF: {spf_val}, DKIM: {dkim_val}, DMARC: {dmarc_val}"
    }

    url_findings = []
    if ip_url_match:
        url_findings.append(f"Direct IP URL detected: {ip_url_match.group(0)} (High Threat)")
    if suspicious_domain_match:
        url_findings.append(f"Lookalike / Untrusted domain detected: {suspicious_domain_match.group(2)}")
    if re.search(r'/(login|verify|signin|re-verify)', full_text):
        url_findings.append("Potential credential harvesting endpoint detected in URL path")
    if not url_findings:
        url_findings.append("No malicious or deceptive URLs detected")

    url_analysis_payload = {
        "total_urls": len(url_findings) if (ip_url_match or suspicious_domain_match) else 0,
        "malicious_urls": 1 if (ip_url_match or suspicious_domain_match) else 0,
        "url_risk_score": 85.0 if ip_url_match else (40.0 if suspicious_domain_match else 0.0),
        "findings": url_findings
    }

    att_findings = []
    if scenario_id == "malicious_attachment" or re.search(r'\.(exe|scr|vbs|bat|cmd|docm|xlsm)', full_text):
        att_findings.append("High-risk executable or macro attachment detected")
    else:
        att_findings.append("Clean MIME structure: zero dangerous attachments")

    attachment_analysis_payload = {
        "total_attachments": 1 if "attachment" in full_text else 0,
        "malicious_count": 1 if (scenario_id == "malicious_attachment") else 0,
        "findings": att_findings
    }

    rule_triggers = []
    if spf_val == "FAIL":
        rule_triggers.append("AUTH_SPF_FAIL_UNAUTHORIZED_IP")
    if dkim_val == "FAIL":
        rule_triggers.append("AUTH_DKIM_SIGNATURE_TAMPERED")
    if dmarc_val == "FAIL":
        rule_triggers.append("AUTH_DMARC_POLICY_REJECT")
    if ip_url_match:
        rule_triggers.append("NETWORK_IP_HOSTED_URL_DETECTED")
    if urgency_hits:
        rule_triggers.append("LINGUISTIC_URGENCY_HARVESTING_PRESSURE")
    if suspicious_domain_match:
        rule_triggers.append("DOMAIN_HOMOGLYPH_OR_UNTRUSTED_TLD")
    if not rule_triggers:
        rule_triggers.append("GATEWAY_PRE_DELIVERY_CLEAN_PASS")

    if is_quarantined:
        result = {
            "id": msg_id,
            "sender": sender,
            "senderEmail": sender,
            "recipient": "user@mailtrace.local",
            "subject": subject,
            "body": raw_email or "Suspicious email content quarantined.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "QUARANTINED",
            "riskScore": final_score,
            "threat_score": final_score,
            "delivery_action": "QUARANTINE",
            "requires_warning": False,
            "latency_sec": 0.174,
            "policy_summary": "Pre-delivery quarantine enforced: multi-signal threat indicators detected.",
            "scan_timeline": DEFAULT_SCAN_TIMELINE,
            "securityReasons": reasons,
            "signals": signals,
            "attachments": [],
            "verdict": "MALICIOUS",
            "is_quarantined": True,
            "evidence_sha256": sha_digest,
            "chain_of_custody": f"Received at Gateway → Deep Scan → Threat Score {final_score}/100 → Pre-Delivery Block → Quarantined (ISO/IEC 27037)",
            "relay_map": ["smtp.untrusted-origin.net", "relay.external-hop.org", "gateway.mailtrace.local"],
            "authentication": auth_payload,
            "url_analysis": url_analysis_payload,
            "attachment_analysis": attachment_analysis_payload,
            "rule_triggers": rule_triggers,
        }
        MOCK_QUARANTINE.append(result)
    elif requires_warning:
        result = {
            "id": msg_id,
            "sender": sender,
            "senderEmail": sender,
            "recipient": "user@mailtrace.local",
            "subject": subject,
            "body": raw_email or "Message delivered with warning.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "WARNING",
            "riskScore": final_score,
            "threat_score": final_score,
            "delivery_action": "WARN",
            "requires_warning": True,
            "latency_sec": 0.138,
            "policy_summary": "Delivered with warning banner: suspicious relay or tracking parameters detected.",
            "scan_timeline": DEFAULT_SCAN_TIMELINE,
            "securityReasons": reasons,
            "signals": signals,
            "attachments": [],
            "verdict": "SUSPICIOUS",
            "is_quarantined": False,
            "evidence_sha256": sha_digest,
            "chain_of_custody": f"Received at Gateway → Scan passed with warnings (Score {final_score}/100) → Delivered with Alert Banner",
            "relay_map": ["smtp.external-sender.org", "gateway.mailtrace.local"],
            "authentication": auth_payload,
            "url_analysis": url_analysis_payload,
            "attachment_analysis": attachment_analysis_payload,
            "rule_triggers": rule_triggers,
        }
        MOCK_INBOX.append(result)
    else:
        result = {
            "id": msg_id,
            "sender": sender,
            "senderEmail": sender,
            "recipient": "user@mailtrace.local",
            "subject": subject,
            "body": raw_email or "Clean email content.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "DELIVERED",
            "riskScore": final_score,
            "threat_score": final_score,
            "delivery_action": "DELIVER",
            "requires_warning": False,
            "latency_sec": 0.112,
            "policy_summary": "Clean delivery: all cryptographic and content security policies satisfied.",
            "scan_timeline": DEFAULT_SCAN_TIMELINE,
            "securityReasons": ["SPF: pass", "DKIM: pass", "DMARC: pass", "Zero threat indicators detected"],
            "signals": ["SPF: pass", "DKIM: pass", "Clean content"],
            "attachments": [],
            "verdict": "SAFE",
            "is_quarantined": False,
            "evidence_sha256": sha_digest,
            "chain_of_custody": "Received at Gateway → Scan Clean (Score 6.5/100) → Delivered to User Inbox",
            "relay_map": ["smtp.verified-sender.org", "gateway.mailtrace.local"],
            "authentication": auth_payload,
            "url_analysis": url_analysis_payload,
            "attachment_analysis": attachment_analysis_payload,
            "rule_triggers": rule_triggers,
        }
        MOCK_INBOX.append(result)

    return result


@app.post("/api/messages/{msg_id}/release", tags=["Quarantine"])
def release_message(msg_id: str) -> Dict:
    """Release a message from quarantine to inbox."""
    global MOCK_QUARANTINE
    released = None
    for msg in MOCK_QUARANTINE:
        if msg["id"] == msg_id:
            released = msg
            break
    if released:
        MOCK_QUARANTINE = [m for m in MOCK_QUARANTINE if m["id"] != msg_id]
        released["status"] = "DELIVERED"
        released["is_quarantined"] = False
        MOCK_INBOX.append(released)
    return {"success": True, "message": f"Message {msg_id} released to inbox"}


@app.get("/", tags=["Root"])
def root() -> Dict[str, str]:
    """Root entrypoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
    }
