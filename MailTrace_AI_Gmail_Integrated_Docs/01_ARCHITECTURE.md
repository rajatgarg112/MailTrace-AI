# MailTrace AI --- Gmail-Integrated Architecture

MailTrace AI is a security/forensic engine integrated with Gmail. Gmail
is the primary user environment; an analyst dashboard is optional.

## Runtime

``` text
Gmail → Gmail Integration → FastAPI → Evidence
→ Analysis Engine → Decision Engine → Gmail Action
→ Case + Forensic Report
```

## Analysis Engine

``` text
Email
 ├─ Body → AI Detection
 ├─ Headers → Forensics → SPF/DKIM/DMARC → Relay → IP
 ├─ URLs → URL/Domain Analysis
 └─ Attachments → Static Analysis
                         ↓
                 GeoLocation + TI
                         ↓
                    Correlation
                         ↓
                 Attribution Support
                         ↓
                   Final Risk
```

## Rules

1.  Keep Gmail integration separate from analysis modules.
2.  Analysis must be testable with `.eml` fixtures without Gmail.
3.  External intelligence is enrichment, not a hard dependency.
4.  Preserve evidence before modifying/handling the Gmail message.
5.  Findings should include explainable signals.
6.  Never claim guaranteed attribution.
7.  Never execute untrusted attachments in the core prototype.

## Gmail Integration Boundary

The Gmail integration is an adapter around the analysis engine, not a
replacement for Gmail's native delivery/spam infrastructure.

``` text
Gmail receives/accepts message
        ↓
Gmail/Workspace event
        ↓
Fetch message
        ↓
MailTrace analysis
        ↓
Risk: SAFE / SUSPICIOUS / MALICIOUS / UNKNOWN
        ↓
Supported Gmail action + alert/review
```

The core engine must also run against `.eml` fixtures without Gmail.

## Privacy & Governance

Use scoped OAuth permissions, minimize retained content, protect
evidence at rest/in transit, maintain audit logs, and define
retention/deletion rules. Do not expose tokens or sensitive email
content in logs.

## Decision Principle

No single signal should force the final verdict. Combine AI,
authentication, headers, URLs, attachments, infrastructure intelligence,
GeoLocation context and correlation, while preserving an UNKNOWN state
when evidence is insufficient.
