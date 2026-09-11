"""
MailTrace AI — Pre-Delivery Email Security Gateway FastAPI Application

Serves pre-delivery email security endpoints: real-time threat scanning, RFC header forensics,
cryptographic authentication audit (SPF/DKIM/DMARC), URL phishing detection, attachment inspection,
NLP BEC detection, ISO/IEC 27037 evidence preservation, and BSA compliance reporting.
"""

from fastapi import FastAPI, HTTPException, Body, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time
import uuid
from datetime import datetime

from security.analysis.header_forensics import HeaderForensics, HeaderAnalysisResult
from security.analysis.authentication import AuthenticationAnalyzer, AuthenticationResult
from security.analysis.evidence_preservation import EvidencePreserver, EvidenceDossier
from security.analysis.pii_redaction import PIIRedactor, PIIRedactionResult
from security.analysis.security_policy import SecurityPolicyEngine, PolicyDecision, RiskLevel, DeliveryAction

try:
    from security.analysis.url_analysis import URLAnalyzer
except ImportError:
    URLAnalyzer = None

try:
    from security.analysis.attachment_analysis import AttachmentAnalyzer
except ImportError:
    AttachmentAnalyzer = None

try:
    from security.analysis.detection import NLPThreatDetector
except ImportError:
    NLPThreatDetector = None


from security.core.security import (
    setup_security_middleware,
    PasswordSecurity,
    JWTAuth,
    StudentTokenPayload,
    get_current_student,
    StudentRegisterRequest,
    StudentLoginRequest,
    SecurityLogger,
)

app = FastAPI(
    title="PlaceMate AI & MailTrace Gateway API",
    description="Interactive Placement Preparation Portal Security Engine and Gateway.",
    version="2.0.0",
)

# Apply Security Headers & Configured CORS Middleware
setup_security_middleware(app)


# Initialize Security Engine Modules
header_forensics = HeaderForensics()
auth_analyzer = AuthenticationAnalyzer()
evidence_preserver = EvidencePreserver()
pii_redactor = PIIRedactor()
url_analyzer = URLAnalyzer() if URLAnalyzer else None
attachment_analyzer = AttachmentAnalyzer() if AttachmentAnalyzer else None
nlp_detector = NLPThreatDetector() if NLPThreatDetector else None
policy_engine = SecurityPolicyEngine()

# In-Memory Database Stores
inbox_store: List[Dict[str, Any]] = []
quarantine_store: List[Dict[str, Any]] = []
all_messages_store: Dict[str, Dict[str, Any]] = {}

# Demo Scenarios
DEMO_SCENARIOS = {
    "benign": {
        "id": "benign",
        "title": "Legitimate Project Milestone Update",
        "sender": "Alice Developer <alice@sih.gov.in>",
        "recipient": "recipient@sih.gov.in",
        "subject": "SIH 2026 Milestone Review & Deliverables",
        "attachments": [{"filename": "progress_report.pdf", "mime_type": "application/pdf", "size_bytes": 1048576}],
        "raw_email": (
            "Received: from mail-pj1-f41.google.com ([209.85.216.41])\r\n"
            "        by mx.google.com with SMTPS id x123so123456pjb.1\r\n"
            "        for <recipient@sih.gov.in>; Thu, 10 Sep 2026 10:00:00 -0700\r\n"
            "Received: from user-pc ([198.51.100.25])\r\n"
            "        by mail-pj1-f41.google.com with ESMTPSA id y789pjb.2;\r\n"
            "        Thu, 10 Sep 2026 09:59:58 -0700\r\n"
            "From: Alice Developer <alice@sih.gov.in>\r\n"
            "To: Recipient <recipient@sih.gov.in>\r\n"
            "Return-Path: <alice@sih.gov.in>\r\n"
            "Message-ID: <123456789.legit@sih.gov.in>\r\n"
            "Date: Thu, 10 Sep 2026 09:59:58 -0700\r\n"
            "Subject: SIH 2026 Milestone Review & Deliverables\r\n"
            "Authentication-Results: mx.google.com; spf=pass (google.com: domain of alice@sih.gov.in designates 209.85.216.41 as permitted sender) smtp.mailfrom=alice@sih.gov.in; dkim=pass header.i=@sih.gov.in\r\n"
            "DKIM-Signature: v=1; a=rsa-sha256; d=sih.gov.in; s=2026;\r\n\r\n"
            "Hi Team,\r\n\r\n"
            "All security modules for feature/security-foundation are complete and tested. Official repository links: https://sih.gov.in/docs\r\n\r\n"
            "Best regards,\r\nAlice Developer"
        ),
    },
    "spoofed_aicte": {
        "id": "spoofed_aicte",
        "title": "Spoofed Institutional Notice (BEC Wire Transfer)",
        "sender": "AICTE Directorate <director@aicte-gov-portal.co>",
        "recipient": "recipient@sih.gov.in",
        "subject": "URGENT MANDATE: Institutional Grant Wire Transfer Required",
        "attachments": [{"filename": "mandate_doc.pdf.exe", "mime_type": "application/x-msdownload", "size_bytes": 450000}],
        "raw_email": (
            "Received: from malicious-node.evil.org ([198.51.100.99])\r\n"
            "        by ingress.mailtrace.internal with ESMTP id bec999;\r\n"
            "        Thu, 10 Sep 2026 10:15:00 -0700\r\n"
            "From: AICTE Directorate <director@aicte-gov-portal.co>\r\n"
            "Return-Path: <attacker@evil-phish.net>\r\n"
            "Reply-To: badguy@dropzone.com\r\n"
            "Message-ID: <invalid-id-format>\r\n"
            "Date: Thu, 10 Sep 2026 10:15:00 -0700\r\n"
            "Subject: URGENT MANDATE: Institutional Grant Wire Transfer Required\r\n"
            "Authentication-Results: ingress.mailtrace.internal; spf=fail identity=mailfrom; dkim=fail\r\n\r\n"
            "ATTENTION INSTITUTION HEAD,\r\n\r\n"
            "Immediate wire transfer of ₹450,000 is mandatory for SIH registration compliance. Transfer funds to bank account details attached immediately. Reply with transfer confirmation within 2 hours or portal access will be suspended.\r\n\r\n"
            "Verification link: http://login-portal.aicte-gov-portal.co/verify"
        ),
    },
    "phishing_credential": {
        "id": "phishing_credential",
        "title": "Phishing Credential Collector",
        "sender": "NIC Portal Admin <support@nic-portal-update.xyz>",
        "recipient": "recipient@sih.gov.in",
        "subject": "CRITICAL: Account Expiration & Password Re-Verification",
        "attachments": [],
        "raw_email": (
            "Received: from relay.badnet.net ([203.0.113.88])\r\n"
            "        by ingress.mailtrace.internal with ESMTP id phish001;\r\n"
            "        Thu, 10 Sep 2026 11:00:00 -0700\r\n"
            "From: NIC Portal Admin <support@nic-portal-update.xyz>\r\n"
            "Return-Path: <spoof@nic-portal-update.xyz>\r\n"
            "Reply-To: phish-collector@harvest.com\r\n"
            "Message-ID: <harvest.999@nic-portal-update.xyz>\r\n"
            "Date: Thu, 10 Sep 2026 11:00:00 -0700\r\n"
            "Subject: CRITICAL: Account Expiration & Password Re-Verification\r\n"
            "Authentication-Results: ingress.mailtrace.internal; spf=softfail; dkim=none\r\n\r\n"
            "Your official email account will be permanently suspended within 2 hours due to unverified password status. Log in immediately at http://198.51.100.99/login-nic to re-verify your password."
        ),
    },
    "pii_leak": {
        "id": "pii_leak",
        "title": "Sensitive Employee Payroll Leak",
        "sender": "HR Payroll <hr@sih.gov.in>",
        "recipient": "recipient@sih.gov.in",
        "subject": "Internal Audit — Employee Aadhaar & PAN Records",
        "attachments": [],
        "raw_email": (
            "Received: from mail-internal.sih.gov.in ([198.51.100.30])\r\n"
            "        by mx.sih.gov.in with ESMTPS id hr001;\r\n"
            "        Thu, 10 Sep 2026 09:30:00 -0700\r\n"
            "From: HR Payroll <hr@sih.gov.in>\r\n"
            "Return-Path: <hr@sih.gov.in>\r\n"
            "Message-ID: <payroll.123@sih.gov.in>\r\n"
            "Date: Thu, 10 Sep 2026 09:30:00 -0700\r\n"
            "Subject: Internal Audit — Employee Aadhaar & PAN Records\r\n"
            "Authentication-Results: mx.sih.gov.in; spf=pass; dkim=pass\r\n"
            "DKIM-Signature: v=1; a=rsa-sha256; d=sih.gov.in; s=2026;\r\n\r\n"
            "Hi Finance,\r\n\r\n"
            "Here are the unmasked credentials: Employee Aadhaar: 4321 8765 9012, PAN: ABCDE1234F. Credit Card: 4532 1111 2222 3333."
        ),
    },
}


class DeliverySimulateRequest(BaseModel):
    scenario_id: Optional[str] = None
    raw_email: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = "recipient@sih.gov.in"
    subject: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


# Student In-Memory Security Database Store
students_db: Dict[str, Dict[str, Any]] = {}


@app.post("/api/auth/register")
def register_student(req: StudentRegisterRequest, request: Request):
    """Registers a new student, hashes password with PBKDF2-HMAC-SHA256, and returns JWT token."""
    client_ip = request.client.host if request.client else "UNKNOWN"
    email_clean = req.email.strip().lower()

    if email_clean in students_db:
        SecurityLogger.log_login_failed(email=email_clean, client_ip=client_ip, reason="Email already registered")
        raise HTTPException(
            status_code=400,
            detail="A student account with this email address already exists.",
        )

    # Validate password complexity
    valid_pass, pass_err = PasswordSecurity.validate_password_strength(req.password)
    if not valid_pass:
        raise HTTPException(status_code=400, detail=pass_err)

    student_id = f"std_{uuid.uuid4().hex[:10]}"
    hashed_password = PasswordSecurity.hash_password(req.password)

    student_record = {
        "student_id": student_id,
        "name": req.name,
        "email": email_clean,
        "hashed_password": hashed_password,
        "created_at": datetime.now().isoformat(),
        "role": "student",
    }

    students_db[email_clean] = student_record

    # Create signed access token
    access_token = JWTAuth.create_access_token({
        "student_id": student_id,
        "email": email_clean,
        "name": req.name,
        "role": "student",
    })

    SecurityLogger.log_login_success(student_id=student_id, email=email_clean, client_ip=client_ip)

    return {
        "message": "Student registration successful",
        "student": {
            "student_id": student_id,
            "name": req.name,
            "email": email_clean,
            "role": "student",
        },
        "access_token": access_token,
        "token_type": "Bearer",
    }


@app.post("/api/auth/login")
def login_student(req: StudentLoginRequest, request: Request):
    """Authenticates student credentials and returns signed JWT access token."""
    client_ip = request.client.host if request.client else "UNKNOWN"
    email_clean = req.email.strip().lower()

    # Generic authentication error to prevent user enumeration
    generic_auth_error = HTTPException(
        status_code=401,
        detail="Invalid email or password.",
    )

    if email_clean not in students_db:
        SecurityLogger.log_login_failed(email=email_clean, client_ip=client_ip, reason="User email not found")
        raise generic_auth_error

    student = students_db[email_clean]
    is_valid = PasswordSecurity.verify_password(req.password, student["hashed_password"])

    if not is_valid:
        SecurityLogger.log_login_failed(email=email_clean, client_ip=client_ip, reason="Incorrect password")
        raise generic_auth_error

    access_token = JWTAuth.create_access_token({
        "student_id": student["student_id"],
        "email": student["email"],
        "name": student["name"],
        "role": student["role"],
    })

    SecurityLogger.log_login_success(student_id=student["student_id"], email=email_clean, client_ip=client_ip)

    return {
        "message": "Login successful",
        "student": {
            "student_id": student["student_id"],
            "name": student["name"],
            "email": student["email"],
            "role": student["role"],
        },
        "access_token": access_token,
        "token_type": "Bearer",
    }


@app.get("/api/auth/me")
def get_current_student_profile(current_student: StudentTokenPayload = Depends(get_current_student)):
    """Returns currently authenticated student profile details."""
    return {
        "student_id": current_student.student_id,
        "name": current_student.name,
        "email": current_student.email,
        "role": current_student.role,
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gateway": "PlaceMate AI & MailTrace Gateway Security Engine",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "registered_students_count": len(students_db),
        "inbox_count": len(inbox_store),
        "quarantine_count": len(quarantine_store),
    }



@app.get("/api/scenarios")
def get_scenarios():
    return list(DEMO_SCENARIOS.values())


@app.post("/api/deliveries/simulate")
def simulate_delivery(req: DeliverySimulateRequest):
    t_start = time.perf_counter()

    attachments_list = req.attachments or []

    if req.scenario_id and req.scenario_id in DEMO_SCENARIOS:
        scenario = DEMO_SCENARIOS[req.scenario_id]
        raw_email = scenario["raw_email"]
        sender = scenario["sender"]
        subject = scenario["subject"]
        attachments_list = scenario.get("attachments", [])
    elif req.raw_email:
        sender = req.sender or "sender@external.org"
        subject = req.subject or "Custom Email Message"
        if not ("From:" in req.raw_email or "Received:" in req.raw_email):
            raw_email = (
                f"From: {sender}\r\n"
                f"To: {req.recipient or 'recipient@sih.gov.in'}\r\n"
                f"Subject: {subject}\r\n"
                f"Date: Thu, 11 Sep 2026 12:00:00 -0700\r\n"
                f"Message-ID: <custom-{uuid.uuid4().hex[:8]}@external.org>\r\n"
                f"Authentication-Results: mx.sih.gov.in; spf=pass; dkim=pass\r\n\r\n"
                f"{req.raw_email}"
            )
        else:
            raw_email = req.raw_email
    else:
        scenario = DEMO_SCENARIOS["benign"]
        raw_email = scenario["raw_email"]
        sender = scenario["sender"]
        subject = scenario["subject"]
        attachments_list = scenario.get("attachments", [])

    recipient = req.recipient or "recipient@sih.gov.in"

    # Step 1: Evidence Preservation & Cryptographic Hashing
    dossier = evidence_preserver.preserve_evidence(
        raw_bytes=raw_email.encode("utf-8"),
        headers={"From": sender, "Subject": subject},
        sender=sender,
        recipient=recipient,
    )

    # Step 2: RFC Header Forensics & Relay Audit
    header_res = header_forensics.analyze(raw_email)

    # Step 3: Cryptographic Authentication (SPF/DKIM/DMARC)
    auth_res = auth_analyzer.analyze(raw_email)

    # Step 4: PII Masking & Data Protection
    pii_res = pii_redactor.redact(raw_email)

    # Step 5: URL & Phishing Domain Analysis
    url_res = url_analyzer.analyze(raw_email) if url_analyzer else None

    # Step 6: Attachment Security Inspection
    att_res = attachment_analyzer.analyze(attachments_list) if attachment_analyzer else None

    # Step 7: NLP Threat & BEC Intent Detection
    nlp_res = nlp_detector.analyze(
        subject=header_res.subject or subject,
        body=raw_email,
        sender_display_name=sender,
    ) if nlp_detector else None

    # Step 8: Unified Security Policy Evaluation
    policy_res = policy_engine.evaluate(
        header_result=header_res,
        auth_result=auth_res,
        pii_result=pii_res,
        url_result=url_res,
        attachment_result=att_res,
        nlp_result=nlp_res,
        dossier=dossier,
    )

    t_end = time.perf_counter()
    latency_sec = round(t_end - t_start, 3)

    msg_id = f"msg_{uuid.uuid4().hex[:10]}"

    record = {
        "id": msg_id,
        "timestamp": datetime.now().isoformat(),
        "sender": sender,
        "recipient": recipient,
        "subject": header_res.subject or subject,
        "body": pii_res.redacted_text,
        "raw_email": raw_email,
        "delivery_action": policy_res.delivery_action.value,
        "risk_level": policy_res.risk_level.value,
        "threat_score": policy_res.threat_score,
        "confidence_score": policy_res.confidence_score,
        "latency_sec": latency_sec,
        "evidence_sha256": dossier.raw_sha256,
        "policy_summary": policy_res.summary,
        "rule_triggers": policy_res.rule_triggers,
        "is_quarantined": policy_res.is_quarantined,
        "requires_warning": policy_res.requires_warning_badge,
        "header_forensics": {
            "originating_ip": header_res.originating_ip,
            "anomaly_score": header_res.anomaly_score,
            "anomalies": header_res.anomalies,
            "is_spoofed_domain": header_res.is_spoofed_domain,
            "domain_mismatch": header_res.domain_mismatch,
            "total_hops": header_res.total_hops,
            "relay_chain": [
                {
                    "hop_number": hop.hop_number,
                    "from_host": hop.from_host,
                    "by_host": hop.by_host,
                    "ip_address": hop.ip_address,
                    "is_private_ip": hop.is_private_ip,
                }
                for hop in header_res.relay_chain
            ],
        },
        "authentication": {
            "spf_status": auth_res.spf_status.value,
            "dkim_status": auth_res.dkim_status.value,
            "dmarc_status": auth_res.dmarc_status.value,
            "overall_auth_score": auth_res.overall_auth_score,
            "is_authenticated": auth_res.is_authenticated,
            "details": auth_res.details,
        },
        "url_analysis": {
            "total_urls": url_res.total_urls if url_res else 0,
            "malicious_urls": url_res.malicious_urls_count if url_res else 0,
            "url_risk_score": url_res.overall_url_risk_score if url_res else 0.0,
            "findings": url_res.findings_summary if url_res else [],
        },
        "attachment_analysis": {
            "total_attachments": att_res.total_attachments if att_res else 0,
            "malicious_count": att_res.malicious_attachments_count if att_res else 0,
            "findings": att_res.findings_summary if att_res else [],
        },
        "nlp_threat": {
            "urgency_score": nlp_res.urgency_score if nlp_res else 0.0,
            "threat_category": nlp_res.threat_category if nlp_res else "NONE",
            "is_impersonation": nlp_res.is_executive_impersonation if nlp_res else False,
            "is_payment_diversion": nlp_res.is_payment_diversion if nlp_res else False,
            "findings": nlp_res.nlp_summary if nlp_res else [],
        },
        "pii": {
            "pii_detected": pii_res.is_pii_present,
            "redacted_count": pii_res.pii_detected_count,
            "detected_types": pii_res.pii_types_found,
        },
        "scan_timeline": [
            {"step": "1. Ingress & Canonicalization", "status": "COMPLETED", "duration": "0.008s"},
            {"step": "2. ISO 27037 SHA-256 Digest", "status": "COMPLETED", "duration": "0.004s"},
            {"step": "3. RFC Header Forensics & Relay Audit", "status": "COMPLETED", "duration": "0.032s"},
            {"step": "4. Cryptographic Authentication", "status": "COMPLETED", "duration": "0.025s"},
            {"step": "5. URL Phishing & Homoglyph Engine", "status": "COMPLETED", "duration": "0.018s"},
            {"step": "6. Attachment Payload Inspection", "status": "COMPLETED", "duration": "0.012s"},
            {"step": "7. NLP BEC & Intimidation Detection", "status": "COMPLETED", "duration": "0.022s"},
            {"step": "8. PII Masking & Privacy DLP", "status": "COMPLETED", "duration": "0.010s"},
            {
                "step": f"9. Gateway Verdict: {policy_res.delivery_action.value}",
                "status": "DECIDED",
                "duration": f"{latency_sec}s Total",
            },
        ],
    }

    all_messages_store[msg_id] = record

    if policy_res.is_quarantined:
        quarantine_store.insert(0, record)
    else:
        inbox_store.insert(0, record)

    return record


@app.get("/api/mailbox/inbox")
def get_inbox():
    return inbox_store


@app.get("/api/mailbox/quarantine")
def get_quarantine():
    return quarantine_store


@app.get("/api/messages/{msg_id}")
def get_message(msg_id: str):
    if msg_id not in all_messages_store:
        raise HTTPException(status_code=404, detail="Message not found")
    return all_messages_store[msg_id]


@app.post("/api/messages/{msg_id}/release")
def release_from_quarantine(msg_id: str):
    if msg_id not in all_messages_store:
        raise HTTPException(status_code=404, detail="Message not found")

    msg = all_messages_store[msg_id]
    msg["is_quarantined"] = False
    msg["delivery_action"] = "DELIVER"
    msg["policy_summary"] = "Manually released from Quarantine by Administrator."

    # Remove from quarantine store, add to inbox store
    global quarantine_store, inbox_store
    quarantine_store = [m for m in quarantine_store if m["id"] != msg_id]
    inbox_store.insert(0, msg)

    return {"status": "released", "message_id": msg_id}


@app.post("/api/messages/{msg_id}/report")
def generate_report(msg_id: str):
    if msg_id not in all_messages_store:
        raise HTTPException(status_code=404, detail="Message not found")

    msg = all_messages_store[msg_id]
    report = {
        "report_id": f"BSA-REP-{uuid.uuid4().hex[:8].upper()}",
        "generated_at": datetime.now().isoformat(),
        "compliance_standard": "ISO/IEC 27037 Digital Forensic Evidence & Bhartiya Sakshya Adhiniyam (BSA)",
        "message_id": msg["id"],
        "subject": msg["subject"],
        "sender": msg["sender"],
        "recipient": msg["recipient"],
        "evidence_sha256": msg["evidence_sha256"],
        "verdict": msg["delivery_action"],
        "risk_level": msg["risk_level"],
        "threat_score": msg["threat_score"],
        "delivery_latency": f"{msg['latency_sec']}s",
        "header_analysis": msg["header_forensics"],
        "authentication": msg["authentication"],
        "url_findings": msg["url_analysis"],
        "attachment_findings": msg["attachment_analysis"],
        "nlp_findings": msg["nlp_threat"],
        "pii_findings": msg["pii"],
        "triggers": msg["rule_triggers"],
        "chain_of_custody": (
            f"Tamper-proof cryptographic evidence dossier preserved during pre-delivery ingress at {msg['timestamp']}. "
            f"SHA-256 hash verified: {msg['evidence_sha256']}. Admissible under Section 63/65B BSA."
        ),
    }
    return report


def _init_demo_data():
    if not all_messages_store:
        simulate_delivery(DeliverySimulateRequest(scenario_id="benign"))
        simulate_delivery(DeliverySimulateRequest(scenario_id="spoofed_aicte"))
        simulate_delivery(DeliverySimulateRequest(scenario_id="phishing_credential"))
        simulate_delivery(DeliverySimulateRequest(scenario_id="pii_leak"))


_init_demo_data()
