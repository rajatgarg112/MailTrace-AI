# MailTrace AI --- Setup & Team Workflow

## Development Order

``` text
1. Freeze Gmail architecture
2. Freeze common data contract
3. Prepare sanitized .eml fixtures
4. Build parser + evidence hashing
5. Build Gmail ingestion
6. Build AI detection
7. Build header forensics
8. Build URL/attachment analysis
9. Build GeoLocation + intelligence
10. Build correlation
11. Build decision engine
12. Integrate Gmail actions
13. Add cases/reporting
14. End-to-end testing
15. Optional analyst dashboard
```

## Team Ownership

### AI/Detection

NLP, TF-IDF, classifier, BEC/phishing/impersonation signals.

### Header/Forensics

Parser, Received chain, SPF/DKIM/DMARC, origin and evidence.

### Intelligence/Geo

GeoIP, DNS, WHOIS, reputation and URL analysis.

### Attachment/Content

Attachment metadata, text extraction, OCR where justified and embedded
URL indicators.

### Backend/Gmail/Integration

FastAPI, Gmail integration, orchestration, database, decision engine,
cases, reporting and integration tests.

### Optional Frontend

Analyst dashboard, map and correlation graph.

## Stack

FastAPI, Gmail API/Workspace, SQLite, PostgreSQL target, scikit-learn,
Python `email`, dkimpy, pyspf, dnspython, python-whois, NetworkX,
ReportLab and Docker.

Optional React/Vite + Leaflet.

## Key Rule

The analysis engine must work independently using `.eml` fixtures. Gmail
is the integration layer around the core AI/forensic engine.

Never commit OAuth secrets, API keys or sensitive raw email evidence.

## Final Ownership Rule

Gmail integration, OAuth scopes, event handling and Gmail actions belong
to the integration/backend owner. The analysis modules must remain
independently testable with `.eml` fixtures.

## Final Security Checklist

Before demo: - OAuth scopes are least-privilege. - No secrets are
committed. - Raw email/attachments are not written to ordinary logs. -
Evidence hashes and timestamps are recorded. - Retention/deletion
behavior is documented. - UNKNOWN is preserved when evidence is
insufficient. - Gmail is not described as being replaced or intercepted
at SMTP level.
