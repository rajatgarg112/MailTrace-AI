# MailTrace AI — Delivery-Time Analysis Pipeline

## 1. Objective

MailTrace analyzes an incoming message **inside the delivery path** so that the security verdict is available before normal inbox delivery.

## 2. Pipeline

```text
Incoming Message
      ↓
Receive + Preserve
      ↓
Parse / Normalize
      ↓
Fast Parallel Analysis
 ┌────┬────┬────┬────┬────┐
 ↓    ↓    ↓    ↓    ↓    ↓
AI  Header Auth URL Attach Origin/TI
 └────┴────┴────┴────┴────┘
              ↓
       Correlation Engine
              ↓
          Risk Engine
              ↓
       Delivery Policy
              ↓
 Deliver / Warn / Quarantine / Reject / Hold
```

## 3. Phase 1 — Ingress

Accept the message through:

- simulated SMTP delivery;
- REST delivery endpoint; or
- `.eml` import for testing.

Immediately generate a `delivery_id`, capture the raw source, calculate SHA-256, and timestamp receipt.

## 4. Phase 2 — Fast parsing

Extract:

- headers;
- sender/recipient;
- body;
- URLs;
- attachments;
- message timestamps;
- relay information.

Parsing must be lightweight enough to start downstream analyzers quickly.

## 5. Phase 3 — Parallel security analysis

### AI/NLP
Detect:

- phishing language;
- credential requests;
- financial fraud;
- impersonation;
- BEC/payment diversion;
- social engineering.

### Header forensics
Inspect:

- Received chain;
- Return-Path;
- Message-ID;
- Reply-To;
- timestamp anomalies;
- sender/domain mismatches.

### Authentication
When evidence is available, analyze SPF, DKIM and DMARC. Missing evidence must remain `UNKNOWN` rather than being treated as failure or success.

### URLs and domains
Check:

- URL structure;
- domain reputation;
- redirects where safely supported;
- domain age/reputation signals;
- known malicious indicators.

### Attachments
Perform safe static inspection:

- file type;
- extension mismatch;
- hash;
- macro/script indicators;
- archive characteristics;
- malware reputation where available.

Never execute an untrusted attachment directly in the application server.

### Origin / GeoLocation / intelligence
Use observable relay/IP data to enrich the investigation. GeoLocation is evidence about infrastructure and is not proof of a person's physical location.

## 6. Phase 4 — Correlation

Correlate:

```text
Sender ↔ Domain ↔ IP ↔ URL ↔ Attachment ↔ Prior Cases
```

The correlation engine produces explainable relationships and confidence values.

## 7. Phase 5 — Risk and delivery decision

```text
Evidence
   ↓
Risk Score
   ↓
Classification
   ↓
Policy
   ├── SAFE → DELIVER
   ├── SUSPICIOUS → WARN / HOLD
   ├── MALICIOUS → QUARANTINE / REJECT
   └── UNKNOWN → HOLD / WARN / DELIVER BY POLICY
```

## 8. Performance design

The delivery path should avoid unnecessary sequential calls.

Recommended approach:

1. Parse once.
2. Run independent checks concurrently.
3. Cache reputation/intelligence where safe.
4. Apply strict timeouts to external services.
5. Use a fast path for clearly benign messages.
6. Use deeper analysis for high-risk or ambiguous messages.

Target demo latency: approximately **1–3 seconds for typical messages**, with a visible `SCANNING` state. Heavier attachments or external sandboxing may exceed this target.

## 9. Fail-safe behavior

If an analyzer times out:

- record the failure;
- preserve the evidence;
- do not silently convert missing evidence into `SAFE`;
- let the delivery policy decide whether to warn, hold, or quarantine.
