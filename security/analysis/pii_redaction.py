"""
MailTrace AI — AES-256 PII Redaction & Privacy Engine

Provides automated PII identification and redaction for sensitive documents/emails
(Aadhaar, PAN, SSN, Credit Cards, Phone Numbers) and AES-256-GCM encryption for evidence protection.
"""

from dataclasses import dataclass
import base64
import os
import re
from typing import List, Dict, Tuple, Optional


@dataclass
class PIIRedactionResult:
    original_length: int
    redacted_length: int
    pii_detected_count: int
    pii_types_found: List[str]
    redacted_text: str
    is_pii_present: bool


class PIIRedactor:
    """Automated PII Masking and AES-256 Privacy Engine"""

    # Regex patterns for common sensitive Indian and International PII fields
    PATTERNS = {
        "AADHAAR": re.compile(r"\b[2-9]{1}\d{3}[\s-]?\d{4}[\s-]?\d{4}\b"),
        "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"),
        "CREDIT_CARD": re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"),
        "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "PHONE_INDIA": re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b"),
        "IFSC_CODE": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
    }

    REDACTION_LABELS = {
        "AADHAAR": "[REDACTED-AADHAAR]",
        "PAN": "[REDACTED-PAN]",
        "CREDIT_CARD": "[REDACTED-CARD]",
        "SSN": "[REDACTED-SSN]",
        "PHONE_INDIA": "[REDACTED-PHONE]",
        "IFSC_CODE": "[REDACTED-IFSC]",
    }

    def redact(self, text: str) -> PIIRedactionResult:
        """Detects PII occurrences and replaces them with secure redaction masks."""
        if not text:
            return PIIRedactionResult(
                original_length=0,
                redacted_length=0,
                pii_detected_count=0,
                pii_types_found=[],
                redacted_text="",
                is_pii_present=False,
            )

        redacted_text = text
        pii_types_found = []
        total_count = 0

        for pii_type, regex in self.PATTERNS.items():
            matches = list(regex.finditer(redacted_text))
            if matches:
                pii_types_found.append(pii_type)
                total_count += len(matches)
                mask = self.REDACTION_LABELS[pii_type]
                redacted_text = regex.sub(mask, redacted_text)

        return PIIRedactionResult(
            original_length=len(text),
            redacted_length=len(redacted_text),
            pii_detected_count=total_count,
            pii_types_found=pii_types_found,
            redacted_text=redacted_text,
            is_pii_present=total_count > 0,
        )

    @staticmethod
    def encrypt_aes256_gcm(data: str, secret_key: bytes) -> str:
        """Encrypts string payload with AES-256-GCM or authenticated cryptographic fallback."""
        if len(secret_key) < 32:
            secret_key = secret_key.ljust(32, b"0")[:32]

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            nonce = os.urandom(12)
            aesgcm = AESGCM(secret_key)
            ct = aesgcm.encrypt(nonce, data.encode("utf-8"), None)
            combined = nonce + ct
            return base64.b64encode(combined).decode("utf-8")
        except ImportError:
            # Fallback HMAC-SHA256 authenticated XOR cipher for environments without cryptography lib
            import hashlib
            import hmac
            nonce = os.urandom(16)
            key_hash = hashlib.sha256(secret_key + nonce).digest()
            data_bytes = data.encode("utf-8")
            ct_bytes = bytes([b ^ key_hash[i % len(key_hash)] for i, b in enumerate(data_bytes)])
            mac = hmac.new(secret_key, nonce + ct_bytes, hashlib.sha256).digest()
            combined = nonce + mac + ct_bytes
            return base64.b64encode(combined).decode("utf-8")

    @staticmethod
    def decrypt_aes256_gcm(encrypted_b64: str, secret_key: bytes) -> str:
        """Decrypts AES-256-GCM payload."""
        if len(secret_key) < 32:
            secret_key = secret_key.ljust(32, b"0")[:32]

        raw = base64.b64decode(encrypted_b64)

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            nonce = raw[:12]
            ct = raw[12:]
            aesgcm = AESGCM(secret_key)
            decrypted = aesgcm.decrypt(nonce, ct, None)
            return decrypted.decode("utf-8")
        except ImportError:
            import hashlib
            import hmac
            nonce = raw[:16]
            mac = raw[16:48]
            ct_bytes = raw[48:]
            expected_mac = hmac.new(secret_key, nonce + ct_bytes, hashlib.sha256).digest()
            if not hmac.compare_digest(mac, expected_mac):
                raise ValueError("Cryptographic authentication MAC verification failed")
            key_hash = hashlib.sha256(secret_key + nonce).digest()
            pt_bytes = bytes([b ^ key_hash[i % len(key_hash)] for i, b in enumerate(ct_bytes)])
            return pt_bytes.decode("utf-8")
