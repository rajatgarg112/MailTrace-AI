# MailTrace AI — Architecture

## Purpose
This document defines the implementation architecture for MailTrace AI and follows the project flow established in `scaffold.md`.

## System Flow

```text
Email Upload
    ↓
Evidence Hashing
    ↓
Email Parser
    ↓
Threat Detection
    ↓
SPF / DKIM / DMARC
    ↓
Relay Chain Reconstruction
    ↓
Earliest Reliable Observed IP
    ↓
GeoIP + DNS + WHOIS + Threat Intelligence
    ↓
Infrastructure Correlation
    ↓
Explainable Findings
    ↓
Case Storage
    ↓
Dashboard + Forensic Report
```

## Components

### Frontend
- React
- Vite
- Leaflet for map visualization

Responsibilities:
- `.eml` upload
- analysis status
- threat score and classification
- authentication results
- relay-chain visualization
- origin/IP information
- infrastructure graph
- case management
- report download

### Backend
- Python
- FastAPI

Responsibilities:
- REST API
- email ingestion
- pipeline orchestration
- module integration
- database access
- case management
- report generation

### Analysis Layer
The analysis layer is divided into independent modules:
- parser
- detection
- authentication
- header/origin analysis
- domain intelligence
- reputation intelligence
- correlation
- attachment analysis
- evidence/reporting

## Design Principles

1. Modules must remain independently testable.
2. External intelligence failures must not crash an analysis.
3. External lookup fields must be nullable.
4. Findings must include evidence or rationale where possible.
5. Do not claim a guaranteed physical origin or real-person identity.
6. Preserve the original evidence and its SHA-256 hash.
