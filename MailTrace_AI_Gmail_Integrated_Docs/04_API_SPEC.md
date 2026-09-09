# MailTrace AI --- Gmail Integration API

Backend: FastAPI.

## POST `/gmail/events`

Accepts Gmail mailbox-change events and triggers message processing.

Responsibilities: - validate event - identify relevant changes - fetch
message - prevent duplicate processing - trigger analysis

## POST `/email/analyze`

Analyzes a raw email or `.eml` fixture for development/re-analysis.

## GET `/cases`

Lists forensic cases.

## POST `/cases`

Creates a manual case when required.

## GET `/cases/{case_id}`

Returns complete case analysis and evidence metadata.

## GET `/reports/{case_id}`

Generates or retrieves the integrity-verifiable report.

## Gmail Action Service

Keep Gmail-specific actions in a dedicated service: - labels - supported
message handling - action logging - previous-state recording - API error
handling

Never expose OAuth tokens or API secrets. Keep analysis independent from
Gmail-specific code.

## Risk Response Contract

Decision responses should expose:

``` json
{
  "level": "SAFE | SUSPICIOUS | MALICIOUS | UNKNOWN",
  "score": 0.0,
  "reasoning": [],
  "alerts": [],
  "gmail_action": null
}
```

Optional feedback endpoint/workflow can record analyst outcomes such as
confirmed threat, false positive, false negative and marked safe.

## Gmail Integration Constraint

`/gmail/events` represents a supported Gmail/Workspace event ingestion
path. It does not imply that MailTrace is positioned directly in Gmail's
SMTP delivery path or that it can replace Gmail's native spam
classifier.
