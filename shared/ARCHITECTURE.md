# MailTrace AI — System Architecture & Integration Guide

> **Branch:** ``feature/integration-foundation``  
> **Author:** Member 6 — Integration & Architecture Lead  
> **Phase:** 1

---

## 1. System Overview

MailTrace AI is a **pre-delivery email security gateway** with its own webmail interface.
Every inbound email is intercepted, analysed, and given a risk decision **before** it reaches the user''s inbox.
Phase 1 uses mock data and a mock ML classifier — no real SMTP, no Gmail API.

---

## 2. Module Responsibilities

| Member | Module | Responsibility |
|--------|--------|----------------|
| **1** | React Frontend | Webmail UI — inbox, quarantine, forensic detail tabs |
| **2** | FastAPI Backend | REST APIs, orchestration, gateway simulation |
| **3** | Database (SQLAlchemy + SQLite) | Persistent storage of emails, events, analysis results |
| **4** | Security Engine | Header forensics, SPF/DKIM/DMARC, URL, attachment, PII analysis |
| **5** | ML Engine | NLP-based email classification (phishing / suspicious / benign) |
| **6** | Integration Lead | Shared contracts, enums, constants, architecture |

---

## 3. Email Pipeline

```
Sender
  ↓
MailTrace Gateway
  ↓
RECEIVED  (email queued in database)
  ↓
SCANNING  (Security Engine + ML Engine run in parallel)
  ↓
DECISION  (Risk Engine combines both outputs)
  ↓
 ┌──────────────────────────────────────────────┐
 │  riskScore < 25   →  DELIVERED  ✅           │
 │  25 <= score < 55 →  WARNING    ⚠️           │
 │  55 <= score < 90 →  QUARANTINED 🔒          │
 │  score >= 90      →  REJECTED   ❌           │
 │  error            →  FAILED     💀           │
 └──────────────────────────────────────────────┘
  ↓
MailTrace Inbox / Quarantine Store
  ↓
React Frontend (Member 1)
```

---

## 4. Shared Folder Structure

```
shared/
├── __init__.py
├── ARCHITECTURE.md
├── enums/
│   ├── __init__.py
│   ├── email_status.py      ← EmailStatus (9 states) — SINGLE SOURCE OF TRUTH
│   ├── decision.py          ← RiskDecision (5 terminal verdicts)
│   └── verdict.py           ← Verdict (SAFE/SUSPICIOUS/MALICIOUS/UNKNOWN)
├── contracts/
│   ├── __init__.py
│   ├── email_contract.py    ← Canonical shared email object
│   ├── security_result.py   ← Security Engine output contract
│   ├── ml_result.py         ← ML Engine output contract
│   ├── risk_decision.py     ← Risk Engine final decision contract
│   └── email_event.py       ← Lifecycle event contract
├── schemas/
│   ├── __init__.py
│   └── api_envelope.py      ← ApiEnvelope[T] standard API wrapper
├── constants/
│   ├── __init__.py
│   └── pipeline.py          ← Thresholds, phase flags, source tags
├── types/
│   ├── emailStatus.ts       ← TypeScript mirror of EmailStatus
│   └── contracts.ts         ← TypeScript interfaces for all contracts
└── tests/
    └── test_shared_contracts.py
```

---

## 5. Risk Score Thresholds

| Range       | Decision       |
|-------------|----------------|
| 0.0 – 24.9  | DELIVERED      |
| 25.0 – 54.9 | WARNING        |
| 55.0 – 89.9 | QUARANTINED    |
| 90.0 – 100  | REJECTED       |
| Error       | FAILED         |

Defined in: ``shared/constants/pipeline.py``

---

## 6. Integration Rules

### Always
- Import ``EmailStatus`` from ``shared.enums.email_status`` only
- Wrap backend responses in ``ApiEnvelope[T]``
- Use ``EmailContract`` at all API boundaries
- Emit ``EmailEventContract`` on every status transition

### Never
- Redefine ``EmailStatus`` in any other module
- Add business logic to contracts or enums
- Return raw dicts across module boundaries

---

## 7. Phase 2 — How Each Member Uses Shared Contracts

### Member 1 (React)
```ts
import type { EmailContract } from ''../../shared/types/contracts'';
import { getStatusColor } from ''../../shared/types/emailStatus'';
```

### Member 2 (Backend)
```python
from shared.contracts import EmailContract, RiskDecisionContract
from shared.schemas import ApiEnvelope
from shared.enums import EmailStatus
```

### Member 3 (Database)
```python
# Replace local enums with:
from shared.enums import EmailStatus, Verdict, DEFAULT_EMAIL_STATUS
```

### Member 4 (Security Engine)
```python
from shared.contracts import SecurityResultContract, SecuritySignal
# Wrap PolicyDecision output into SecurityResultContract
```

### Member 5 (ML Engine)
```python
from shared.contracts import MLResultContract
# Wrap MLInferenceResult.to_dict() into MLResultContract
```

---

## 8. Existing Enum Migration (Phase 2)

| File | Old | Replace With |
|------|-----|--------------|
| ``backend/app/schemas/enums.py`` | ``DeliveryStatusEnum``, ``VerdictEnum`` | ``shared.enums.EmailStatus``, ``shared.enums.Verdict`` |
| ``database/app/models/enums.py`` | ``EmailStatus``, ``Verdict`` | Re-export from ``shared.enums`` |
| ``security/analysis/security_policy.py`` | ``DeliveryAction`` | Map to ``shared.enums.RiskDecision`` |
