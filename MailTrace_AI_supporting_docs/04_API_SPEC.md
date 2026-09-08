# MailTrace AI — API Specification

Backend framework: FastAPI.

## `POST /email/analyze`

Uploads and analyzes an email evidence file.

### Input
- `.eml` file

### Processing
1. Hash evidence
2. Parse email
3. Run detection
4. Analyze authentication
5. Reconstruct relay chain
6. Resolve earliest reliable observed IP
7. Query intelligence sources
8. Correlate infrastructure
9. Store case/evidence
10. Return analysis

### Response
Returns the common `EmailAnalysis` contract.

## `POST /cases`

Creates a case record.

## `GET /cases`

Returns available cases.

## `GET /cases/{case_id}`

Returns:
- case metadata
- analysis
- findings
- evidence
- correlation information

## `GET /reports/{case_id}`

Generates or retrieves the forensic report for the case.

## API Rules

- Return structured errors.
- Never expose API secrets.
- External service failures should produce nullable/partial fields.
- Do not expose internal stack traces in production responses.
- Keep response fields aligned with `02_DATA_MODEL.md`.
