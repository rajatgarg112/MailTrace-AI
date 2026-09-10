# PlaceMate AI — Comprehensive Security Documentation & Threat Model

**Project Name**: PlaceMate AI — Interactive Placement Preparation Portal  
**Branch**: `feature/security-foundation`  
**Role**: Member 4 — Security Developer  
**Target Audience**: SIH Evaluators, Developers, System Administrators  

---

## 1. Security Architecture

PlaceMate AI is an interactive placement-preparation portal designed for students. The security architecture protects sensitive student placement records (personal profile details, academic records, coding preparation progress, aptitude test results, mock interview transcripts, and company application status).

```text
                  STUDENT CLIENT (React.js)
                             │
            HTTP Requests + Bearer JWT Token
                             │
                             ▼
              SECURITY MIDDLEWARE (FastAPI)
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
Security Headers       CORS Whitelist       Input Sanitizer & Pydantic
(nosniff, DENY, XSS)  (ALLOWED_ORIGINS)       (XSS/Script Strip)
    │                        │                        │
    └────────────────────────┼────────────────────────┘
                             │
                             ▼
                AUTHORIZATION DEPENDENCY
          verify_student_ownership (student_id)
                             │
                             ▼
                  APPLICATION CONTROLLERS
                  & DATA ACCESS LAYER
```

### Security Boundaries & Layers:
- **Frontend / Backend Boundary**: The React.js frontend handles state presentation. The FastAPI backend enforces authentication, authorization dependencies, and input sanitization on all API routes.
- **API Protection**: All protected routes require a cryptographically signed HMAC-SHA256 JWT Bearer token in the `Authorization` header.
- **Database Protection**: In-memory data stores index student records by `student_id`. Sensitive credentials (passwords) are hashed before storage and are never stored in plaintext.
- **Student Data Protection**: Reusable authorization dependencies (`verify_student_ownership`) restrict access so a student can view and edit only their own placement data.

---

## 2. Authentication

### How Users Authenticate:
1. **Registration** (`POST /api/auth/register`):
   - Accepts student `name`, `email`, and `password`.
   - Validates input format and enforces password complexity policy.
   - Hashes password using PBKDF2-HMAC-SHA256.
   - Generates and returns a signed JWT access token.
2. **Login** (`POST /api/auth/login`):
   - Accepts `email` and `password`.
   - Normalizes email (`strip().lower()`).
   - Verifies password using constant-time hash comparison (`hmac.compare_digest`).
   - Generates and returns a signed JWT access token.

### Password Handling:
- **Hashing Engine**: OWASP-aligned PBKDF2-HMAC-SHA256 using 600,000 iterations and a cryptographically secure 16-byte random salt (`secrets.token_bytes(16)`).
- **Format**: `pbkdf2:sha256:600000$<salt_hex>$<hash_hex>`.
- **Zero Plaintext Storage**: Plaintext passwords are processed in-memory during authentication and discarded immediately. Plaintext passwords are never stored in database records or logged.

### Session & Token Handling:
- **Token Type**: Stateless JSON Web Token (JWT) signed via HMAC-SHA256 (`HS256`).
- **Signature Secret**: Derived from `PLACEMATE_SECRET_KEY` environment variable.
- **Expiration**: Claims include `iat` (issued at) and `exp` (expiration timestamp, defaulting to 60 minutes via `PLACEMATE_TOKEN_EXPIRE_MINUTES`).

### Protected Endpoints & Logout Behavior:
- **Protected Endpoint**: `GET /api/auth/me` requires `Authorization: Bearer <token>`.
- **Logout**: Stateless token-based architecture allowing clients to destroy local tokens upon logout.

> [!NOTE]
> **Limitation**: Token revocation (token blacklist) is not currently implemented in Phase 1 and is planned for Phase 2 via Redis.

---

## 3. Authorization

### Student Ownership & Access Control:
- Each student account is assigned a unique immutable identifier (`student_id`).
- All student-specific placement assets (coding progress, aptitude scores, interview feedback, company applications) are tagged with `student_id`.

### Access Control Mechanism:
- **`get_current_student`**: Reusable FastAPI dependency verifying Bearer token validity and returning `StudentTokenPayload`.
- **`verify_student_ownership(requested_student_id)`**: Dependency comparing `current_student.student_id` against `requested_student_id`.
  - Mismatch results in immediate `403 Forbidden` response: `"Access Denied: You are not authorized to view or modify another student's placement data."`

---

## 4. Input Validation & Data Sanitization

The `InputSanitizer` module in [`validation.py`](file:///d:/SIH%20PROJECT/MailTrace-AI/security/core/security/validation.py) sanitizes incoming user strings to prevent script injection and HTML tampering across all application modules:

| Input Field | Validation / Sanitization Logic | Prevented Threat |
|-------------|--------------------------------|------------------|
| **Student Name** | Length check (2–100 chars); HTML entity escaping; XSS regex stripping | Stored / Reflected XSS |
| **Student Email** | RFC 5322 regex check; case-insensitive normalization; length limit (254 chars) | Malformed input, SQL/Command injection |
| **Password** | Length check (min 8 chars); requires uppercase letter and digit | Weak credentials, brute-force |
| **Coding Answers** | Max size limit (10,000 chars); language string sanitization | Payload bloat, script injection |
| **Aptitude Answers** | Pydantic type enforcement (integer option IDs / sanitized option strings) | Type confusion attacks |
| **Interview Responses** | Sanitized text inputs; script tag removal | Reflected XSS in interview dashboard |
| **Company Applications** | Length check (2–100 chars); HTML escaping for notes | Input tampering, XSS in application list |
| **Search Queries** | Sanitized query string; stripping HTML tags | Injection via search parameters |

---

## 5. API Security

- **Authentication**: Bearer JWT token required for private APIs. Missing/invalid tokens return `401 Unauthorized`.
- **Authorization**: `verify_student_ownership` dependency enforces student resource boundaries (`403 Forbidden`).
- **Input Validation**: Pydantic schema validation returns `422 Unprocessable Entity` for invalid payloads.
- **CORS Configuration**: Configured via `SecurityConfig.ALLOWED_ORIGINS` (defaults to local development origins; configurable per environment).
- **Error Handling**: Exception handlers catch unhandled errors and return generic JSON error messages in production mode, suppressing Python stack traces and internal paths.
- **Sensitive Data Protection**: Passwords, password hashes, JWT secrets, and internal database details are omitted from API response schemas.

---

## 6. Secret Management

- **Centralized Configuration**: All security settings are managed in [`config.py`](file:///d:/SIH%20PROJECT/MailTrace-AI/security/core/security/config.py) reading from environment variables:
  - `PLACEMATE_ENV` (e.g. `development`, `production`)
  - `PLACEMATE_SECRET_KEY`
  - `PLACEMATE_TOKEN_EXPIRE_MINUTES`
  - `PLACEMATE_ALLOWED_ORIGINS`
- **Git Protection**: `.env` and sensitive key files are excluded via [`.gitignore`](file:///d:/SIH%20PROJECT/MailTrace-AI/.gitignore).
- **Template Provided**: [`.env.example`](file:///d:/SIH%20PROJECT/MailTrace-AI/.env.example) is provided as a configuration reference.

---

## 7. Data Privacy & Student Protection

- **Data Minimization**: API endpoints return only necessary data fields (`student_id`, `name`, `email`, `role`). Passwords and internal system keys are excluded.
- **Logging Safety**: `SecurityLogger` filters out sensitive parameters (`password`, `token`, `secret`, `hash`) before writing log records.
- **Frontend Exposure**: React components use standard JSX string rendering, preventing execution of user-supplied HTML strings.

---

## 8. Security Logging Foundation

The `SecurityLogger` in [`logging.py`](file:///d:/SIH%20PROJECT/MailTrace-AI/security/core/security/logging.py) records security-relevant events in JSON format:

- `LOGIN_SUCCESS`: Logged upon successful authentication with student ID, email, client IP, and timestamp.
- `LOGIN_FAILED`: Logged upon failed login attempt with attempted email, client IP, and sanitized reason.
- `UNAUTHORIZED_ACCESS_ATTEMPT`: Logged when an unauthenticated or unauthorized request hits a protected endpoint.

Guaranteed rule: **NO passwords, plaintext secrets, or JWT tokens are written to logs.**

---

## 9. Security Threat Model

| # | Threat | Impact | Likelihood | Current Protection | Remaining Risk | Future Mitigation |
|---|--------|--------|------------|--------------------|----------------|-------------------|
| **1** | **Unauthorized Account Access** | High (Student data exposed) | Medium | Signed HMAC-SHA256 JWT tokens with expiration | Stolen token valid until `exp` | Redis-backed token revocation / blacklist |
| **2** | **Weak Password Handling** | High (Account takeover) | High | Enforced password policy (min 8 chars, uppercase, digit) | User reuses password on external site | 2FA / TOTP authentication |
| **3** | **Credential Theft in Transit** | High (Session interception) | Low | Bearer token architecture; security HTTP headers | Traffic intercepted on unencrypted HTTP | Enforce HTTPS/TLS and HSTS header |
| **4** | **Cross-Student Data Access** | Critical (Privacy breach) | Medium | `verify_student_ownership` dependency checking `student_id` | Developer forgets dependency on new route | Automated API authorization regression tests |
| **5** | **Malicious Input / Script Injection** | Medium (Defacement / XSS) | High | `InputSanitizer` strips script/HTML tags; Pydantic validation | Complex obfuscated script payloads | Content Security Policy (CSP) nonces |
| **6** | **SQL Injection** | Critical (Database compromise) | Low | In-memory store; ORM / parameterized query pattern | Raw SQL queries introduced in future | Enforce ORM parameterization only |
| **7** | **Stored / Reflected XSS** | Medium (Client script execution) | Medium | React default JSX string escaping + backend HTML sanitization | Dangerous `dangerouslySetInnerHTML` usage | ESLint security plugin rule in CI |
| **8** | **API Abuse & Automated Attacks** | Medium (Denial of Service) | High | Sanitized error handlers preventing server stack leaks | No request rate limit per IP | Redis token-bucket rate limiting |
| **9** | **Sensitive Information Leakage** | High (Data leak) | Medium | Response schemas exclude passwords/hashes; audit log filter | Debug endpoints left enabled | Automated secrets scanner in CI |
| **10** | **Incorrect CORS Configuration** | Medium (Cross-origin data read) | Low | Configurable `ALLOWED_ORIGINS` via environment variables | Origin whitelist set to `*` in production | Strict origin check in production config |
| **11** | **Exposed Secrets in Git** | Critical (Infrastructure compromise) | Low | `.env` added to `.gitignore`; `.env.example` template provided | Developer commits `.env` manually | Pre-commit git hooks for secret scanning |
| **12** | **Session / Token Misuse** | High (Unapproved actions) | Medium | Strict token expiration timestamp (`exp` claim) | Token stolen before expiration | Short token lifespan + Refresh token flow |
| **13** | **Unauthorized Modification of Records** | High (Data tampering) | Medium | Authorization checks on update/delete endpoints | Missing check on batch endpoints | Row-level authorization verification |

---

## 10. Security Limitations (Phase 1 Status)

To maintain complete transparency for SIH evaluators, the following capabilities are **NOT** currently implemented in Phase 1:
- **No Redis Rate-Limiting**: Request rate-limiting per IP address is not yet active.
- **No 2FA / TOTP**: Multi-Factor Authentication is not yet supported.
- **No OAuth2 / University SSO**: Single Sign-On integration is deferred.
- **No Persistent Database RLS**: In-memory database store is used for demonstration speed.

---

## 11. Future Improvements (Phase 2 Roadmap)

1. **OAuth2 / Google Workspace SSO**: Allow students to log in using institutional college emails.
2. **Two-Factor Authentication (2FA)**: Add TOTP authenticator app support for placement officers.
3. **Redis Rate Limiting**: Throttle login endpoints to 5 attempts per minute per IP address.
4. **Persistent Relational Database**: Migrate in-memory store to PostgreSQL / MySQL with Row-Level Security (RLS).
5. **Token Refresh & Revocation**: Short-lived access tokens (15 mins) paired with revocable refresh tokens.

---

## 12. Final Documentation Verification

- **Code Accuracy**: Every feature documented above corresponds directly to functional code in `security/core/security/` and `security/app/main.py`.
- **Zero Exposed Secrets**: All examples use generic template variables.
- **SIH Compliance**: Provides a practical, verifiable security foundation protecting student data without unnecessary complexity.
