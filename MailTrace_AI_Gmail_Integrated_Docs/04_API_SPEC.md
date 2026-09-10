# MailTrace AI — Delivery Gateway API Specification

The API models MailTrace as an email-security gateway and mailbox service.

## 1. Receive an email

`POST /api/deliveries`

Creates a delivery transaction and starts pre-delivery analysis.

Example request:

```json
{
  "recipient": "user@mailtrace.local",
  "raw_email": "<RFC-5322 message>",
  "source": "SMTP_SIMULATION"
}
```

Example response:

```json
{
  "delivery_id": "del_123",
  "status": "SCANNING"
}
```

## 2. Delivery status

`GET /api/deliveries/{delivery_id}`

Returns:

- current delivery status;
- analysis status;
- risk classification;
- risk score;
- decision action;
- scan latency;
- total delivery latency.

## 3. Mailbox

`GET /api/mailboxes/{mailbox_id}/messages`

Returns messages that have passed through the MailTrace delivery pipeline.

`GET /api/messages/{email_id}`

Returns message content plus security findings.

## 4. Quarantine

`GET /api/quarantine`

`POST /api/quarantine/{email_id}/release`

`POST /api/quarantine/{email_id}/delete`

Quarantine is an application-owned security store in the prototype.

## 5. Analysis details

`GET /api/messages/{email_id}/analysis`

Returns:

```json
{
  "classification": "MALICIOUS",
  "risk_score": 0.96,
  "signals": [
    "credential harvesting",
    "suspicious URL",
    "sender/domain mismatch"
  ],
  "timing": {
    "scan_latency_ms": 1420,
    "total_delivery_latency_ms": 1510
  }
}
```

## 6. Demo injection endpoints

For SIH demonstrations:

`POST /api/demo/seed/phishing`
`POST /api/demo/seed/benign`
`POST /api/demo/seed/spoofed-sender`
`POST /api/demo/seed/bec`
`POST /api/demo/seed/suspicious-attachment`

These endpoints should create an incoming delivery transaction, not simply insert a message directly into Inbox.

## 7. Delivery event stream

The frontend may subscribe to:

`GET /api/deliveries/{delivery_id}/events`

Events:

```text
RECEIVED
PARSING
ANALYZING
CORRELATING
DECIDING
DELIVERED / WARNING / QUARANTINED / REJECTED / HOLD
```

This supports a live delivery-security animation in the UI.
