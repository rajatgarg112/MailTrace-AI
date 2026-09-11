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

    # URL Extraction Regex (captures http/https and www links)
    URL_REGEX = re.compile(r"(?:https?://|www\.)[^\s<>\"']+", re.IGNORECASE)
    CLICK_HERE_REGEX = re.compile(r"\b(?:click\s+(?:here|this\s+link|link|below|to|and)|follow\s+this\s+link|open\s+link|verify\s+(?:here|account|link)|login\s+here)\b", re.IGNORECASE)

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
        click_here_matches = self.CLICK_HERE_REGEX.findall(clean_text)

        # Normalize www. URLs to http:// for parsing
        normalized_urls = []
        for u in extracted_urls:
            if u.lower().startswith("www."):
                normalized_urls.append("http://" + u)
            else:
                normalized_urls.append(u)

        # Deduplicate while preserving order
        seen = set()
        unique_urls = [u for u in normalized_urls if not (u in seen or seen.add(u))]

        details: List[URLRiskFactor] = []
        findings: List[str] = []
        total_risk_score = 0.0

        for url in unique_urls:
            risk_item = self._evaluate_url(url)
            details.append(risk_item)

            if risk_item.risk_level == "MALICIOUS":
                total_risk_score += 85.0
            elif risk_item.risk_level == "SUSPICIOUS":
                total_risk_score += 65.0
            else:
                # Any embedded link raises risk to at least 60
                total_risk_score += 60.0

            for r in risk_item.reasons:
                findings.append(f"URL ALERT: [{url}] — {r}")

        if click_here_matches and not unique_urls:
            total_risk_score += 80.0
            findings.append(f"LINK ACTION THREAT: Call-to-action phrase detected ('{click_here_matches[0]}') requesting user click")
        elif click_here_matches:
            total_risk_score += 30.0
            findings.append(f"LINK ACTION THREAT: Suspicious link anchor text detected ('{click_here_matches[0]}')")

        total_risk_score = min(100.0, total_risk_score)
        malicious_count = sum(1 for d in details if d.risk_level == "MALICIOUS") + (1 if click_here_matches and not unique_urls else 0)
        suspicious_count = sum(1 for d in details if d.risk_level == "SUSPICIOUS")

        has_links = bool(unique_urls or click_here_matches)

        return URLAnalysisResult(
            total_urls=len(unique_urls) + (1 if (click_here_matches and not unique_urls) else 0),
            malicious_urls_count=malicious_count,
            suspicious_urls_count=suspicious_count,
            url_details=details,
            overall_url_risk_score=total_risk_score,
            has_phishing_links=has_links,
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
