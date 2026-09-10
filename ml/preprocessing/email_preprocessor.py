"""
Concrete Email Preprocessor implementation for cleaning and normalizing email data.
"""

import re
from typing import Any, Dict, List, Union, Optional
from .base import BasePreprocessor, ProcessedEmail


class EmailPreprocessor(BasePreprocessor):
    """
    Cleans raw email HTML/text, extracts embedded indicators (URLs, emails),
    and produces normalized text for feature extraction.
    """

    URL_REGEX = re.compile(
        r'https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?',
        re.IGNORECASE
    )
    EMAIL_REGEX = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )
    HTML_TAG_REGEX = re.compile(r'<[^>]+>')
    EXTRA_WHITESPACE_REGEX = re.compile(r'\s+')

    def preprocess(self, input_data: Union[Dict[str, Any], str]) -> ProcessedEmail:
        """
        Processes dictionary or raw string email into ProcessedEmail.
        """
        if isinstance(input_data, str):
            raw_subject = ""
            raw_body = input_data
            sender_email = None
            sender_domain = None
            headers = {}
        elif isinstance(input_data, dict):
            # Support both nested {"message": {...}} and flat dictionaries
            msg = input_data.get("message", input_data)
            raw_subject = msg.get("subject") or ""
            raw_body = msg.get("body_text") or msg.get("body_html") or msg.get("body") or ""
            sender_email = msg.get("from") or msg.get("sender")
            sender_domain = self._extract_domain(sender_email) if sender_email else None
            headers = input_data.get("headers", {})
        else:
            raw_subject = ""
            raw_body = str(input_data)
            sender_email = None
            sender_domain = None
            headers = {}

        cleaned_subject = self._clean_text(raw_subject)
        cleaned_body = self._clean_text(raw_body)
        
        extracted_urls = self.URL_REGEX.findall(raw_body) + self.URL_REGEX.findall(raw_subject)
        extracted_emails = self.EMAIL_REGEX.findall(raw_body) + self.EMAIL_REGEX.findall(raw_subject)
        
        # Deduplicate while preserving order
        extracted_urls = list(dict.fromkeys(extracted_urls))
        extracted_emails = list(dict.fromkeys(extracted_emails))

        combined_text = f"{cleaned_subject} {cleaned_body}".strip()
        tokens = [token.lower() for token in re.findall(r'\b\w+\b', combined_text)]

        return ProcessedEmail(
            raw_subject=raw_subject,
            raw_body=raw_body,
            cleaned_subject=cleaned_subject,
            cleaned_body=cleaned_body,
            combined_text=combined_text,
            sender_email=sender_email,
            sender_domain=sender_domain,
            extracted_urls=extracted_urls,
            extracted_emails=extracted_emails,
            tokens=tokens,
            metadata={
                "has_html": "<" in raw_body and ">" in raw_body,
                "url_count": len(extracted_urls),
                "email_count": len(extracted_emails),
                "token_count": len(tokens),
                "headers_present": bool(headers)
            }
        )

    def _clean_text(self, text: str) -> str:
        """Strips HTML tags and normalizes whitespace."""
        if not text:
            return ""
        # Strip HTML tags
        no_html = self.HTML_TAG_REGEX.sub(' ', text)
        # Normalize whitespace
        normalized = self.EXTRA_WHITESPACE_REGEX.sub(' ', no_html)
        return normalized.strip()

    def _extract_domain(self, email_str: str) -> Optional[str]:
        """Extracts domain name from email address string."""
        if not email_str:
            return None
        match = self.EMAIL_REGEX.search(email_str)
        if match:
            full_email = match.group(0)
            parts = full_email.split('@')
            if len(parts) == 2:
                return parts[1].lower()
        return None
