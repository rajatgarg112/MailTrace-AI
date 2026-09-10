# MailTrace AI — Evidence, Audit & Reporting

## 1. Evidence lifecycle

```text
Message Received
      ↓
Raw Source Hash
      ↓
Analysis Findings
      ↓
Risk Decision
      ↓
Delivery Action
      ↓
Case / Report
```

## 2. Evidence captured before delivery

Capture, where available:

- raw message hash;
- receipt timestamp;
- sender and recipient metadata;
- relevant headers;
- URLs;
- attachment hashes and metadata;
- analyzer results;
- external intelligence references;
- decision and policy version;
- delivery timing.

## 3. Forensic report

A report should contain:

1. Case summary
2. Message identity
3. Delivery timeline
4. Header/authentication findings
5. AI/ML findings
6. URL/domain findings
7. Attachment findings
8. Origin/GeoLocation evidence
9. Infrastructure correlation
10. Final risk classification
11. Delivery action
12. Evidence hashes
13. Limitations and confidence

## 4. Delivery timeline example

```text
10:20:01.100  Message received
10:20:01.120  Parsing started
10:20:01.300  AI/header checks running
10:20:02.050  URL reputation returned
10:20:02.220  Correlation complete
10:20:02.280  MALICIOUS decision
10:20:02.290  Message quarantined
```

The exact values are generated from the application timestamps; they should not be hard-coded in production.

## 5. Audit events

Record security-relevant events such as:

- message received;
- analysis started/completed;
- finding generated;
- delivery decision made;
- message delivered;
- message quarantined;
- quarantine released;
- case created;
- report generated.

## 6. Attribution limitation

MailTrace may provide infrastructure intelligence and investigative clues. An IP address, GeoLocation result, domain or hosting provider must not be represented as proof of an individual's identity.
