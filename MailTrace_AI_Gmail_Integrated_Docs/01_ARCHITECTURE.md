# MailTrace AI — Pre-Delivery Email Security Architecture

## 1. Product goal

MailTrace is a **mail-delivery security gateway** for the prototype. An incoming message is accepted by the MailTrace mail server, analyzed before it is placed in the recipient inbox, and only then delivered to the MailTrace mailbox.

The project does not require access to Gmail's database, Gmail backend, or Google internal mail infrastructure. The MailTrace prototype owns the complete demonstration mail path.

## 2. Core delivery flow

```text
Incoming Email / Demo SMTP Event
            ↓
      MailTrace Ingress
            ↓
      Evidence Capture
            ↓
   Fast Parallel Analysis
   ┌────────┬────────┬──────────┐
   ↓        ↓        ↓          ↓
 Headers   Body     URLs   Attachments
   ↓        ↓        ↓          ↓
 Auth    AI/ML    Reputation  Static Scan
   └────────┴────────┴──────────┘
            ↓
      Correlation Engine
            ↓
        Risk Decision
            ↓
   ┌────────┼──────────┐
   ↓        ↓          ↓
 DELIVER  WARN/REVIEW  QUARANTINE
   ↓        ↓          ↓
 Inbox   Inbox+Badge  Security Store
```

## 3. Delivery-time security principle

The important architectural change is that **security analysis happens before normal inbox delivery**. The recipient should not first receive an uninspected message and then click an on-demand scan button.

The application therefore models an email-security gateway:

```text
SMTP-like ingress → MailTrace scanner → decision → mailbox delivery
```

For the demo, SMTP can be simulated through an API endpoint or local message generator. A real SMTP/MTA integration can be added later.

## 4. Latency target

The prototype should target **near-real-time delivery**, not a long manual scan. Recommended engineering target:

- normal email: approximately **1–3 seconds end-to-end** in the demo environment;
- lightweight suspicious email: approximately **1–4 seconds**;
- attachment or external-intelligence-heavy messages may take longer;
- the UI must show `SCANNING` while analysis is in progress.

Do not present these values as a guaranteed SLA for every production deployment. External threat-intelligence services and sandboxing can introduce variable latency.

## 5. Parallel analysis

To achieve delivery-time performance, independent checks should execute concurrently:

```text
                 Message
                    ↓
             Parse / Normalize
                    ↓
       ┌────────────┼────────────┐
       ↓            ↓            ↓
   Header/Auth    AI/ML       URL/Domain
       ↓            ↓            ↓
       └────────────┼────────────┘
                    ↓
             Attachment Scan
                    ↓
             Correlation/Risk
                    ↓
                 Decision
```

Use asynchronous jobs or concurrent workers where appropriate. The final decision waits only for the evidence required by the configured policy.

## 6. MailTrace Mail interface

The frontend remains a Gmail-like **demonstration mailbox**, but the mailbox is downstream of the security gateway.

Screens:

- Inbox
- Sent
- Drafts
- Trash
- Quarantine
- Search
- Compose
- Message detail
- Security/case view

The inbox should display a message only after the delivery decision is recorded, except when a policy explicitly allows a warning delivery.

## 7. Delivery states

```text
RECEIVED → SCANNING → DELIVERED
                    ↘ WARNING
                    ↘ QUARANTINED
                    ↘ REJECTED
                    ↘ FAILED/UNKNOWN
```

`UNKNOWN` must not automatically mean safe. The configured policy determines whether an unknown result is delivered with a warning, held for review, or temporarily deferred.

## 8. Components

```text
Frontend
  ↓
Mail API / Delivery API
  ↓
Ingress Service
  ↓
Analysis Orchestrator
  ├── Parser
  ├── Header Forensics
  ├── Authentication Analysis
  ├── AI/ML Detection
  ├── URL/Domain Analysis
  ├── Attachment Analysis
  ├── Geo/IP Intelligence
  ├── Threat Intelligence
  └── Correlation + Risk Engine
  ↓
Delivery Policy Engine
  ↓
Mailbox / Quarantine / Reject Store
```

## 9. Security boundary

- No Gmail OAuth is required.
- No Google database access is claimed.
- No Gmail SMTP interception is claimed.
- Attachments are treated as untrusted input.
- External intelligence is optional and must have timeouts.
- Evidence is hashed and timestamped.
- Failed intelligence checks are represented explicitly.
