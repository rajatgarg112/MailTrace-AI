from enum import Enum


class DeliveryStatusEnum(str, Enum):
    SCANNING = "SCANNING"
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    QUARANTINED = "QUARANTINED"


class VerdictEnum(str, Enum):
    SAFE = "SAFE"
    PHISHING = "PHISHING"
    MALICIOUS = "MALICIOUS"
    SUSPICIOUS = "SUSPICIOUS"
