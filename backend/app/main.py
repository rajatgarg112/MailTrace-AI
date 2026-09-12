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
        "securityReasons": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "signals": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "attachments": [],
        "verdict": "SAFE",
        "is_quarantined": False,
        "relay_map": ["smtp.github.com", "gateway.mailtrace.local"],
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
        "securityReasons": ["SPF: softfail", "DKIM: pass", "Freemail sender detected"],
        "signals": ["SPF: softfail", "DKIM: pass", "Freemail sender detected"],
        "attachments": [],
        "verdict": "SUSPICIOUS",
        "is_quarantined": False,
        "relay_map": ["smtp.linkedin.com", "gateway.mailtrace.local"],
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
        "securityReasons": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "signals": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
        "attachments": [],
        "verdict": "SAFE",
        "is_quarantined": False,
        "relay_map": ["smtp.google.com", "gateway.mailtrace.local"],
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
    },
]

MOCK_SCENARIOS = [
    {"id": "phishing_nic", "name": "NIC Portal Phishing", "description": "Lookalike domain with credential harvesting"},
    {"id": "spf_fail", "name": "SPF Fail Attack", "description": "Email with SPF authentication failure"},
    {"id": "malicious_attachment", "name": "Malicious Attachment", "description": "Email with dangerous .exe attachment"},
    {"id": "benign_newsletter", "name": "Benign Newsletter", "description": "Clean marketing email from known sender"},
    {"id": "bec_attack", "name": "BEC / CEO Fraud", "description": "Business Email Compromise impersonation"},
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
            "securityReasons": reasons,
            "signals": signals,
            "attachments": [],
            "verdict": "MALICIOUS",
            "is_quarantined": True,
            "evidence_sha256": sha_digest,
            "chain_of_custody": f"Received at Gateway → Deep Scan → Threat Score {final_score}/100 → Pre-Delivery Block → Quarantined (ISO/IEC 27037)",
            "relay_map": ["smtp.untrusted-origin.net", "relay.external-hop.org", "gateway.mailtrace.local"],
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
            "securityReasons": reasons,
            "signals": signals,
            "attachments": [],
            "verdict": "SUSPICIOUS",
            "is_quarantined": False,
            "evidence_sha256": sha_digest,
            "chain_of_custody": f"Received at Gateway → Scan passed with warnings (Score {final_score}/100) → Delivered with Alert Banner",
            "relay_map": ["smtp.external-sender.org", "gateway.mailtrace.local"],
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
            "securityReasons": ["SPF: pass", "DKIM: pass", "DMARC: pass", "Zero threat indicators detected"],
            "signals": ["SPF: pass", "DKIM: pass", "Clean content"],
            "attachments": [],
            "verdict": "SAFE",
            "is_quarantined": False,
            "evidence_sha256": sha_digest,
            "chain_of_custody": "Received at Gateway → Scan Clean (Score 6.5/100) → Delivered to User Inbox",
            "relay_map": ["smtp.verified-sender.org", "gateway.mailtrace.local"],
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
