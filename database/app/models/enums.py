from enum import Enum
from typing import List


class EmailStatus(str, Enum):
    """
    Canonical Enum representing all 9 supported email lifecycle states.
    """
    RECEIVED = "RECEIVED"
    SCANNING = "SCANNING"
    DECISION = "DECISION"
    DELIVERED = "DELIVERED"
    WARNING = "WARNING"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def list_values(cls) -> List[str]:
        """Returns a list of string values for all email statuses."""
        return [status.value for status in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Checks whether a given string value is a valid EmailStatus."""
        return value in cls._value2member_map_


class Verdict(str, Enum):
    """
    Canonical Enum representing risk assessment verdicts.
    """
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def list_values(cls) -> List[str]:
        """Returns a list of string values for all verdicts."""
        return [verdict.value for verdict in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Checks whether a given string value is a valid Verdict."""
        return value in cls._value2member_map_


DEFAULT_EMAIL_STATUS = EmailStatus.RECEIVED
