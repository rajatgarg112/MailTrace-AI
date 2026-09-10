# MailTrace AI — Pre-Delivery Email Security Gateway Scaffold

## 1. Product definition

MailTrace AI is a **pre-delivery email security gateway** with its own webmail-style recipient interface.

The prototype simulates the path an email follows before reaching a user's inbox:

```text
Incoming Message
      ↓
MailTrace Ingress
      ↓
Scan / Analyze
      ↓
Risk + Policy Decision
      ↓
Inbox / Warning / Quarantine / Reject / Hold
```

The system does not require Gmail access. The MailTrace application owns the mailbox and simulates the incoming mail transport for demonstration.

## 2. Primary product flow

```text
                   INCOMING EMAIL
                         │
                         ▼
                  MAILTRACE INGRESS
                         │
                         ▼
                EVIDENCE PRESERVATION
                  SHA-256 + timestamp
                         │
                         ▼
                    FAST PARSER
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
       HEADERS          BODY         FILES/URLS
          │              │               │
          ▼              ▼               ▼
       FORENSICS       AI/ML       URL + ATTACHMENT
          │              │               │
          └──────────────┼───────────────┘
                         ▼
                GEO/IP + THREAT INTEL
                         ▼
                    CORRELATION
                         ▼
                    RISK ENGINE
                         ▼
                 DELIVERY POLICY
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          DELIVER       WARN     QUARANTINE
             │           │           │
             ▼           ▼           ▼
           INBOX     INBOX+BADGE  SECURITY STORE
                         │
                         ▼
                 CASE / FORENSIC REPORT
```

## 3. Performance-first architecture

The system should be designed for **near-real-time delivery**. Independent checks run concurrently rather than as a long sequential chain.

Recommended target for the SIH prototype:

> **Typical email: approximately 1–3 seconds from receipt to final delivery decision.**

Large attachments, deep URL analysis, external threat-intelligence services or sandboxing can take longer. The UI must never fake a fixed scan duration; it should display actual status/timing from the backend.

## 4. MailTrace interface

```text
MailTrace Mail
├── Inbox
├── Starred
├── Sent
├── Drafts
├── Trash
├── Quarantine
└── Search
```

The inbox receives only messages that pass the delivery policy.

For a new incoming message, the UI can show a delivery activity panel:

```text
Incoming message from alice@example.com

✓ Received
✓ Parsed
✓ Header analysis
✓ AI analysis
✓ URL analysis
✓ Correlation
✓ Decision: SAFE

Delivered to Inbox — 1.42 s
```

For a malicious message:

```text
Incoming message from suspicious@example.com

✓ Received
✓ Parsed
✓ Header analysis
✓ AI analysis
✓ URL analysis
✓ Correlation
⚠ Decision: MALICIOUS

Quarantined — 1.87 s
```

## 5. Repository structure

```text
mailtrace-ai/
├── database/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── deliveries.py
│   │   │   ├── mailbox.py
│   │   │   ├── messages.py
│   │   │   ├── quarantine.py
│   │   │   ├── cases.py
│   │   │   └── reports.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ingress_service.py
│   │   │   ├── delivery_service.py
│   │   │   ├── analysis_orchestrator.py
│   │   │   ├── policy_service.py
│   │   │   ├── case_service.py
│   │   │   └── report_service.py
│   │   └── core/
│   ├── analysis/
│   │   ├── parser.py
│   │   ├── detection.py
│   │   ├── header_forensics.py
│   │   ├── authentication.py
│   │   ├── origin.py
│   │   ├── geolocation.py
│   │   ├── url_analysis.py
│   │   ├── attachment_analysis.py
│   │   ├── domain_intel.py
│   │   ├── reputation.py
│   │   ├── correlation.py
│   │   └── decision_engine.py
│   ├── integrations/
│   │   └── future_mail_transport/
│   ├── reporting/
│   │   └── forensic_report.py
│   └── tests/
├── frontend/
│   └── mailtrace-mail/
│       ├── src/
│       │   ├── pages/
│       │   ├── components/
│       │   ├── services/
│       │   └── data/
│       └── package.json
├── data/
│   ├── demo/
│   └── uploads/
```

## 6. Delivery states

```text
RECEIVED
  ↓
SCANNING
  ↓
DECIDING
  ├── DELIVERED
  ├── WARNING
  ├── QUARANTINED
  ├── REJECTED
  └── HOLD
```

## 7. Core pillars

1. Pre-delivery AI threat detection
2. Email/header forensics
3. GeoLocation & origin intelligence
4. URL and attachment analysis
5. Threat intelligence
6. Infrastructure correlation
7. Evidence preservation
8. Forensic reporting
9. Delivery-time latency measurement
10. Standalone mail interface
