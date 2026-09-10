"""
Base preprocessor abstract interface and data structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ProcessedEmail:
    """Standardized processed email data structure for ML pipelines."""
    raw_subject: Optional[str] = None
    raw_body: Optional[str] = None
    cleaned_subject: str = ""
    cleaned_body: str = ""
    combined_text: str = ""
    normalized_text: str = ""
    sender_email: Optional[str] = None
    sender_domain: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    recipient_domains: List[str] = field(default_factory=list)
    extracted_urls: List[str] = field(default_factory=list)
    extracted_emails: List[str] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)
    text_indicators: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePreprocessor(ABC):
    """Abstract interface for all preprocessors in MailTrace ML."""

    @abstractmethod
    def preprocess(self, input_data: Any) -> ProcessedEmail:
        """
        Process raw input into a standardized ProcessedEmail structure.
        
        Args:
            input_data: Dict, string, or email object representing the raw payload.
            
        Returns:
            ProcessedEmail dataclass object.
        """
        pass
