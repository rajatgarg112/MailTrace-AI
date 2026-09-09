# MailTrace AI --- Testing Strategy

## Core Scenarios

-   legitimate
-   phishing
-   spoofed sender
-   executive impersonation
-   BEC/payment diversion
-   suspicious URL
-   suspicious attachment
-   multi-hop relay
-   missing headers
-   private IP
-   malformed email
-   missing authentication results
-   intelligence outage
-   Gmail API failure
-   duplicate Gmail event

## Module Tests

### AI

Classification, score, model version, false-positive review.

### Forensics

Received parsing, relay ordering, SPF/DKIM/DMARC and anomalies.

### GeoLocation

Public IP lookup, private IP handling, unavailable provider.

### URL/Attachment

Extraction, type validation, hashes, suspicious indicators and failure
handling.

### Correlation

Entities, relationships, confidence and rationale.

### Gmail

Event handling, fetch, labels/actions, idempotency and permission
errors.

## End-to-End

``` text
Gmail Event → Fetch → Hash → Parse → AI
→ Forensics → URL/Attachment → Geo/TI
→ Correlation → Decision → Gmail Action
→ Case → Report
```

Test both legitimate and malicious flows.

## Required Decision-State Tests

-   clearly benign → SAFE
-   clear phishing/malware indicators → MALICIOUS
-   mixed/ambiguous signals → SUSPICIOUS
-   unavailable/conflicting evidence → UNKNOWN

## Alert & Feedback Tests

-   high-risk alert is generated
-   suspicious review alert is generated
-   no alert for normal safe mail
-   analyst feedback is stored
-   feedback does not silently change the current verdict

## Gmail Boundary Tests

Verify that the system handles Gmail events asynchronously and does not
claim or depend on SMTP-level interception.
