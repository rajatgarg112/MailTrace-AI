# MailTrace AI — Pre-Delivery Email Security Gateway + Mail Interface

MailTrace AI is a standalone email-security platform designed to demonstrate **threat detection during email delivery**. It owns the demonstration mail path, so it does not require access to Gmail's database, Gmail backend, Google internal mail infrastructure, or a real Gmail account.

The project provides a familiar webmail interface as the recipient mailbox, but the key product behavior happens **before the message enters Inbox**.

## Core idea

```text
Incoming Email
      ↓
MailTrace Ingress
      ↓
Evidence Capture
      ↓
Fast Parallel Security Analysis
      ├── AI/NLP threat detection
      ├── Header forensics
      ├── SPF/DKIM/DMARC analysis
      ├── URL/domain analysis
      ├── Attachment analysis
      ├── Origin/GeoLocation
      ├── Threat intelligence
      └── Infrastructure correlation
      ↓
Risk Engine
      ↓
Delivery Policy
  ┌───┼────────┬────────┐
  ↓   ↓        ↓        ↓
DELIVER WARN  QUARANTINE REJECT/HOLD
  ↓   ↓        ↓
 Inbox Inbox+   Security Store
      Warning
```

## What changed from a Gmail-extension concept?

| Gmail-dependent concept | MailTrace delivery-time design |
|---|---|
| Gmail inbox | MailTrace-owned mailbox |
| Gmail API | MailTrace Delivery/Mail API |
| Gmail database | MailTrace SQLite/PostgreSQL database |
| Gmail add-on | Native MailTrace security UI |
| Manual “Analyze” button | Automatic analysis during delivery |
| Gmail labels | MailTrace delivery/security states |
| Gmail quarantine | MailTrace quarantine store |
| Gmail SMTP interception | Simulated MailTrace ingress for prototype |
| Gmail OAuth | Not required |

## Delivery-time objective

MailTrace should behave like a security gateway:

```text
RECEIVED → SCANNING → DECISION → DELIVERED / QUARANTINED
```

For the SIH prototype, target approximately **1–3 seconds end-to-end for a typical email** on the local environment. This is a development target, not a universal production SLA. External intelligence, sandboxing and large attachments can increase latency.

## MailTrace Mail UI

The application includes:

- Inbox
- Sent
- Drafts
- Trash
- Quarantine
- Search
- Compose
- Message detail
- Live delivery/scanning status
- Security verdict and evidence panel

The important UI difference is that the recipient sees:

```text
New email detected
        ↓
MailTrace is scanning...
        ↓
SAFE → Delivered to Inbox

or
MALICIOUS → Quarantined
```

## Demo scenarios

Provide one-click test deliveries:

- Benign email
- Phishing email
- Spoofed sender
- Executive impersonation
- BEC/payment diversion
- Suspicious URL
- Suspicious attachment

Each scenario must pass through the same delivery gateway instead of being inserted directly into Inbox.

## Core pillars

1. Pre-delivery AI-powered threat detection
2. Header and email forensics
3. GeoLocation and origin analysis
4. URL and attachment analysis
5. Threat intelligence
6. Sender/domain/IP correlation
7. Evidence preservation
8. Forensic reporting
9. Delivery-time performance measurement
10. Standalone demonstration mailbox

## Reading order

1. `scaffold.md`
2. `01_ARCHITECTURE.md`
3. `02_DATA_MODEL.md`
4. `03_ANALYSIS_PIPELINE.md`
5. `04_API_SPEC.md`
6. `05_EVIDENCE_AND_REPORTING.md`
7. `06_TESTING.md`
8. `07_SETUP_AND_TEAM_WORKFLOW.md`

## Product boundary

MailTrace owns the demonstration delivery path and mailbox. It must not claim direct access to Google's private databases or Gmail's internal delivery infrastructure. A future authorized integration can connect the same gateway/analysis engine to an actual mail transport system.

Final risk states:

`SAFE | SUSPICIOUS | MALICIOUS | UNKNOWN`

Delivery actions:

`DELIVER | WARN | QUARANTINE | REJECT | HOLD`

Missing intelligence must never be silently treated as proof that a message is safe.
