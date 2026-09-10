# MailTrace AI — Delivery-Time Testing

## 1. Primary acceptance criterion

The key demonstration requirement is:

> **An incoming email is analyzed before it appears as a normal delivered message in the recipient inbox.**

## 2. Functional tests

### Test 1 — Benign email
1. Submit a benign email to the delivery endpoint.
2. Verify `RECEIVED → SCANNING`.
3. Verify the analysis completes.
4. Verify `SAFE`.
5. Verify the message appears in Inbox.

### Test 2 — Phishing email
1. Submit the seeded phishing message.
2. Verify analysis occurs before Inbox delivery.
3. Verify phishing signals are shown.
4. Verify `MALICIOUS` or configured high-risk classification.
5. Verify the message is quarantined or rejected according to policy.

### Test 3 — Suspicious email
Verify that a suspicious message can be delivered with a warning or held for review according to policy.

### Test 4 — Missing intelligence
Disable an external intelligence provider. Verify the message does not become `SAFE` merely because the lookup failed.

### Test 5 — Attachment
Submit a message with a suspicious attachment. Verify the attachment is inspected safely and the message is not delivered as normal when policy requires quarantine.

## 3. Performance tests

Measure:

- parse latency;
- individual analyzer latency;
- parallel analysis latency;
- risk-decision latency;
- total delivery latency.

For the SIH demo, aim for **approximately 1–3 seconds for typical messages** on the local environment. Test separately with heavy attachments and slow external APIs.

## 4. Concurrency test

Submit multiple messages simultaneously and verify:

- delivery IDs remain unique;
- analyses do not overwrite each other;
- each message receives its own decision;
- the mailbox contains only messages permitted by policy.

## 5. UI tests

Verify the frontend visibly shows:

```text
Receiving → Scanning → Decision → Delivery
```

For malicious messages:

```text
Receiving → Scanning → MALICIOUS → Quarantined
```

## 6. Regression tests

Every change to the detection engine must rerun benign, phishing, spoofing, BEC, URL and attachment scenarios.
