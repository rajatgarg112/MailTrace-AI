# MailTrace AI --- Data Model

The shared contract supports Gmail ingestion, AI, forensics,
GeoLocation, URLs, attachments, correlation and Gmail action.

``` python
{
    "email_id": str,
    "case_id": str | None,
    "gmail": {
        "message_id": str | None,
        "thread_id": str | None,
        "labels_before": list[str],
        "action": str | None
    },
    "message": {
        "subject": str | None,
        "from": str | None,
        "to": list[str],
        "cc": list[str],
        "reply_to": str | None,
        "date": str | None,
        "message_id": str | None
    },
    "raw_source": {
        "sha256": str,
        "size_bytes": int,
        "ingested_at": str
    },
    "detection": {
        "classification": str,
        "risk_score": float,
        "model_version": str | None,
        "signals": list[str]
    },
    "authentication": {
        "spf": dict | None,
        "dkim": dict | None,
        "dmarc": dict | None,
        "alignment": dict | None
    },
    "relay_chain": [],
    "origin": {
        "earliest_reliable_ip": str | None,
        "confidence": float | None,
        "limitations": list[str]
    },
    "geolocation": {
        "country": str | None,
        "region": str | None,
        "city": str | None,
        "isp": str | None,
        "asn": str | None,
        "hosting": bool | None,
        "vpn": bool | None,
        "tor_exit": bool | None
    },
    "domain_intel": {},
    "reputation": {},
    "urls": [],
    "attachments": [],
    "correlation": {
        "entities": [],
        "relationships": [],
        "confidence": float | None,
        "rationale": []
    },
    "decision": {
        "level": str,
        "reasoning": [],
        "gmail_action": str | None
    },
    "evidence": {
        "items": [],
        "hashes": [],
        "timestamps": []
    }
}
```

`earliest_reliable_ip` must not be presented as a guaranteed attacker
IP. GeoLocation and external intelligence fields are nullable.

## Decision, Alerting & Feedback Contract

`decision.level` must be one of `SAFE`, `SUSPICIOUS`, `MALICIOUS`, or
`UNKNOWN`.

-   `alerts` records user/analyst notifications triggered by the
    decision.
-   `feedback` can record outcomes such as `CONFIRMED_THREAT`,
    `FALSE_POSITIVE`, `FALSE_NEGATIVE`, or `MARKED_SAFE`.
-   Feedback is initially for evaluation/audit; it must not silently
    retrain a production model.

## Evidence Governance

Evidence records should support: - evidence ID - SHA-256 hash -
capture/ingestion timestamp - source/message reference - access/action
history - retention status - report reference

All external intelligence fields remain nullable because providers can
be unavailable or inconclusive.
