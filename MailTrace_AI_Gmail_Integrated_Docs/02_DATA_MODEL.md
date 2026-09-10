# MailTrace AI — Delivery-Time Data Model

The data model represents an email **before, during, and after delivery**.

## 1. Message contract

```python
{
  "email_id": str,
  "delivery_id": str,
  "mailbox_id": str,
  "status": "RECEIVED | SCANNING | DELIVERED | WARNING | QUARANTINED | REJECTED | FAILED",
  "message": {
    "subject": str | None,
    "from": str | None,
    "to": list[str],
    "cc": list[str],
    "reply_to": str | None,
    "date": str | None,
    "message_id": str | None,
    "body_text": str | None,
    "body_html": str | None
  },
  "raw_source": {
    "sha256": str,
    "size_bytes": int,
    "source_type": "SMTP_SIMULATION | API | EML_IMPORT | FUTURE_EXTERNAL_MTA",
    "received_at": str
  },
  "analysis": {
    "status": "PENDING | RUNNING | COMPLETE | FAILED",
    "classification": "SAFE | SUSPICIOUS | MALICIOUS | UNKNOWN | None",
    "risk_score": float | None,
    "model_version": str | None,
    "signals": list[str]
  },
  "timing": {
    "received_at": str,
    "scan_started_at": str | None,
    "scan_completed_at": str | None,
    "delivery_started_at": str | None,
    "delivered_at": str | None,
    "scan_latency_ms": int | None,
    "total_delivery_latency_ms": int | None
  },
  "authentication": {
    "spf": dict | None,
    "dkim": dict | None,
    "dmarc": dict | None,
    "alignment": dict | None
  },
  "relay_chain": [],
  "origin": {},
  "geolocation": {},
  "domain_intel": {},
  "reputation": {},
  "urls": [],
  "attachments": [],
  "correlation": {},
  "decision": {
    "level": "SAFE | SUSPICIOUS | MALICIOUS | UNKNOWN",
    "action": "DELIVER | WARN | QUARANTINE | REJECT | HOLD",
    "reasoning": []
  },
  "evidence": {
    "items": [],
    "hashes": [],
    "timestamps": []
  }
}
```

## 2. Minimum database tables

```text
users
mailboxes
delivery_events
messages
message_recipients
attachments
message_urls
analysis_runs
findings
delivery_decisions
quarantine_items
cases
evidence_items
reports
audit_events
```

## 3. Timing fields

Every delivery should record:

- message received time;
- analysis start time;
- analysis completion time;
- delivery time;
- scan latency;
- total delivery latency.

This allows the demo dashboard to show measurable performance instead of claiming an arbitrary scan time.

## 4. Decision contract

Risk classification:

`SAFE | SUSPICIOUS | MALICIOUS | UNKNOWN`

Delivery action:

`DELIVER | WARN | QUARANTINE | REJECT | HOLD`

Classification and action are separate because an organization may choose different policies.

## 5. Evidence

Each important finding should contain:

- finding ID;
- evidence type;
- source message/delivery ID;
- timestamp;
- SHA-256 where applicable;
- confidence;
- explanation;
- analyzer/version.
