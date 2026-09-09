# MailTrace AI --- Gmail-Integrated Documentation

These documents reflect the final direction: **MailTrace AI is primarily
a Gmail-integrated AI email security and forensic intelligence engine,
not a standalone upload website.**

## Core pillars

-   AI threat detection
-   email/header forensics
-   GeoLocation and origin analysis
-   URL and attachment analysis
-   threat intelligence
-   infrastructure correlation
-   attribution support
-   evidence preservation
-   forensic reporting
-   Gmail automated handling

## Reading order

1.  `scaffold.md`
2.  `01_ARCHITECTURE.md`
3.  `02_DATA_MODEL.md`
4.  `03_ANALYSIS_PIPELINE.md`
5.  `04_API_SPEC.md`
6.  `05_EVIDENCE_AND_REPORTING.md`
7.  `06_TESTING.md`
8.  `07_SETUP_AND_TEAM_WORKFLOW.md`

The optional analyst dashboard is secondary. The primary runtime begins
with an incoming Gmail message and ends with an evidence-backed Gmail
action and forensic case record.

## Finalized Product Boundary

MailTrace AI is a Gmail-integrated security/forensic engine, not a
standalone email upload website.

The system analyzes messages after supported Gmail/Workspace ingestion
events, then applies supported actions such as labels/review/quarantine
workflows. It should not be presented as a replacement for Gmail's
native spam infrastructure or as a guaranteed pre-delivery SMTP blocker.

## Final Risk States

`SAFE | SUSPICIOUS | MALICIOUS | UNKNOWN`

UNKNOWN is important when evidence is missing, conflicting or external
intelligence is unavailable.

## Forensics

Forensics is performed throughout ingestion and analysis. The final PDF
is only an integrity-verifiable presentation of the evidence trail.
