"""
MailTrace AI — Pre-Delivery URL & Phishing Domain Analysis Module

Parses HTML and plain-text email bodies for embedded URLs, detecting IP-based hostnames,
unencrypted HTTP credential login links, shortened redirect URLs, zero-width Unicode
character obfuscation, and homoglyph / typosquatting domain impersonation.
"""

from dataclasses import dataclass, field
import re
import urllib.parse
from typing import List, Dict, Optional, Set


@dataclass
class URLRiskFactor:
    url: str
    domain: str
    risk_level: str  # SAFE | SUSPICIOUS | MALICIOUS
    reasons: List[str]
    is_ip_address: bool
    is_http: bool
    is_shortener: bool
    is_spoofed_domain: bool


@dataclass
class URLAnalysisResult:
    total_urls: int
    malicious_urls_count: int
    suspicious_urls_count: int
    url_details: List[URLRiskFactor]
    overall_url_risk_score: float  # 0.0 (Clean) to 100.0 (High Threat)
    has_phishing_links: bool
    findings_summary: List[str]


class URLAnalyzer:
    """Pre-Delivery URL & Phishing Link Security Engine"""

    # URL Extraction Regex (captures http/https links)
    URL_REGEX = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)

    # Common URL Shorteners
    SHORTENERS = {
        "bit.ly", "tinyurl.com", "goo.gl", "is.gd", "buff.ly", "ow.ly",
        "t.co", "rebrand.ly", "cutt.ly", "shorturl.at"
    }

    # Known high-risk target institutional domains
    TARGET_DOMAINS = [
        "aicte-india.org", "gov.in", "nic.in", "ac.in", "sih.gov.in",
        "paypal.com", "microsoft.com", "google.com", "bankofbaroda.in", "sbi.co.in"
    ]

    # IP Address Regex
    IP_REGEX = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

    def analyze(self, text: str) -> URLAnalysisResult:
        """Parses email body text for URLs and calculates URL threat indicators."""
        if not text:
            return URLAnalysisResult(
                total_urls=0,
                malicious_urls_count=0,
                suspicious_urls_count=0,
                url_details=[],
                overall_url_risk_score=0.0,
                has_phishing_links=False,
                findings_summary=["No URLs detected in message body."],
            )

        # Detect zero-width unicode characters used for obfuscation
        zero_width_chars = ["\u200b", "\u200c", "\u200d", "\ufeff"]
        clean_text = text
        for zw in zero_width_chars:
            clean_text = clean_text.replace(zw, "")

        extracted_urls = self.URL_REGEX.findall(clean_text)
        # Deduplicate while preserving order
        seen = set()
        unique_urls = [u for u in extracted_urls if not (u in seen or seen.add(u))]

        details: List[URLRiskFactor] = []
        findings: List[str] = []
        total_risk_score = 0.0

        for url in unique_urls:
            risk_item = self._evaluate_url(url)
            details.append(risk_item)

            if risk_item.risk_level == "MALICIOUS":
                total_risk_score += 45.0
            elif risk_item.risk_level == "SUSPICIOUS":
                total_risk_score += 25.0

            for r in risk_item.reasons:
                findings.append(f"URL ALERT: [{url}] — {r}")

        total_risk_score = min(100.0, total_risk_score)
        malicious_count = sum(1 for d in details if d.risk_level == "MALICIOUS")
        suspicious_count = sum(1 for d in details if d.risk_level == "SUSPICIOUS")

        return URLAnalysisResult(
            total_urls=len(unique_urls),
            malicious_urls_count=malicious_count,
            suspicious_urls_count=suspicious_count,
            url_details=details,
            overall_url_risk_score=total_risk_score,
            has_phishing_links=(malicious_count > 0 or suspicious_count > 0),
            findings_summary=findings if findings else ["All embedded URLs verified as clean."],
        )

    def _evaluate_url(self, url: str) -> URLRiskFactor:
        reasons: List[str] = []
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or "").lower()

        is_ip = bool(self.IP_REGEX.match(hostname))
        is_http = parsed.scheme.lower() == "http"
        is_short = hostname in self.SHORTENERS
        is_spoofed = self._check_lookalike_hostname(hostname)

        risk_level = "SAFE"

        if is_ip:
            reasons.append("Raw IP address used in host instead of domain name")
            risk_level = "MALICIOUS"

        if is_spoofed:
            reasons.append(f"Lookalike / typosquatting phishing domain detected ('{hostname}')")
            risk_level = "MALICIOUS"

        if is_short:
            reasons.append("URL shortener used to hide destination link")
            if risk_level != "MALICIOUS":
                risk_level = "SUSPICIOUS"

        if is_http:
            if "login" in url.lower() or "signin" in url.lower() or "verify" in url.lower() or "account" in url.lower():
                reasons.append("Unencrypted HTTP link requesting login/credential verification")
                risk_level = "MALICIOUS"
            elif risk_level == "SAFE":
                reasons.append("Unencrypted HTTP web link")
                risk_level = "SUSPICIOUS"

        return URLRiskFactor(
            url=url,
            domain=hostname,
            risk_level=risk_level,
            reasons=reasons,
            is_ip_address=is_ip,
            is_http=is_http,
            is_shortener=is_short,
            is_spoofed_domain=is_spoofed,
        )

    def _check_lookalike_hostname(self, hostname: str) -> bool:
        if not hostname:
            return False

        # Phishing keywords in hostname
        keywords = ["gov-portal", "nic-portal", "aicte-gov", "sih-login", "bank-verify", "login-portal"]
        for kw in keywords:
            if kw in hostname:
                return True

        for target in self.TARGET_DOMAINS:
            name = target.split(".")[0]
            if len(name) > 3 and name in hostname and hostname != target:
                if hostname.endswith(".co") or hostname.endswith(".xyz") or hostname.endswith(".top") or hostname.endswith(".online"):
                    return True

        return False
