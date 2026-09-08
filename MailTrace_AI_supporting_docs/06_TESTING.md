# MailTrace AI — Testing Strategy

Testing follows the phases defined in `scaffold.md`.

## Email Fixtures

Maintain `.eml` fixtures for:

1. Legitimate email
2. Phishing email
3. Spoofed sender
4. Multi-hop relay chain
5. Missing `Received` headers
6. Private IP addresses
7. Malformed email
8. Missing authentication results
9. Suspicious URLs
10. Email with suspicious attachment metadata

## Unit Tests

### Parser
- headers parsed correctly
- body extracted
- URLs detected
- attachments detected
- malformed messages handled safely

### Detection
- expected classification returned
- score remains within expected range
- model version is recorded

### Authentication
- SPF result handled
- DKIM result handled
- DMARC result handled
- missing results do not crash the pipeline

### Origin
- relay chain ordered correctly
- private IPs handled
- invalid IPs ignored
- earliest reliable observed IP is selected conservatively

### Intelligence
- successful lookup handled
- API timeout handled
- missing result handled
- rate-limit/error response handled

### Correlation
- expected entities created
- relationships generated
- rationale stored

## Integration Tests

Minimum end-to-end tests:

```text
Upload .eml
 → Parse
 → Detect
 → Authenticate
 → Trace
 → Enrich
 → Correlate
 → Store
 → Report
```

Test both:
- phishing scenario
- legitimate scenario

## Security Tests

Check:
- no secrets committed
- unsafe file handling
- upload size limits
- malformed input
- path traversal protection
- API error leakage

## Definition of Test Success

The pipeline should produce useful partial output even when an external intelligence service is unavailable.
