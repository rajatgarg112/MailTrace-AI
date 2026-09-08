# MailTrace AI — Analysis Pipeline

## Phase 0 — Architecture Freeze

Freeze:
- FastAPI backend
- React + Vite frontend
- SQLite prototype database
- PostgreSQL deployment target
- common `EmailAnalysis` contract
- module interfaces
- API naming

No feature development should silently change the architecture.

## Phase 1 — Foundation

### Parser
Input:
- `.eml`

Output:
- headers
- body
- URLs
- attachments
- received headers
- message metadata

The parser must preserve raw evidence.

### Stub Pipeline

```text
.eml
 ↓
parse()
 ↓
EmailAnalysis
 ↓
save_case()
```

The stub allows frontend/backend integration before every analysis module is complete.

## Phase 2 — Detection

Baseline approach:
- TF-IDF
- Logistic Regression or SVM
- scikit-learn

Possible stretch:
- transformer/BERT model

Detection should expose:
- classification
- risk score
- model version
- contributing signals

## Phase 3 — Header and Origin Analysis

### Authentication
Process:
- SPF
- DKIM
- DMARC

### Relay Reconstruction

Parse `Received` headers and reconstruct the observable relay sequence.

The system should identify the **earliest reliable observed IP**, not claim a guaranteed attacker IP.

Reliability factors may include:
- syntactic validity
- private/public address
- header consistency
- timestamp consistency
- trusted receiving boundary
- conflicting relay evidence

## Phase 4 — Intelligence

Collect where available:
- GeoIP
- DNS
- WHOIS
- IP/domain reputation
- Tor/VPN/hosting indicators
- abuse intelligence

External API failures must return partial results rather than fail the whole analysis.

## Phase 5 — Correlation

Build relationships such as:

```text
Email
 ├── Sender
 ├── Domain
 ├── IP
 ├── URL
 ├── Attachment
 └── Case
```

NetworkX may be used for graph construction.

Every important correlation should have an explainable rationale.

## Phase 6 — Reporting and Integration

Final flow:

```text
Upload
 → Analyze
 → Correlate
 → Store Case
 → Display Dashboard
 → Generate Report
```

The report should be integrity-verifiable using evidence hashes and an audit trail.
