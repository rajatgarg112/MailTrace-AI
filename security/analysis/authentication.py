"""
MailTrace AI — Cryptographic Authentication Audit Module

Parses and validates SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail),
and DMARC (Domain-based Message Authentication) email authentication status.
Supports explicit UNKNOWN states when cryptographic evidence is missing or unverified.
"""

from dataclasses import dataclass
from enum import Enum
from email.message import Message
from email.parser import Parser
import re
from typing import Optional, List, Dict


class AuthStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SOFTFAIL = "SOFTFAIL"
    NEUTRAL = "NEUTRAL"
    NONE = "NONE"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


@dataclass
class AuthenticationResult:
    spf_status: AuthStatus
    spf_domain: Optional[str]
    dkim_status: AuthStatus
    dkim_domain: Optional[str]
    dmarc_status: AuthStatus
    dmarc_policy: Optional[str]  # e.g., 'reject', 'quarantine', 'none'
    overall_auth_score: float  # 0.0 (Failed/Forged) to 100.0 (Fully Authenticated)
    is_authenticated: bool
    auth_summary: str
    details: List[str]


class AuthenticationAnalyzer:
    """Cryptographic Email Authentication Evaluator"""

    def analyze(self, raw_email_or_msg: str | bytes | Message) -> AuthenticationResult:
        """Parses email authentication headers and evaluates SPF, DKIM, and DMARC."""
        if isinstance(raw_email_or_msg, Message):
            msg = raw_email_or_msg
        elif isinstance(raw_email_or_msg, bytes):
            msg = Parser().parsestr(raw_email_or_msg.decode("utf-8", errors="replace"))
        else:
            msg = Parser().parsestr(str(raw_email_or_msg))

        details: List[str] = []

        # Parse Authentication-Results header
        auth_results_header = msg.get("Authentication-Results", "")
        received_spf_header = msg.get("Received-SPF", "")
        dkim_sig_header = msg.get("DKIM-Signature", "")

        # 1. Evaluate SPF
        spf_status, spf_domain = self._eval_spf(auth_results_header, received_spf_header)
        details.append(f"SPF Status: {spf_status.value}" + (f" (domain: {spf_domain})" if spf_domain else ""))

        # 2. Evaluate DKIM
        dkim_status, dkim_domain = self._eval_dkim(auth_results_header, dkim_sig_header)
        details.append(f"DKIM Status: {dkim_status.value}" + (f" (domain: {dkim_domain})" if dkim_domain else ""))

        # 3. Evaluate DMARC
        dmarc_status, dmarc_policy = self._eval_dmarc(auth_results_header, spf_status, dkim_status)
        details.append(
            f"DMARC Status: {dmarc_status.value}" + (f" (policy: {dmarc_policy})" if dmarc_policy else "")
        )

        # Compute overall authentication score (0 to 100)
        overall_score, is_authenticated = self._calculate_auth_score(spf_status, dkim_status, dmarc_status)

        summary = f"SPF={spf_status.value}, DKIM={dkim_status.value}, DMARC={dmarc_status.value}"

        return AuthenticationResult(
            spf_status=spf_status,
            spf_domain=spf_domain,
            dkim_status=dkim_status,
            dkim_domain=dkim_domain,
            dmarc_status=dmarc_status,
            dmarc_policy=dmarc_policy,
            overall_auth_score=overall_score,
            is_authenticated=is_authenticated,
            auth_summary=summary,
            details=details,
        )

    def _eval_spf(self, auth_header: str, spf_header: str) -> tuple[AuthStatus, Optional[str]]:
        """Evaluates Received-SPF or Authentication-Results for SPF details."""
        combined = f"{auth_header} {spf_header}".lower()

        domain_match = re.search(r"spf=([a-z]+).*?identity=([^\s;]+)", combined)
        spf_domain = None
        if domain_match:
            spf_domain = domain_match.group(2)

        if "spf=pass" in combined or "pass (google.com:" in combined or spf_header.lower().startswith("pass"):
            return AuthStatus.PASS, spf_domain
        elif "spf=fail" in combined or spf_header.lower().startswith("fail"):
            return AuthStatus.FAIL, spf_domain
        elif "spf=softfail" in combined or spf_header.lower().startswith("softfail"):
            return AuthStatus.SOFTFAIL, spf_domain
        elif "spf=neutral" in combined:
            return AuthStatus.NEUTRAL, spf_domain
        elif "spf=none" in combined:
            return AuthStatus.NONE, spf_domain
        elif not auth_header and not spf_header:
            return AuthStatus.UNKNOWN, None

        return AuthStatus.UNKNOWN, spf_domain

    def _eval_dkim(self, auth_header: str, dkim_header: str) -> tuple[AuthStatus, Optional[str]]:
        """Evaluates DKIM-Signature and Authentication-Results for DKIM status."""
        auth_lower = auth_header.lower()

        domain_match = re.search(r"d=([a-zA-Z0-9.-]+)", dkim_header)
        dkim_domain = domain_match.group(1) if domain_match else None

        if "dkim=pass" in auth_lower or "header.i=" in auth_lower and "pass" in auth_lower:
            return AuthStatus.PASS, dkim_domain
        elif "dkim=fail" in auth_lower:
            return AuthStatus.FAIL, dkim_domain
        elif "dkim=neutral" in auth_lower or "dkim=none" in auth_lower:
            return AuthStatus.NONE, dkim_domain
        elif dkim_header and not auth_header:
            # Has DKIM signature header but unverified by receiver
            return AuthStatus.UNKNOWN, dkim_domain
        elif not dkim_header and not auth_header:
            return AuthStatus.NONE, None

        return AuthStatus.UNKNOWN, dkim_domain

    def _eval_dmarc(
        self, auth_header: str, spf_status: AuthStatus, dkim_status: AuthStatus
    ) -> tuple[AuthStatus, Optional[str]]:
        """Evaluates DMARC alignment and policy."""
        auth_lower = auth_header.lower()

        policy_match = re.search(r"dmarc=pass.*?p=([a-z]+)", auth_lower)
        dmarc_policy = policy_match.group(1) if policy_match else None

        if "dmarc=pass" in auth_lower:
            return AuthStatus.PASS, dmarc_policy or "none"
        elif "dmarc=fail" in auth_lower:
            return AuthStatus.FAIL, dmarc_policy or "reject"
        elif spf_status == AuthStatus.PASS or dkim_status == AuthStatus.PASS:
            # Implicit DMARC alignment pass if either SPF or DKIM passes
            return AuthStatus.PASS, "none"
        elif spf_status == AuthStatus.FAIL and dkim_status == AuthStatus.FAIL:
            return AuthStatus.FAIL, "quarantine"
        elif spf_status == AuthStatus.UNKNOWN and dkim_status == AuthStatus.UNKNOWN:
            return AuthStatus.UNKNOWN, None

        return AuthStatus.NONE, None

    def _calculate_auth_score(
        self, spf: AuthStatus, dkim: AuthStatus, dmarc: AuthStatus
    ) -> tuple[float, bool]:
        """Calculates auth score from 0.0 to 100.0."""
        score = 50.0  # Base neutral starting score

        if spf == AuthStatus.PASS:
            score += 25.0
        elif spf == AuthStatus.FAIL:
            score -= 25.0
        elif spf == AuthStatus.SOFTFAIL:
            score -= 15.0

        if dkim == AuthStatus.PASS:
            score += 25.0
        elif dkim == AuthStatus.FAIL:
            score -= 25.0

        if dmarc == AuthStatus.PASS:
            score += 20.0
        elif dmarc == AuthStatus.FAIL:
            score -= 30.0

        score = max(0.0, min(100.0, score))
        is_authenticated = score >= 70.0

        return score, is_authenticated
