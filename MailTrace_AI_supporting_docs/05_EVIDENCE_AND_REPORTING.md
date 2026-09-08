# MailTrace AI — Evidence & Forensic Reporting

## Evidence Preservation

At ingestion time:
1. Preserve the original `.eml`.
2. Calculate SHA-256.
3. Record file size.
4. Record ingestion timestamp.
5. Associate the evidence with a case.

Example:

```text
Evidence ID
SHA-256
Original filename
Size
Ingestion timestamp
Case ID
```

## Evidence Items

Evidence can include:
- raw email
- headers
- URLs
- attachment metadata
- IP observations
- DNS results
- WHOIS results
- reputation responses
- detection signals
- correlation findings

## Integrity

The system should use SHA-256 hashes to make evidence integrity verifiable.

Use the term:

> Integrity-verifiable forensic report

Do not claim the generated PDF is inherently "tamper-proof".

## Report Sections

1. Case information
2. Email summary
3. Threat classification
4. Risk score
5. SPF/DKIM/DMARC
6. Relay chain
7. Earliest reliable observed IP
8. GeoIP information
9. DNS/WHOIS information
10. Reputation intelligence
11. URL and attachment findings
12. Infrastructure correlation
13. Evidence hashes
14. Limitations
15. Analysis timestamp

## Limitations

The report must clearly state that:
- email headers can be incomplete or manipulated
- IP location is approximate
- a network node is not necessarily the attacker's physical machine
- attribution does not automatically identify a person
- third-party intelligence can be incomplete or unavailable
