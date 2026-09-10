"""
MailTrace AI — Pre-Delivery Attachment Security Inspection Module

Inspects incoming email attachments for high-risk executable extensions, double extensions
(e.g., invoice.pdf.exe), script payloads, macro-enabled documents (.docm, .xlsm), and
MIME content-type mismatches.
"""

from dataclasses import dataclass, field
import os
from typing import List, Dict, Optional


@dataclass
class AttachmentRiskFactor:
    filename: str
    extension: str
    mime_type: Optional[str]
    size_bytes: int
    risk_level: str  # SAFE | SUSPICIOUS | MALICIOUS
    reasons: List[str]
    is_executable: bool
    is_double_extension: bool
    is_macro_enabled: bool


@dataclass
class AttachmentAnalysisResult:
    total_attachments: int
    malicious_attachments_count: int
    attachment_details: List[AttachmentRiskFactor]
    overall_attachment_risk_score: float  # 0.0 (Clean) to 100.0 (High Threat)
    has_dangerous_attachments: bool
    findings_summary: List[str]


class AttachmentAnalyzer:
    """Pre-Delivery Email Attachment Security Engine"""

    DANGEROUS_EXTENSIONS = {
        ".exe", ".scr", ".vbs", ".bat", ".ps1", ".cmd", ".msi", ".jar",
        ".pif", ".application", ".gadget", ".hta", ".cpl", ".msc"
    }

    MACRO_EXTENSIONS = {".docm", ".xlsm", ".pptm", ".dotm", ".xltm"}

    def analyze(self, attachments: List[Dict[str, str]]) -> AttachmentAnalysisResult:
        """Inspects attachment list for dangerous extensions and double extension tricks."""
        if not attachments:
            return AttachmentAnalysisResult(
                total_attachments=0,
                malicious_attachments_count=0,
                attachment_details=[],
                overall_attachment_risk_score=0.0,
                has_dangerous_attachments=False,
                findings_summary=["No email attachments present."],
            )

        details: List[AttachmentRiskFactor] = []
        findings: List[str] = []
        total_risk_score = 0.0

        for att in attachments:
            filename = att.get("filename", "")
            mime = att.get("mime_type", None)
            size = int(att.get("size_bytes", 0))

            risk_item = self._evaluate_attachment(filename, mime, size)
            details.append(risk_item)

            if risk_item.risk_level == "MALICIOUS":
                total_risk_score += 50.0
            elif risk_item.risk_level == "SUSPICIOUS":
                total_risk_score += 25.0

            for r in risk_item.reasons:
                findings.append(f"ATTACHMENT ALERT: [{filename}] — {r}")

        total_risk_score = min(100.0, total_risk_score)
        malicious_count = sum(1 for d in details if d.risk_level == "MALICIOUS")

        return AttachmentAnalysisResult(
            total_attachments=len(attachments),
            malicious_attachments_count=malicious_count,
            attachment_details=details,
            overall_attachment_risk_score=total_risk_score,
            has_dangerous_attachments=(malicious_count > 0),
            findings_summary=findings if findings else ["All attachments verified clean."],
        )

    def _evaluate_attachment(
        self, filename: str, mime_type: Optional[str], size_bytes: int
    ) -> AttachmentRiskFactor:
        reasons: List[str] = []
        filename_lower = filename.lower().strip()
        parts = filename_lower.split(".")

        ext = f".{parts[-1]}" if len(parts) > 1 else ""

        is_exe = ext in self.DANGEROUS_EXTENSIONS
        is_double_ext = len(parts) > 2 and f".{parts[-1]}" in self.DANGEROUS_EXTENSIONS
        is_macro = ext in self.MACRO_EXTENSIONS

        risk_level = "SAFE"

        if is_double_ext:
            reasons.append(f"Double extension spoofing detected ('{filename}')")
            risk_level = "MALICIOUS"

        if is_exe:
            reasons.append(f"High-risk executable script extension ('{ext}')")
            risk_level = "MALICIOUS"

        if is_macro:
            reasons.append(f"Macro-enabled Office document payload ('{ext}')")
            if risk_level != "MALICIOUS":
                risk_level = "SUSPICIOUS"

        if mime_type and "application/x-dsexec" in mime_type or "application/octet-stream" in mime_type:
            if not is_exe and risk_level == "SAFE":
                reasons.append("Generic binary payload type without safe extension")
                risk_level = "SUSPICIOUS"

        return AttachmentRiskFactor(
            filename=filename,
            extension=ext,
            mime_type=mime_type,
            size_bytes=size_bytes,
            risk_level=risk_level,
            reasons=reasons,
            is_executable=is_exe,
            is_double_extension=is_double_ext,
            is_macro_enabled=is_macro,
        )
