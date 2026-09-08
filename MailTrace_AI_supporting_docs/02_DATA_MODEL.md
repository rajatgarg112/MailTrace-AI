# MailTrace AI — Data Model

This document defines the core data contract used across the pipeline.

## Core `EmailAnalysis`

```python
{
    "email_id": str,
    "case_id": str | None,

    "message": {
        "subject": str | None,
        "from": str | None,
        "to": list[str],
        "date": str | None,
        "message_id": str | None
    },

    "raw_source": {
        "sha256": str,
        "size_bytes": int
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

    "relay_chain": [
        {
            "ip": str | None,
            "hostname": str | None,
            "timestamp": str | None,
            "reliability": float | None,
            "evidence": str
        }
    ],

    "origin": {
        "earliest_reliable_ip": str | None,
        "confidence": float | None,
        "limitations": list[str]
    },

    "domain_intel": {
        "domain": str | None,
        "created_date": str | None,
        "dns": dict | None,
        "whois": dict | None
    },

    "reputation": {
        "abuse_score": float | None,
        "tor_exit": bool | None,
        "vpn": bool | None,
        "hosting": bool | None,
        "known_malicious": bool | None,
        "botnet_indicator": bool | None
    },

    "urls": [],
    "attachments": [],

    "correlation": {
        "entities": [],
        "relationships": [],
        "confidence": float | None,
        "rationale": []
    },

    "evidence": {
        "items": [],
        "hashes": [],
        "timestamps": []
    }
}
```

## Important Rules

- Do not use `true_origin_ip` as a field.
- Use `earliest_reliable_ip`.
- WHOIS, DNS and reputation data may be unavailable.
- Authentication results should distinguish observed results from independently verified results.
- Risk score and classification must not be treated as proof of malicious activity.
