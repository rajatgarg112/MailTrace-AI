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
    Simulate email delivery with mock security scan result.
    Accepts scenario_id or raw email fields.
    """
    scenario_id = payload.get("scenario_id", "")
    sender = payload.get("sender", "test@example.com")
    subject = payload.get("subject", "Test Email")

    # Pick matching quarantine scenario or default to benign
    if scenario_id in ("phishing_nic", "bec_attack", "malicious_attachment") or "phish" in sender.lower():
        mock_result = {
            "id": f"msg_{uuid.uuid4().hex[:6]}",
            "sender": sender or "attacker@evil-domain.xyz",
            "senderEmail": sender or "attacker@evil-domain.xyz",
            "recipient": "user@mailtrace.local",
            "subject": subject or "Urgent Action Required",
            "body": payload.get("raw_email", "Suspicious content detected."),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "QUARANTINED",
            "riskScore": 88.5,
            "threat_score": 88.5,
            "delivery_action": "QUARANTINE",
            "requires_warning": False,
            "securityReasons": ["SPF: FAIL", "Lookalike domain", "Malicious URL detected", "Credential harvesting language"],
            "signals": ["SPF: FAIL", "Lookalike domain", "Malicious URL detected", "Credential harvesting language"],
            "attachments": [],
            "verdict": "MALICIOUS",
            "is_quarantined": True,
            "evidence_sha256": uuid.uuid4().hex,
            "chain_of_custody": "Received → Scanned → ML: phishing (0.92) → Risk Engine → QUARANTINED",
            "relay_map": ["smtp.evil-domain.xyz", "gateway.mailtrace.local"],
        }
        MOCK_QUARANTINE.append(mock_result)
    else:
        mock_result = {
            "id": f"msg_{uuid.uuid4().hex[:6]}",
            "sender": sender,
            "senderEmail": sender,
            "recipient": "user@mailtrace.local",
            "subject": subject,
            "body": payload.get("raw_email", "Clean email content."),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "DELIVERED",
            "riskScore": 8.0,
            "threat_score": 8.0,
            "delivery_action": "DELIVER",
            "requires_warning": False,
            "securityReasons": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
            "signals": ["SPF: pass", "DKIM: pass", "DMARC: pass"],
            "attachments": [],
            "verdict": "SAFE",
            "is_quarantined": False,
            "evidence_sha256": uuid.uuid4().hex,
            "chain_of_custody": "Received → Scanned → ML: benign (0.95) → Risk Engine → DELIVERED",
            "relay_map": ["smtp.example.com", "gateway.mailtrace.local"],

        }
        MOCK_INBOX.append(mock_result)

    return mock_result


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
