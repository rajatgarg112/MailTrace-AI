# MailTrace AI --- Gmail-Integrated AI Email Threat Detection, GeoLocation & Forensic Intelligence Platform

## 1. Product Definition

MailTrace AI is not primarily a standalone email-analysis website. It is
a Gmail-integrated security and forensic intelligence tool whose core
engine automatically analyzes incoming emails, URLs, attachments,
headers, sender infrastructure, and related indicators.

### Core pillars

1.  AI-Powered Email Threat Detection
2.  GeoLocation & Origin Analysis
3.  Email Forensics
4.  Threat Intelligence & Infrastructure Correlation
5.  Attribution Support & Investigative Intelligence
6.  Evidence Preservation & Forensic Reporting
7.  Gmail Integration & Automated Mail Handling

An analyst dashboard can be added later, but it is optional and
secondary.

## 2. Primary Product Flow

``` text
GMAIL / GOOGLE WORKSPACE
  ↓
Gmail Integration / Mailbox Event
  ↓
Fetch Message
  ↓
Email Ingestion
  ↓
Evidence Preservation (SHA-256 + timestamp)
  ↓
Email Parser
  ↓
┌──────────────┬───────────────┬──────────────┐
│ BODY         │ HEADERS       │ ATTACHMENTS  │
│ ↓            │ ↓             │ ↓            │
│ AI Detection │ Forensics     │ File Analysis│
└──────┬───────┴───────┬───────┴──────┬───────┘
       │               │              │
       └───────────────┼──────────────┘
                       ↓
                  URL Analysis
                       ↓
             Relay Reconstruction
                       ↓
          Earliest Reliable Observed IP
                       ↓
                  GeoLocation
                       ↓
             DNS / WHOIS / Reputation
                       ↓
              Threat Intelligence
                       ↓
             Graph-Based Correlation
                       ↓
               Attribution Support
                       ↓
                 Final Risk Engine
                       ↓
             ┌──────────┼──────────┬──────────┐
             ↓          ↓          ↓          ↓
           SAFE     SUSPICIOUS  MALICIOUS   UNKNOWN
             ↓          ↓          ↓          ↓
        Normal       Review +   Quarantine/  Review/
        Handling       Alert       Label     No forced claim
                       ↓
                Forensic Case
                       ↓
          Integrity-Verifiable Report
```

## 3. Repository Structure

``` text
mailtrace-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
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
│   │   └── gmail/
│   ├── reporting/
│   │   └── forensic_report.py
│   └── tests/
├── frontend/
│   └── optional-analyst-dashboard/
├── data/
├── docs/
└── docker-compose.yml
```

## 4. Module → Phase

  ---------------------------------------------------------------------------
  Module                  Phase                   Responsibility
  ----------------------- ----------------------- ---------------------------
  Gmail integration       0--1                    Receive mailbox events and
                                                  apply supported actions

  Parser                  1                       Extract message, headers,
                                                  URLs, attachments

  Evidence                1                       Preserve source and
                                                  calculate SHA-256

  Detection               2                       AI/NLP threat
                                                  classification

  Header forensics        3                       Technical header/routing
                                                  analysis

  Authentication          3                       SPF/DKIM/DMARC

  Origin                  3                       Relay reconstruction and
                                                  earliest reliable observed
                                                  IP

  GeoLocation             4                       Approximate IP/network
                                                  location

  URL analysis            4                       URL/domain risk analysis

  Attachment analysis     4                       Static file analysis

  Domain intelligence     4                       DNS/WHOIS/infrastructure

  Reputation              4                       Threat intelligence

  Correlation             5                       Sender/domain/IP/URL/case
                                                  relationships

  Attribution support     5                       Confidence-based
                                                  investigative findings

  Decision engine         6                       Final risk and Gmail action

  Case/reporting          6                       Case storage and forensic
                                                  report
  ---------------------------------------------------------------------------

## 5. AI Detection

Analyze subject, body, urgency, impersonation, social engineering,
phishing, BEC/payment diversion, credential harvesting, sender/domain
signals, URLs and attachment signals.

Baseline:

``` text
TF-IDF → Logistic Regression / SVM
```

Transformer/BERT is a stretch feature. AI is one evidence stream, not
the sole proof of maliciousness.

## 6. Forensics

Analyze Return-Path, Received, Message-ID, Reply-To, sender fields, SPF,
DKIM, DMARC, timestamps and routing anomalies.

Preserve original evidence and record rationale for important findings.

## 7. Origin & GeoLocation

Reconstruct the observable relay chain and identify the **Earliest
Reliable Observed IP**.

Do not claim a guaranteed attacker IP, physical location, or attacker's
machine.

GeoLocation can provide country, region, city, ISP/ASN and hosting
information, with VPN/TOR/proxy indicators where available.

## 8. URLs & Attachments

Analyze URLs for structure, obfuscation, domain, DNS, redirects where
safely available, age and reputation.

Analyze common PDF, PPT/PPTX, DOC/DOCX, XLS/XLSX, image, ZIP/archive,
HTML/text and suspicious file types using static indicators such as
filename, extension, MIME, size, SHA-256, metadata, extracted text and
embedded URLs.

Do not execute untrusted attachments in the prototype.

## 9. Correlation & Attribution Support

``` text
Sender ↔ Domain ↔ IP ↔ URL ↔ Attachment ↔ Case
```

Use graph relationships, confidence and rationale to identify related
infrastructure/campaign patterns.

Attribution is investigative support, not guaranteed person-level
identification.

## 10. Final Decision

The final decision is multi-signal. AI is one evidence stream and must
not be the sole proof of maliciousness.

``` text
AI + Forensics + Authentication + URL + Attachment
+ IP/Domain Intelligence + GeoLocation + Correlation
                     ↓
              Final Risk Assessment
                     ↓
       SAFE / SUSPICIOUS / MALICIOUS / UNKNOWN
```

Conceptual policy:

``` text
LOW / strong benign evidence → SAFE
MEDIUM / conflicting evidence → SUSPICIOUS
HIGH / strong malicious evidence → MALICIOUS
Insufficient or unavailable evidence → UNKNOWN
```

Thresholds must be calibrated with testing. UNKNOWN must not be silently
converted into SAFE or MALICIOUS.

## 11. Gmail Actions

``` text
SAFE       → Normal Gmail handling
SUSPICIOUS → MailTrace Review label + Alert
MALICIOUS  → Supported quarantine / label workflow + Alert
UNKNOWN    → Review label / no forced malicious action
```

MailTrace does not replace Gmail's native spam classifier or sit inside
Gmail's SMTP delivery path. The prototype observes/receives supported
Gmail/Workspace events, analyzes the message, and then applies only
supported Gmail actions using scoped permissions. Organization-level
mail routing/gateway controls may be required for true pre-delivery
blocking.

## 12. Evidence & Reporting

Forensics runs throughout the pipeline; the PDF is only one final
presentation of the evidence.

``` text
Evidence Captured
      ↓
SHA-256 + Timestamp + Evidence ID
      ↓
Immutable/controlled evidence record
      ↓
Analysis + Findings + Actions logged
      ↓
Chain-of-custody / audit trail
      ↓
Case
      ↓
Integrity-verifiable forensic report
```

Report sections include email summary, AI findings, authentication,
relay path, earliest reliable IP, GeoLocation, infrastructure
intelligence, URLs, attachments, correlation, attribution support,
evidence hashes, action history, limitations and timestamps.

Use the term **Integrity-verifiable forensic report**, not "tamper-proof
PDF".

## 13. Privacy, Compliance & Evidence Governance

-   Use least-privilege Gmail/OAuth scopes.
-   Minimize retained email content and retain only what the case
    requires.
-   Protect raw email and attachment evidence in transit and at rest.
-   Record evidence access and analysis actions in an audit trail.
-   Define retention/deletion rules for stored messages, attachments and
    reports.
-   Mask sensitive fields in analyst views where practical.
-   Never expose Gmail OAuth tokens, API keys or raw evidence in logs.
-   Treat forensic output as investigation support, not automatic legal
    attribution.

## 14. Technology Stack

-   Python
-   FastAPI
-   Gmail API / Google Workspace integration
-   SQLite
-   PostgreSQL deployment target
-   scikit-learn
-   Python `email`
-   dkimpy
-   pyspf
-   MaxMind GeoLite2 or IPinfo
-   dnspython
-   python-whois
-   AbuseIPDB / OTX where available
-   NetworkX
-   ReportLab
-   Docker / Docker Compose
-   Optional: React + Vite, Leaflet for analyst dashboard

## 14. API Surface

``` text
POST /gmail/events
POST /email/analyze
GET  /cases
POST /cases
GET  /cases/{case_id}
GET  /reports/{case_id}
```

## 15. Testing

Test legitimate, phishing, spoofing, impersonation, BEC, suspicious
URLs/attachments, multi-hop relay, missing headers, private IPs,
malformed email, missing authentication, intelligence outages, Gmail API
failures and duplicate events.

End-to-end:

``` text
Gmail Event → Fetch → Hash → Parse → Analyze → Correlate
→ Decide → Gmail Action → Case → Report
```

## 16. Definition of Done

The prototype is complete when Gmail ingestion, evidence hashing,
message/URL/attachment extraction, AI detection, SPF/DKIM/DMARC, relay
reconstruction, earliest reliable IP, GeoLocation/intelligence,
URL/attachment analysis, correlation, attribution-support findings,
final risk, Gmail action, case storage and integrity-verifiable
reporting all work and are tested.

## 17. Scope Boundaries

Do not claim guaranteed attacker identity, guaranteed physical location,
guaranteed originating machine, full malware sandboxing, replacement of
Gmail's spam infrastructure, perfect detection, production-scale threat
intelligence, or blockchain merely for branding.

### Core Value Proposition

> Detect the threat, inspect the complete email, reconstruct observable
> infrastructure, estimate geographic context, correlate related
> indicators, support investigation, preserve evidence, and take an
> appropriate Gmail action.
