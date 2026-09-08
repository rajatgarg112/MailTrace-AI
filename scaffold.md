# MailTrace AI --- `scaffold.md`

### AI-Powered Email Threat Detection, Geolocation & Forensic Intelligence Platform

**SIH 2026 · Problem Statement 26106 · Team WebInnovators**

This document defines the repository structure, module boundaries,
shared data contract, technology choices, ownership model, and
implementation order for the MailTrace AI prototype.

The architecture follows the project roadmap:

**Research → Detection → Header Forensics → Origin Intelligence →
Correlation → Dashboard/Report → Integration & Testing**

The goal is to let team members work in parallel without creating
incompatible interfaces.

------------------------------------------------------------------------

## 1. Architecture Principles

1.  **One shared analysis contract**
    -   Every backend module reads from and writes to the same
        `EmailAnalysis` structure.
    -   Do not create independent result formats for individual modules.
2.  **Evidence before conclusions**
    -   Detection scores and attribution must be supported by observable
        indicators.
    -   The system should explain *why* an email was flagged.
3.  **Do not claim a "true attacker IP"**
    -   The system identifies the **earliest reliable observed network
        node** available from the email evidence.
    -   Relay headers may be incomplete, stripped, private, proxied, or
        otherwise unreliable.
4.  **Prototype first, advanced features second**
    -   Build a working deterministic pipeline before adding
        BERT/transformers or other stretch features.
5.  **Explainable attribution**
    -   Correlation scores must show the signals that contributed to the
        score rather than behaving as a black box.
6.  **Evidence integrity**
    -   Preserve hashes and collection metadata for important evidence.
    -   Reports should be described as **integrity-verifiable forensic
        reports**, not inherently "tamper-proof" documents.

------------------------------------------------------------------------

## 2. Repository Layout

``` text
email-forensics-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI application entrypoint
│   │   │
│   │   ├── api/
│   │   │   ├── routes_ingest.py          # POST /email/analyze
│   │   │   │                              # upload .eml / raw email
│   │   │   ├── routes_cases.py           # GET/POST /cases
│   │   │   └── routes_reports.py         # GET /reports/{case_id}
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                 # environment variables / API keys
│   │   │   └── security.py               # optional analyst authentication
│   │   │
│   │   ├── detection/                    # ── Phase 1 ──
│   │   │   ├── classifier.py             # TF-IDF + LR/SVM baseline
│   │   │   ├── nlp_features.py           # urgency / impersonation cues
│   │   │   ├── url_analysis.py            # URL and shortener analysis
│   │   │   ├── attachment_analysis.py     # metadata / hash / suspicious type checks
│   │   │   └── models/                    # trained model artifacts
│   │   │
│   │   ├── header_analysis/              # ── Phase 2 ──
│   │   │   ├── eml_parser.py             # Python email library
│   │   │   ├── relay_chain.py             # Received-header reconstruction
│   │   │   └── auth_validator.py          # SPF / DKIM / DMARC analysis
│   │   │
│   │   ├── origin_trace/                 # ── Phase 3 ──
│   │   │   ├── ip_geolocation.py          # GeoIP provider wrapper
│   │   │   ├── infra_fingerprint.py       # VPN / TOR / hosting / reputation
│   │   │   └── domain_intel.py             # WHOIS + DNS/MX
│   │   │
│   │   ├── correlation/                  # ── Phase 4 ──
│   │   │   ├── graph_builder.py           # NetworkX graph
│   │   │   └── confidence_score.py        # explainable correlation score
│   │   │
│   │   ├── reporting/                    # ── Phase 5 ──
│   │   │   ├── pdf_report.py              # forensic report generation
│   │   │   ├── evidence.py                # evidence metadata + SHA-256 hashes
│   │   │   └── case_store.py               # case persistence / retrieval
│   │   │
│   │   └── pipeline.py                   # end-to-end orchestration
│   │
│   ├── tests/
│   │   ├── test_detection.py
│   │   ├── test_header_analysis.py
│   │   ├── test_origin_trace.py
│   │   ├── test_correlation.py
│   │   ├── test_reporting.py
│   │   └── sample_emails/                # .eml fixtures
│   │       ├── phishing/
│   │       └── legitimate/
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                             # ── Phase 5 ──
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx             # risk score + indicators
│   │   │   ├── EmailSummary.jsx           # sender / subject / key findings
│   │   │   ├── HeaderTimeline.jsx         # relay / authentication view
│   │   │   ├── TraceMap.jsx               # Leaflet map
│   │   │   ├── CorrelationGraph.jsx       # linked IP/domain/email graph
│   │   │   ├── CaseList.jsx               # case management
│   │   │   └── ReportViewer.jsx            # report view / download
│   │   ├── api/
│   │   │   └── client.js                 # backend REST client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/                                  # ── Phase 0 ──
│   ├── raw/                               # source datasets / sample emails
│   ├── processed/                         # cleaned / labeled datasets
│   └── notebooks/
│       └── eda_and_training.ipynb         # EDA + baseline model training
│
├── docs/
│   ├── architecture.md
│   ├── api_spec.md
│   └── roadmap.md
│
├── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

## 3. Module → Roadmap Phase → Owner

  --------------------------------------------------------------------------------
  Module                           Roadmap Phase           Suggested Owner
  -------------------------------- ----------------------- -----------------------
  `data/`                          Phase 0 --- Research &  Whole team
                                   Scoping                 

  `backend/app/detection/`         Phase 1 --- Detection   2 members
                                   Engine                  

  `backend/app/header_analysis/`   Phase 2 --- Header &    2 members
                                   Protocol Analysis       

  `backend/app/origin_trace/`      Phase 3 --- Origin      Same 2 members
                                   Traceability &          
                                   Geolocation             

  `backend/app/correlation/`       Phase 4 --- Identity    Backend & Correlation
                                   Correlation             member

  `backend/app/reporting/`         Phase 5 --- Forensic    Backend member
                                   Reporting               

  `frontend/`                      Phase 5 --- Dashboard   Frontend member

  `pipeline.py`, API integration,  Phase 6 --- Integration Whole team
  tests, deployment                & Polish                
  --------------------------------------------------------------------------------

### Team split

``` text
2 members → Detection Engine
             NLP/ML, urgency, impersonation, URLs, attachments

2 members → Header + Origin Intelligence
             .eml parsing, Received chain, SPF/DKIM/DMARC,
             IP geolocation, DNS/WHOIS, infrastructure intelligence

1 member → Frontend
            React dashboard, map, timeline, graph visualization

1 member → Backend + Correlation
            FastAPI, pipeline, database, NetworkX,
            evidence/reporting, integration
```

------------------------------------------------------------------------

## 4. Core Data Contract

Every module must consume and return the shared `EmailAnalysis` object.

The exact implementation can later use Pydantic models, but the logical
contract should remain stable.

``` python
EmailAnalysis = {
    "metadata": {
        "email_id": str,
        "case_id": str,
        "received_at": str | None,
        "analysis_started_at": str | None,
        "analysis_completed_at": str | None,
    },

    "message": {
        "from": str | None,
        "to": [str],
        "reply_to": str | None,
        "return_path": str | None,
        "subject": str | None,
        "body": str | None,
        "urls": [dict],
        "attachments": [dict],
    },

    "raw": {
        "headers": dict,
        "source_format": "eml | raw_text",
        "source_sha256": str | None,
    },

    "detection": {
        "classification":
            "legit | suspicious | impersonated | phishing | fraud",
        "risk_score": float,
        "confidence": float,
        "flags": [str],
        "model_version": str | None,
    },

    "auth": {
        "spf": "pass | fail | none | neutral | softfail | temperror | permerror",
        "dkim": "pass | fail | none | neutral | temperror | permerror",
        "dmarc": "pass | fail | none | quarantine | reject",
        "alignment": {
            "spf_aligned": bool | None,
            "dkim_aligned": bool | None,
        },
    },

    "relay_chain": [
        {
            "hop": int,
            "ip": str | None,
            "hostname": str | None,
            "timestamp": str | None,
            "source": str,
            "reliability": "high | medium | low",
        }
    ],

    "origin": {
        "earliest_reliable_ip": str | None,
        "country": str | None,
        "region": str | None,
        "city": str | None,
        "isp": str | None,
        "organization": str | None,
        "is_vpn": bool | None,
        "is_tor": bool | None,
        "is_hosting": bool | None,
        "reputation": {
            "known_malicious": bool | None,
            "abuse_score": float | None,
            "botnet_indicator": bool | None,
        },
        "confidence": float | None,
    },

    "domain_intel": {
        "sender_domain": str | None,
        "whois_registrar": str | None,
        "domain_created": str | None,
        "domain_age_days": int | None,
        "mx_records": [str],
        "dns_records": dict,
    },

    "correlation": {
        "linked_domains": [str],
        "linked_ips": [str],
        "linked_emails": [str],
        "linked_cases": [str],
        "confidence_score": float | None,
        "signals": [str],
    },

    "attribution": {
        "confidence_score": float | None,
        "infra_type":
            "compromised_account | spoofed_domain | anonymized | "
            "hosting_infrastructure | unknown",
        "rationale": [str],
    },

    "evidence": {
        "items": [
            {
                "evidence_id": str,
                "type": "email | header | url | attachment | ip | domain | report",
                "sha256": str | None,
                "collected_at": str | None,
                "description": str,
            }
        ],
    },
}
```

### Contract rules

-   Fields that cannot be reliably obtained must use `None` or an empty
    list rather than invented values.
-   Do not overwrite raw evidence with normalized values.
-   Keep the original email/source hash.
-   Detection confidence and attribution confidence are different
    concepts.
-   `earliest_reliable_ip` means the earliest node judged reliable by
    the parser; it does **not** mean the attacker's guaranteed physical
    origin.
-   Attribution must include a human-readable rationale.

------------------------------------------------------------------------

## 5. Processing Pipeline

The backend pipeline should follow this order:

``` text
                    Raw .eml / Raw Email
                            │
                            ▼
                    ┌───────────────┐
                    │  Ingestion    │
                    │ + SHA-256     │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │ EML / Header  │
                    │    Parser     │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       Detection       Auth Analysis    URL/Attachment
       Engine          SPF/DKIM/DMARC     Analysis
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    ┌───────────────┐
                    │ Relay Chain   │
                    │ Reconstruction│
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │ Origin Intel  │
                    │ GeoIP / DNS   │
                    │ WHOIS / TI    │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │ Correlation   │
                    │   NetworkX    │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │ Case + Evidence│
                    │    Storage    │
                    └───────┬───────┘
                            ▼
              ┌─────────────┴─────────────┐
              ▼                           ▼
        React Dashboard            Forensic PDF
```

------------------------------------------------------------------------

## 6. Phase Responsibilities

### Phase 0 --- Research & Scoping

**Goal:** establish the data, email standards, and external intelligence
providers before feature development.

Tasks:

1.  Collect and organize legitimate/phishing sample emails.
2.  Study RFC 5321/5322 email structure.
3.  Study SPF, DKIM and DMARC behavior.
4.  Compare GeoIP providers and their limits.
5.  Define the first version of the `EmailAnalysis` contract.
6.  Create representative `.eml` fixtures for testing.

Primary data sources planned by the roadmap include Enron, Nazario,
PhishTank and SpamAssassin.

------------------------------------------------------------------------

### Phase 1 --- Fraudulent Email Detection Engine

**Goal:** classify and score suspicious email content.

Initial implementation:

``` text
TF-IDF
  ↓
Logistic Regression / SVM baseline
  ↓
Risk + confidence
```

Additional signals:

-   urgency language
-   payment/credential requests
-   impersonation cues
-   suspicious URLs
-   URL shorteners
-   suspicious attachment metadata

**Stretch:** transformer/BERT-based NLP only after the baseline is
working.

------------------------------------------------------------------------

### Phase 2 --- Email Header & Protocol Analysis

**Goal:** determine how the email was structured and what authentication
evidence is available.

Tasks:

1.  Parse raw `.eml`.
2.  Extract:
    -   From
    -   To
    -   Reply-To
    -   Return-Path
    -   Message-ID
    -   Subject
    -   Authentication-Results
    -   Received headers
3.  Reconstruct the relay chain.
4.  Analyze SPF, DKIM and DMARC.
5.  Compare sender-domain information with authentication evidence.

The system should preserve both **observed authentication results** and
any independently verified results when available.

------------------------------------------------------------------------

### Phase 3 --- Origin Traceability & Geolocation

**Goal:** turn reliable relay information into network and
infrastructure intelligence.

Tasks:

1.  Extract candidate IP addresses from the relay chain.
2.  Filter private/reserved/unusable addresses.
3.  Rank candidate nodes by reliability.
4.  Select the **earliest reliable observed IP**.
5.  Perform GeoIP lookup.
6.  Check infrastructure/reputation intelligence.
7.  Perform WHOIS and DNS/MX lookups.

Output examples:

``` text
Earliest reliable IP
Country / Region / City
ISP / Organization
VPN indicator
TOR indicator
Hosting indicator
Reputation information
Domain age
MX records
Origin confidence
```

**Important:** location data is approximate intelligence, not proof of
the attacker's physical location.

------------------------------------------------------------------------

### Phase 4 --- Identity Correlation & Attribution

**Goal:** connect evidence across multiple emails/cases.

Network graph concept:

``` text
Email
  │
  ├── Sender
  ├── Domain
  ├── IP
  ├── URL
  └── Case
       │
       └── related cases
```

Use NetworkX to identify repeated infrastructure.

The attribution layer should produce:

-   linked IPs
-   linked domains
-   linked cases/emails
-   correlation signals
-   confidence score
-   rationale
-   likely infrastructure type

Avoid presenting correlation as proof of a real-world person's identity.

------------------------------------------------------------------------

### Phase 5 --- Dashboard & Forensic Reporting

**Goal:** make the analysis understandable to an analyst.

Dashboard should show:

1.  Overall risk score.
2.  Classification and confidence.
3.  Why the email was flagged.
4.  Sender/header summary.
5.  SPF/DKIM/DMARC results.
6.  Relay-chain timeline.
7.  Earliest reliable observed IP.
8.  GeoIP information.
9.  Infrastructure/reputation indicators.
10. Correlation graph.
11. Evidence list.
12. Case information.
13. PDF report generation.

The map should visualize the observed/derived network nodes, not imply
that a map marker proves the attacker's physical location.

------------------------------------------------------------------------

### Phase 6 --- Integration, Testing & Pitch

**Goal:** produce a stable judge-ready end-to-end demonstration.

Required demo path:

``` text
Upload .eml
   ↓
Parse
   ↓
Detect
   ↓
Authenticate
   ↓
Reconstruct relay chain
   ↓
Trace earliest reliable node
   ↓
GeoIP + domain intelligence
   ↓
Correlate
   ↓
Display dashboard
   ↓
Generate integrity-verifiable forensic report
```

Testing priorities:

-   phishing detection
-   legitimate email false positives
-   malformed `.eml`
-   missing headers
-   private IP addresses
-   incomplete `Received` chains
-   missing WHOIS/DNS data
-   API failures/rate limits
-   unknown URL/attachment formats
-   empty/partial authentication results

------------------------------------------------------------------------

## 7. Tech Stack --- Frozen Prototype Choices

  -----------------------------------------------------------------------
  Layer                               Technology
  ----------------------------------- -----------------------------------
  Backend API                         **FastAPI**

  Frontend                            **React + Vite**

  Map                                 **Leaflet**

  ML/NLP baseline                     **scikit-learn**

  Text features                       **TF-IDF**

  Baseline models                     **Logistic Regression / SVM**

  Advanced NLP                        Transformer/BERT --- stretch only

  Email parsing                       Python `email` standard library

  DKIM                                `dkimpy`

  SPF                                 `pyspf`

  Geolocation                         **Choose one primary provider:**
                                      MaxMind GeoLite2 or IPinfo

  DNS                                 `dnspython`

  WHOIS                               `python-whois`

  Threat/reputation intelligence      AbuseIPDB / OTX where available and
                                      appropriate

  Graph correlation                   **NetworkX**

  Database                            **SQLite for prototype**;
                                      PostgreSQL can be the deployment
                                      target

  PDF                                 **ReportLab**

  Containerization                    Docker / Docker Compose
  -----------------------------------------------------------------------

### Stack rule

Do not simultaneously implement multiple alternatives just because they
appear in earlier planning documents.

For the prototype:

``` text
FastAPI
React + Vite
SQLite
ReportLab
NetworkX
scikit-learn
One primary GeoIP provider
```

Other options can remain documented as future/deployment alternatives.

------------------------------------------------------------------------

## 8. API Surface

Initial API contract:

``` text
POST /email/analyze
    Upload .eml / raw email
    → returns EmailAnalysis

GET /cases
    → list analyzed cases

POST /cases
    → create/store a case when needed

GET /cases/{case_id}
    → retrieve complete analysis

GET /reports/{case_id}
    → generate/return forensic PDF
```

The detailed request/response schemas belong in:

``` text
docs/api_spec.md
```

------------------------------------------------------------------------

## 9. Evidence Integrity

For every uploaded email:

1.  Preserve the original source.
2.  Calculate SHA-256.
3.  Store the hash with the case.
4.  Hash important extracted evidence where appropriate.
5.  Record collection/analysis timestamps.
6.  Include evidence identifiers in the report.

Example:

``` text
Evidence ID: EV-0001
Type: Original Email
SHA-256: <hash>
Collected At: <timestamp>
Case ID: CASE-0001
```

The report should be described as:

> **Integrity-verifiable forensic report**

Do not claim that a generated PDF is automatically "tamper-proof."

------------------------------------------------------------------------

## 10. Database Scope

The initial SQLite database should support at least:

``` text
cases
emails
analysis_results
relay_hops
domains
ip_intelligence
correlations
evidence
```

Keep the database layer behind `case_store.py` so the application can
move from SQLite to PostgreSQL without rewriting the analysis modules.

------------------------------------------------------------------------

## 11. Error Handling & External Services

External intelligence services are not guaranteed to respond.

Every external lookup should support:

``` text
success
not_found
rate_limited
timeout
provider_error
```

A failed GeoIP/WHOIS/DNS lookup must **not** cause the complete email
analysis to fail.

Example:

``` text
GeoIP → success
WHOIS → timeout
DNS → success

Final analysis → still valid
WHOIS field → None
warning → "WHOIS lookup unavailable"
```

API keys must never be committed to Git.

Use:

``` text
.env
.env.example
```

and environment variables.

------------------------------------------------------------------------

## 12. Development Rules for the Team

### Rule 1 --- Do not change the shared contract casually

If a field must change:

1.  Discuss it with the backend/integration owner.
2.  Update `docs/api_spec.md`.
3.  Update tests.
4.  Update all affected modules.

### Rule 2 --- Modules must remain independently testable

For example:

``` text
detection/
header_analysis/
origin_trace/
correlation/
```

should be testable without requiring the entire frontend.

### Rule 3 --- Never hardcode API keys

Bad:

``` python
IPINFO_TOKEN = "actual-secret"
```

Good:

``` python
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")
```

### Rule 4 --- Keep raw evidence separate

Never modify the original `.eml` and treat the modified copy as the
original evidence.

### Rule 5 --- Do not overclaim forensic conclusions

Use:

``` text
"earliest reliable observed IP"
"correlation"
"indicator"
"confidence"
"likely infrastructure"
```

instead of:

``` text
"true attacker IP"
"confirmed attacker identity"
"exact physical location"
```

unless independently established by evidence outside the email analysis.

------------------------------------------------------------------------

## 13. Testing Strategy

### Unit tests

Each major module gets independent tests:

``` text
tests/
├── test_detection.py
├── test_header_analysis.py
├── test_origin_trace.py
├── test_correlation.py
└── test_reporting.py
```

### Fixture categories

``` text
legitimate email
phishing email
spoofed sender
missing Reply-To
missing Return-Path
multiple Received headers
private relay IP
TOR/hosting example
malformed email
missing authentication results
```

### End-to-end test

At least one fixture must successfully pass through:

``` text
ingest
→ parse
→ detection
→ auth
→ relay reconstruction
→ origin intelligence
→ correlation
→ storage
→ report
```

------------------------------------------------------------------------

## 14. Setup Order

Do not start by implementing every feature independently.

### Step 1 --- Freeze the architecture

Confirm:

``` text
FastAPI
React + Vite
SQLite
NetworkX
scikit-learn
ReportLab
primary GeoIP provider
```

### Step 2 --- Freeze the `EmailAnalysis` contract

Create the model/schema first.

### Step 3 --- Create sample `.eml` fixtures

Include at least:

``` text
1 legitimate
1 phishing
1 spoofed/impersonation example
1 multi-hop relay example
```

### Step 4 --- Build the parser

Get:

``` text
headers
body
URLs
attachments
Received chain
```

working before advanced ML.

### Step 5 --- Build the stub pipeline

Make one email flow through every module using placeholder outputs.

### Step 6 --- Build the FastAPI layer

Expose `/email/analyze` and case/report endpoints.

### Step 7 --- Parallel implementation

Teams implement their modules against the frozen contract.

### Step 8 --- Integration tests

Replace stubs one module at a time and verify the complete pipeline.

### Step 9 --- Dashboard

Connect the frontend only after the API response structure is stable.

### Step 10 --- Evidence/reporting

Generate the forensic report from the same `EmailAnalysis` object used
by the dashboard.

### Step 11 --- Final demo

Test the complete:

``` text
Upload → Detect → Explain → Trace → Correlate → Report
```

flow repeatedly.

------------------------------------------------------------------------

## 15. Definition of Done

The prototype is considered complete when:

-   [ ] A `.eml` file can be uploaded.
-   [ ] Raw headers/body are parsed.
-   [ ] URLs and attachment metadata are extracted.
-   [ ] The email receives a risk score and classification.
-   [ ] SPF/DKIM/DMARC information is displayed when available.
-   [ ] `Received` headers are reconstructed into a relay chain.
-   [ ] An earliest reliable observed IP can be selected when evidence
    allows.
-   [ ] GeoIP information is displayed when available.
-   [ ] Domain/DNS intelligence is displayed when available.
-   [ ] VPN/TOR/hosting/reputation indicators are shown when supported
    by the available intelligence source.
-   [ ] Related IPs/domains/cases can be correlated.
-   [ ] Correlation has an explainable rationale.
-   [ ] A case can be stored and retrieved.
-   [ ] Evidence has SHA-256 integrity metadata.
-   [ ] A forensic PDF can be generated.
-   [ ] The frontend displays the complete analysis.
-   [ ] At least one phishing and one legitimate email pass through the
    full pipeline.
-   [ ] External API failures do not crash the complete analysis.
-   [ ] No API secrets are committed to the repository.

------------------------------------------------------------------------

## 16. Final Project Flow

``` text
                 MAILTRACE AI
                     │
                     ▼
              Email / .eml Upload
                     │
                     ▼
              Raw Evidence Hash
                     │
                     ▼
              RFC / EML Parsing
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     AI Detection          Header Forensics
          │                     │
          │              SPF / DKIM / DMARC
          │                     │
          └──────────┬──────────┘
                     ▼
             Relay Reconstruction
                     │
                     ▼
          Earliest Reliable Node
                     │
                     ▼
        GeoIP + DNS + WHOIS + TI
                     │
                     ▼
             Threat Correlation
                     │
                     ▼
            Explainable Findings
                     │
              ┌──────┴──────┐
              ▼             ▼
          Dashboard      PDF Report
              │             │
              └──────┬──────┘
                     ▼
             Forensic Case Record
```

------------------------------------------------------------------------

## 17. Important Scope Boundary

The first working prototype should **not** attempt to:

-   identify a real person's identity from an email alone;
-   guarantee the attacker's physical location;
-   guarantee the first IP is the attacker's machine;
-   perform full malware sandboxing;
-   build a production-scale threat-intelligence platform;
-   add BERT/transformers before the baseline pipeline works;
-   add blockchain merely for branding.

The core hackathon value is:

> **Detect the threat, explain the evidence, reconstruct the observable
> path, correlate infrastructure, and produce an integrity-verifiable
> forensic case report.**

That is the primary implementation target for the team.
