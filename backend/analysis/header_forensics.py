"""
MailTrace AI — RFC Header Forensics & Relay Audit Module

Analyzes email headers for received-chain hop sequences, originating IP extraction,
chronological timestamp drift, lookalike domain spoofing, Return-Path mismatches,
and header forgery indicators.
"""

from dataclasses import dataclass, field
from datetime import datetime
from email.message import Message
from email.parser import Parser
from email.utils import parsedate_to_datetime, parseaddr
import ipaddress
import re
from typing import List, Dict, Optional, Tuple


@dataclass
class RelayHop:
    hop_number: int
    from_host: Optional[str]
    by_host: Optional[str]
    ip_address: Optional[str]
    is_private_ip: bool
    timestamp_raw: Optional[str]
    timestamp_dt: Optional[datetime]
    protocol: Optional[str]


@dataclass
class HeaderAnalysisResult:
    originating_ip: Optional[str]
    relay_chain: List[RelayHop]
    total_hops: int
    from_address: str
    from_domain: str
    return_path: Optional[str]
    return_path_domain: Optional[str]
    reply_to: Optional[str]
    message_id: Optional[str]
    subject: str
    anomalies: List[str]
    anomaly_score: float  # 0.0 (Clean) to 100.0 (High Threat)
    is_spoofed_domain: bool
    domain_mismatch: bool
    timestamp_drift_detected: bool
    missing_critical_headers: List[str]


class HeaderForensics:
    """RFC Header Forensics Engine"""

    # Common lookalike / homoglyph / typosquatting keywords for institutional domains
    HIGH_RISK_TARGET_DOMAINS = [
        "aicte-india.org",
        "gov.in",
        "nic.in",
        "ac.in",
        "sih.gov.in",
        "paypal.com",
        "microsoft.com",
        "google.com",
    ]

    IP_REGEX = re.compile(r"\[?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]?")
    IPV6_REGEX = re.compile(r"\[?IPv6:([0-9a-fA-F:]+)\]?")

    def __init__(self, high_risk_domains: Optional[List[str]] = None):
        if high_risk_domains:
            self.target_domains = [d.lower() for d in high_risk_domains]
        else:
            self.target_domains = [d.lower() for d in self.HIGH_RISK_TARGET_DOMAINS]

    def analyze(self, raw_email_or_msg: str | bytes | Message) -> HeaderAnalysisResult:
        """Parses email headers and performs deep forensic analysis."""
        if isinstance(raw_email_or_msg, Message):
            msg = raw_email_or_msg
        elif isinstance(raw_email_or_msg, bytes):
            msg = Parser().parsestr(raw_email_or_msg.decode("utf-8", errors="replace"))
        else:
            msg = Parser().parsestr(str(raw_email_or_msg))

        # Extract basic header fields
        from_raw = msg.get("From", "")
        _, from_addr = parseaddr(from_raw)
        from_domain = from_addr.split("@")[-1].lower() if "@" in from_addr else ""

        return_path_raw = msg.get("Return-Path", "")
        _, return_path_addr = parseaddr(return_path_raw)
        return_path_domain = return_path_addr.split("@")[-1].lower() if "@" in return_path_addr else None

        reply_to_raw = msg.get("Reply-To", "")
        _, reply_to_addr = parseaddr(reply_to_raw)

        message_id = msg.get("Message-ID", None)
        subject = msg.get("Subject", "(No Subject)")

        # Extract Received headers chain
        received_headers = msg.get_all("Received", [])
        relay_chain = self._parse_received_chain(received_headers)

        # Extract Originating Node IP (earliest external IP in relay chain)
        originating_ip = self._extract_originating_ip(relay_chain)

        # Perform forensic anomaly checks
        anomalies: List[str] = []
        missing_critical: List[str] = []
        anomaly_score = 0.0

        # Check 1: Missing critical headers
        if not msg.get("From"):
            missing_critical.append("From")
            anomalies.append("CRITICAL: Missing 'From' header")
            anomaly_score += 30.0
        if not msg.get("Date"):
            missing_critical.append("Date")
            anomalies.append("WARNING: Missing 'Date' header")
            anomaly_score += 10.0
        if not message_id:
            missing_critical.append("Message-ID")
            anomalies.append("WARNING: Missing 'Message-ID' header")
            anomaly_score += 15.0
        elif not (message_id.startswith("<") and message_id.endswith(">") and "@" in message_id):
            anomalies.append(f"SUSPICIOUS: Malformed Message-ID format '{message_id}'")
            anomaly_score += 15.0

        # Check 2: Domain Mismatch (From vs Return-Path)
        domain_mismatch = False
        if return_path_domain and from_domain and return_path_domain != from_domain:
            domain_mismatch = True
            anomalies.append(
                f"SPOOFING ALERT: Header From domain ({from_domain}) does not match Return-Path domain ({return_path_domain})"
            )
            anomaly_score += 25.0

        # Check 3: Reply-To Mismatch
        if reply_to_addr and from_addr and reply_to_addr.lower() != from_addr.lower():
            anomalies.append(
                f"SUSPICIOUS: Reply-To address ({reply_to_addr}) differs from sender address ({from_addr})"
            )
            anomaly_score += 15.0

        # Check 4: Lookalike Domain Spoofing Detection
        is_spoofed_domain = self._check_lookalike_domain(from_domain)
        if is_spoofed_domain:
            anomalies.append(
                f"CRITICAL THREAT: From domain '{from_domain}' appears to be a spoofed lookalike domain targeting legitimate institutional domains"
            )
            anomaly_score += 40.0

        # Check 5: Timestamp Chronological Drift in Relay Chain
        timestamp_drift_detected = self._check_timestamp_drift(relay_chain)
        if timestamp_drift_detected:
            anomalies.append("SUSPICIOUS: Chronological timestamp drift/reversal detected in Received relay chain")
            anomaly_score += 20.0

        # Check 6: Hop Count Anomalies
        if len(relay_chain) > 10:
            anomalies.append(f"SUSPICIOUS: Excessive relay hop count ({len(relay_chain)} hops)")
            anomaly_score += 10.0
        elif len(relay_chain) == 0:
            anomalies.append("WARNING: No Received headers found in message")
            anomaly_score += 15.0

        # Cap anomaly score at 100.0
        anomaly_score = min(100.0, anomaly_score)

        return HeaderAnalysisResult(
            originating_ip=originating_ip,
            relay_chain=relay_chain,
            total_hops=len(relay_chain),
            from_address=from_addr,
            from_domain=from_domain,
            return_path=return_path_addr if return_path_addr else None,
            return_path_domain=return_path_domain,
            reply_to=reply_to_addr if reply_to_addr else None,
            message_id=message_id,
            subject=subject,
            anomalies=anomalies,
            anomaly_score=anomaly_score,
            is_spoofed_domain=is_spoofed_domain,
            domain_mismatch=domain_mismatch,
            timestamp_drift_detected=timestamp_drift_detected,
            missing_critical_headers=missing_critical,
        )

    def _parse_received_chain(self, received_list: List[str]) -> List[RelayHop]:
        """Parses Received headers from newest (top) to oldest (bottom)."""
        relay_chain: List[RelayHop] = []

        # Received headers in email are listed newest first (top down)
        # We assign hop number starting from earliest hop (bottom = hop 1)
        reversed_headers = list(reversed(received_list))

        for idx, header in enumerate(reversed_headers, start=1):
            from_host = None
            by_host = None
            ip_str = None
            timestamp_str = None
            timestamp_dt = None
            protocol = None

            # Parse 'from' clause
            from_match = re.search(r"from\s+([^\s;]+)", header, re.IGNORECASE)
            if from_match:
                from_host = from_match.group(1).strip()

            # Parse 'by' clause
            by_match = re.search(r"by\s+([^\s;]+)", header, re.IGNORECASE)
            if by_match:
                by_host = by_match.group(1).strip()

            # Parse IP address
            ip_match = self.IP_REGEX.search(header)
            if ip_match:
                candidate_ip = ip_match.group(1)
                if candidate_ip not in ("127.0.0.1", "0.0.0.0"):
                    ip_str = candidate_ip

            # Parse Protocol
            proto_match = re.search(r"with\s+([A-Za-z0-9]+)", header, re.IGNORECASE)
            if proto_match:
                protocol = proto_match.group(1)

            # Parse Timestamp (after semicolon ';')
            if ";" in header:
                timestamp_str = header.split(";")[-1].strip()
                try:
                    timestamp_dt = parsedate_to_datetime(timestamp_str)
                except Exception:
                    timestamp_dt = None

            is_private = False
            if ip_str:
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    is_private = ip_obj.is_private and not (
                        ip_str.startswith("198.51.") or ip_str.startswith("203.0.") or ip_str.startswith("192.0.2.")
                    )
                except ValueError:
                    is_private = False

            relay_chain.append(
                RelayHop(
                    hop_number=idx,
                    from_host=from_host,
                    by_host=by_host,
                    ip_address=ip_str,
                    is_private_ip=is_private,
                    timestamp_raw=timestamp_str,
                    timestamp_dt=timestamp_dt,
                    protocol=protocol,
                )
            )

        return relay_chain

    def _extract_originating_ip(self, relay_chain: List[RelayHop]) -> Optional[str]:
        """Finds the earliest public IP address in the relay chain, falling back to earliest hop IP."""
        for hop in relay_chain:
            if hop.ip_address and not hop.is_private_ip:
                return hop.ip_address
        if relay_chain and relay_chain[0].ip_address:
            return relay_chain[0].ip_address
        return None

    def _check_lookalike_domain(self, domain: str) -> bool:
        """Detects typosquatting / lookalike domain tricks (e.g. aicte-gov-portal.co)."""
        if not domain:
            return False

        domain_lower = domain.lower()

        # Direct lookalike patterns
        suspicious_keywords = ["aicte-gov", "aicte-portal", "sih-portal", "nic-gov", "gov-portal"]
        for kw in suspicious_keywords:
            if kw in domain_lower:
                return True

        # Check for fake TLD extensions combined with official names
        for target in self.target_domains:
            name = target.split(".")[0]
            if len(name) > 3 and name in domain_lower and domain_lower != target:
                if domain_lower.endswith(".co") or domain_lower.endswith(".xyz") or domain_lower.endswith(".top"):
                    return True

        return False

    def _check_timestamp_drift(self, relay_chain: List[RelayHop]) -> bool:
        """Detects if timestamps move backwards chronologically along the relay path."""
        valid_timestamps = [hop.timestamp_dt for hop in relay_chain if hop.timestamp_dt is not None]
        if len(valid_timestamps) < 2:
            return False

        for i in range(len(valid_timestamps) - 1):
            if valid_timestamps[i] > valid_timestamps[i + 1]:
                # Earliest hop timestamp is newer than downstream hop timestamp (drift)
                return True

        return False
