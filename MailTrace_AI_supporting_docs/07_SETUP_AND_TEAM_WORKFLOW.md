# MailTrace AI — Setup & Team Workflow

## Development Order

Follow this order:

```text
1. Freeze architecture
2. Freeze data contract
3. Create sample .eml fixtures
4. Build parser
5. Build stub pipeline
6. Build API
7. Implement modules in parallel
8. Integrate modules
9. Add integration tests
10. Build frontend
11. Add evidence/reporting
12. End-to-end demo testing
```

## Team Ownership

### Detection Team
Own:
- NLP preprocessing
- TF-IDF baseline
- classifier
- threat signals
- model evaluation

### Header + Origin Team
Own:
- email parsing
- `Received` chain
- SPF/DKIM/DMARC
- earliest reliable observed IP
- GeoIP
- DNS/WHOIS integration

### Frontend Team
Own:
- dashboard
- upload flow
- threat visualization
- map
- case pages
- graph visualization

### Backend + Integration Owner
Own:
- FastAPI
- API contracts
- pipeline orchestration
- database
- case management
- correlation
- reporting integration
- integration tests

## Git Rules

- Keep modules isolated.
- Avoid unrelated changes in the same commit.
- Do not commit secrets.
- Keep sample evidence sanitized.
- Update documentation when an API/data contract changes.

## Environment

Recommended prototype stack:

- Python
- FastAPI
- React + Vite
- SQLite
- scikit-learn
- Python `email`
- dkimpy
- pyspf
- dnspython
- python-whois
- NetworkX
- Leaflet
- ReportLab
- Docker / Docker Compose

## External Intelligence

Choose one primary GeoIP provider for the prototype rather than integrating many providers unnecessarily.

Possible services:
- MaxMind GeoLite2
- IPinfo
- AbuseIPDB
- OTX

Keep provider-specific code behind service modules so providers can be replaced later.

## Done Criteria

The prototype is complete when:

- `.eml` upload works
- evidence is hashed
- headers/body/URLs/attachments are parsed
- threat classification works
- SPF/DKIM/DMARC are represented
- relay chain is reconstructed
- earliest reliable observed IP is identified conservatively
- GeoIP/DNS/WHOIS/reputation enrichment works where available
- infrastructure correlation works
- cases are stored
- evidence hashes appear in the report
- PDF report is generated
- frontend displays the findings
- phishing and legitimate end-to-end tests pass
- external failures do not crash analysis
- no secrets are committed
