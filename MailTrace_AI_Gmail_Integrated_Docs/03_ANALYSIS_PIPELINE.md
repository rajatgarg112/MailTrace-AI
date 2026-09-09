# MailTrace AI --- Gmail Analysis Pipeline

## Phase 0 --- Integration Freeze

Freeze Gmail integration, FastAPI, data contract, database, module
interfaces and decision policy.

## Phase 1 --- Ingestion & Evidence

``` text
Gmail event → Fetch message → Preserve source → SHA-256 → Parse
```

Extract body, headers, URLs, attachments and metadata.

## Phase 2 --- AI Detection

Detect phishing, fraud, impersonation, BEC, credential harvesting and
social engineering.

Baseline: TF-IDF + Logistic Regression/SVM.

## Phase 3 --- Header Forensics

Analyze Return-Path, Received, Message-ID, Reply-To, SPF, DKIM, DMARC,
timestamps and routing anomalies.

Reconstruct the observable relay chain.

## Phase 4 --- Origin, GeoLocation & Intelligence

``` text
Relay Chain → Earliest Reliable Observed IP
→ GeoIP → DNS/WHOIS → Reputation → VPN/TOR/Hosting indicators
```

Also analyze URLs and attachments.

## Phase 5 --- Correlation & Attribution Support

Correlate:

``` text
Sender ↔ Domain ↔ IP ↔ URL ↔ Attachment ↔ Case
```

Produce confidence-based investigative findings.

## Phase 6 --- Decision & Gmail Action

``` text
All Evidence → Final Risk → Safe/Suspicious/Malicious
→ Gmail Action → Case → Report
```

Medium-risk messages should normally go to review rather than
automatically being treated as malicious.

## Decision States

The final engine returns four states:

-   SAFE --- sufficient benign evidence.
-   SUSPICIOUS --- meaningful risk or conflicting signals; review/alert.
-   MALICIOUS --- strong malicious evidence; supported quarantine/label
    workflow.
-   UNKNOWN --- insufficient, unavailable or conflicting evidence; do
    not force a binary claim.

## Alert & Feedback

High-risk and suspicious cases can generate alerts. Analyst/user
feedback is recorded for evaluation, audit and future model improvement.

## Gmail Timing Boundary

The prototype should describe Gmail integration as event-driven
processing after Gmail has accepted/received the message. A Gmail add-on
should not be described as an SMTP interception layer or guaranteed
pre-delivery blocker.
