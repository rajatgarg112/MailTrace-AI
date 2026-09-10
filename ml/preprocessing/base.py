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
    sender_email: Optional[str] = None
    sender_domain: Optional[str] = None
    extracted_urls: List[str] = field(default_factory=list)
    extracted_emails: List[str] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePreprocessor(ABC):
    """Abstract interface for all preprocessors in MailTrace ML."""

    @abstractmethod
    def preprocess(self, input_data: Any) -> ProcessedEmail:
        """
        Process raw input into a standardized ProcessedEmail structure.
        
        Args:
            input_data: Dict or string representing the raw email payload.
            
        Returns:
            ProcessedEmail dataclass object.
        """
        pass
