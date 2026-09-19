from enum import Enum


class DeliveryStatusEnum(str, Enum):
    SCANNING = "SCANNING"
    DELIVERED = "DELIVERED"
    WARNING = "WARNING"
    SUSPICIOUS = "SUSPICIOUS"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class VerdictEnum(str, Enum):
    SAFE = "SAFE"
    PHISHING = "PHISHING"
    MALICIOUS = "MALICIOUS"
    SUSPICIOUS = "SUSPICIOUS"
