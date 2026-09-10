# MailTrace AI — Setup & Team Workflow

## 1. Development goal

Build MailTrace as a self-contained email-security gateway with its own demonstration mailbox. No Gmail credentials are required.

## 2. Local services

Recommended development setup:

```text
Frontend      React + Vite
Backend       FastAPI
Database      SQLite (demo)
               ↓
            PostgreSQL (production target)
Analysis      Python modules / ML service
Reports       ReportLab
```

## 3. Running the demo

```text
Start backend
      ↓
Start frontend
      ↓
Open MailTrace Mail
      ↓
Click “Send Test Email”
      ↓
Observe Receiving → Scanning → Decision
      ↓
SAFE → Inbox
MALICIOUS → Quarantine
```

## 4. Team split

### Frontend
Build:

- MailTrace webmail UI;
- live delivery status;
- inbox/quarantine;
- security verdict card;
- evidence view.

### Backend / delivery gateway
Build:

- delivery endpoint;
- message persistence;
- orchestration;
- policy engine;
- timing/audit events.

### AI/ML
Build:

- NLP classifier;
- feature extraction;
- explainable signals;
- model versioning.

### Forensics / intelligence
Build:

- header parser;
- SPF/DKIM/DMARC interpretation;
- URL/domain analysis;
- attachment inspection;
- IP/GeoLocation/TI enrichment;
- correlation.

### Reporting / QA
Build:

- case management;
- evidence hashes;
- forensic reports;
- test fixtures;
- latency benchmarks.

## 5. Git workflow

Use small feature branches:

```text
main
 ├── feature/delivery-gateway
 ├── feature/mail-ui
 ├── feature/ai-detection
 ├── feature/header-forensics
 ├── feature/url-attachment-analysis
 └── feature/reporting
```

Do not commit secrets, API keys, private mail or real user credentials.

## 6. SIH demonstration script

1. Open MailTrace Mail.
2. Click `Send Test Email`.
3. Show `Receiving`.
4. Show `Scanning` with parallel analysis stages.
5. Show the final verdict before the message reaches Inbox.
6. For a benign email, show `SAFE → Delivered`.
7. For phishing, show `MALICIOUS → Quarantined`.
8. Open the security result and evidence.
9. Show delivery latency and the forensic timeline.

## 7. Product boundary

The prototype represents the architecture of a **pre-delivery email security gateway**. It does not claim direct access to Gmail's backend or guaranteed control over Gmail delivery. A future deployment can connect the same analysis engine to an authorized mail transport layer.
