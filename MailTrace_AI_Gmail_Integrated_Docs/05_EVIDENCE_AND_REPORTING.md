# MailTrace AI --- Evidence & Forensic Reporting

## Evidence Lifecycle

``` text
Gmail Message → Raw Source → SHA-256 → Evidence ID
→ Analysis → Findings → Case → Report
```

Preserve, where permitted: - raw email - headers - URLs - attachment
metadata/hashes - IP observations - DNS/WHOIS - reputation results - AI
signals - correlation findings - Gmail action history

## Report

Include: 1. Case details 2. Email summary 3. AI detection 4.
SPF/DKIM/DMARC 5. Relay path 6. Earliest reliable observed IP 7.
GeoLocation 8. IP/domain intelligence 9. URLs 10. Attachments 11.
Correlation 12. Attribution support 13. Decision/Gmail action 14.
Evidence hashes 15. Limitations 16. Timestamps

Use **Integrity-verifiable forensic report**.

Clearly separate observed evidence, inferred relationships, confidence
and investigative hypotheses. A network IP/geolocation result is not
proof of a person's identity or physical location.

## Chain of Custody

For each retained evidence item, record:

1.  capture/ingestion timestamp
2.  SHA-256 hash
3.  evidence ID
4.  source/message reference
5.  analysis actions
6.  analyst/system access where applicable
7.  final report reference
8.  retention/deletion status

This creates an auditable evidence trail. It does not make a PDF or
database mathematically "tamper-proof".

## Privacy & Retention

Retain only data required for the investigation. Protect raw messages
and attachments, restrict access, avoid sensitive data in logs, and
apply defined retention/deletion rules.
