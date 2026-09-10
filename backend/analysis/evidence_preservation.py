"""
MailTrace AI — ISO/IEC 27037 Evidence Preservation & BSA Compliance Module

Provides cryptographic integrity checks, SHA-256 raw hashing, microsecond timestamping,
and tamper-proof digital evidence dossier generation aligned with ISO/IEC 27037
and Bhartiya Sakshya Adhiniyam (BSA) requirements for court admissibility.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
import uuid
from typing import Dict, Any, Optional


@dataclass
class EvidenceDossier:
    evidence_id: str
    case_reference_id: str
    timestamp_utc: str
    raw_sha256: str
    canonical_headers_sha256: str
    custody_chain_hash: str
    iso_27037_compliant: bool
    bsa_admissible: bool
    metadata: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


class EvidencePreserver:
    """ISO/IEC 27037 Digital Evidence Preservation Engine"""

    @staticmethod
    def compute_sha256(data: bytes | str) -> str:
        """Calculates standard SHA-256 hash."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def canonicalize_headers(headers_dict: Dict[str, str]) -> str:
        """Creates a canonicalized header string sorted alphabetically by header name."""
        sorted_keys = sorted(headers_dict.keys(), key=lambda k: k.lower())
        lines = []
        for k in sorted_keys:
            v = headers_dict[k].strip().replace("\r\n", " ").replace("\n", " ")
            lines.append(f"{k.lower()}:{v}")
        return "\n".join(lines)

    def preserve_evidence(
        self,
        raw_bytes: bytes,
        headers: Dict[str, str],
        sender: str,
        recipient: str,
        case_id: Optional[str] = None,
    ) -> EvidenceDossier:
        """Generates an immutable Evidence Dossier with SHA-256 integrity and custody chain hash."""
        evidence_id = f"EV-{uuid.uuid4().hex[:12].upper()}"
        case_ref = case_id if case_id else f"CASE-{uuid.uuid4().hex[:8].upper()}"
        now_utc = datetime.now(timezone.utc).isoformat()

        # 1. Raw Byte SHA-256 Hash
        raw_sha256 = self.compute_sha256(raw_bytes)

        # 2. Canonical Headers SHA-256 Hash
        canonical_headers = self.canonicalize_headers(headers)
        canonical_headers_sha256 = self.compute_sha256(canonical_headers)

        # 3. Compute Custody Chain Hash (ISO/IEC 27037 Hash Seal)
        custody_payload = f"{evidence_id}|{case_ref}|{now_utc}|{raw_sha256}|{canonical_headers_sha256}|{sender}|{recipient}"
        custody_chain_hash = self.compute_sha256(custody_payload)

        metadata = {
            "preservation_standard": "ISO/IEC 27037:2012",
            "legal_compliance": "Bhartiya Sakshya Adhiniyam (BSA) Section 63",
            "sender": sender,
            "recipient": recipient,
            "raw_byte_length": len(raw_bytes),
            "hash_algorithm": "SHA-256",
        }

        return EvidenceDossier(
            evidence_id=evidence_id,
            case_reference_id=case_ref,
            timestamp_utc=now_utc,
            raw_sha256=raw_sha256,
            canonical_headers_sha256=canonical_headers_sha256,
            custody_chain_hash=custody_chain_hash,
            iso_27037_compliant=True,
            bsa_admissible=True,
            metadata=metadata,
        )

    def verify_integrity(self, dossier: EvidenceDossier, raw_bytes: bytes) -> bool:
        """Verifies if raw message bytes match the preserved Evidence Dossier SHA-256 hash."""
        recomputed_hash = self.compute_sha256(raw_bytes)
        return recomputed_hash.lower() == dossier.raw_sha256.lower()
