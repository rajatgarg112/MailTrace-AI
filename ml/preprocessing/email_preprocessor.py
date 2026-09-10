"""
Concrete Email Preprocessor implementation.
Parses, cleans, and normalizes email inputs (sender, recipients, subject, body, URLs)
and extracts basic text indicators for ML feature pipelines.
"""

import re
from typing import Any, Dict, List, Union, Optional
from .base import BasePreprocessor, ProcessedEmail
from .normalizer import TextNormalizer
from .indicator_extractor import IndicatorExtractor


class EmailPreprocessor(BasePreprocessor):
    """
    Modular Email Preprocessor.
    Cleans email text, normalizes sender/recipients/URLs,
    handles missing or empty fields safely, and extracts text indicators.
    """

    URL_REGEX = re.compile(
        r'https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?',
        re.IGNORECASE
    )
    EMAIL_REGEX = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )

    def __init__(
        self,
        normalizer: Optional[TextNormalizer] = None,
        indicator_extractor: Optional[IndicatorExtractor] = None
    ):
        self.normalizer = normalizer or TextNormalizer()
        self.indicator_extractor = indicator_extractor or IndicatorExtractor()

    def preprocess(self, input_data: Union[Dict[str, Any], str, Any]) -> ProcessedEmail:
        """
        Main preprocessing entry point.
        Converts flexible email input into a standardized ProcessedEmail object.
        """
        raw_subject, raw_body, sender_raw, recipients_raw, explicit_urls, metadata_dict = self._parse_input(input_data)

        # 1. Clean Subject & Body
        cleaned_subject = self.normalizer.clean_text(raw_subject)
        cleaned_body = self.normalizer.clean_text(raw_body)
        combined_text = f"{cleaned_subject} {cleaned_body}".strip()
        normalized_text = self.normalizer.normalize_for_nlp(combined_text)
        tokens = self.normalizer.tokenize(combined_text)

        # 2. Process Sender & Sender Domain
        sender_email = self._extract_first_email(sender_raw)
        sender_domain = self._extract_domain(sender_email) if sender_email else None

        # 3. Process Recipients & Recipient Domains
        recipients = self._parse_recipients(recipients_raw)
        recipient_domains = list(dict.fromkeys(
            filter(None, [self._extract_domain(r) for r in recipients])
        ))

        # 4. Process URLs (Combine explicit URLs and regex-extracted URLs from cleaned text)
        extracted_urls = self._extract_urls(cleaned_subject, cleaned_body, explicit_urls)

        # 5. Extract Embedded Email Addresses
        extracted_emails = self._extract_embedded_emails(raw_subject, raw_body)

        # 6. Extract Basic Text Indicators
        text_indicators = self.indicator_extractor.extract_indicators(
            raw_subject=raw_subject,
            raw_body=raw_body,
            cleaned_subject=cleaned_subject,
            cleaned_body=cleaned_body,
            sender_email=sender_email,
            recipients=recipients,
            urls=extracted_urls,
            tokens=tokens
        )

        metadata = {
            **metadata_dict,
            "has_html": "<" in (raw_body or "") and ">" in (raw_body or ""),
            "url_count": len(extracted_urls),
            "email_count": len(extracted_emails),
            "recipient_count": len(recipients),
            "token_count": len(tokens)
        }

        return ProcessedEmail(
            raw_subject=raw_subject,
            raw_body=raw_body,
            cleaned_subject=cleaned_subject,
            cleaned_body=cleaned_body,
            combined_text=combined_text,
            normalized_text=normalized_text,
            sender_email=sender_email,
            sender_domain=sender_domain,
            recipients=recipients,
            recipient_domains=recipient_domains,
            extracted_urls=extracted_urls,
            extracted_emails=extracted_emails,
            tokens=tokens,
            text_indicators=text_indicators,
            metadata=metadata
        )

    def _parse_input(self, input_data: Any) -> tuple:
        """Parses flexible inputs into (subject, body, sender, recipients, urls, metadata)."""
        if isinstance(input_data, str):
            return None, input_data, None, [], [], {}

        if isinstance(input_data, dict):
            msg = input_data.get("message", input_data)

            # Subject extraction
            subject = msg.get("subject") or msg.get("raw_subject")

            # Body extraction (try text, html, body, content)
            body = msg.get("body_text") or msg.get("body_html") or msg.get("body") or msg.get("content") or msg.get("text")

            # Sender extraction
            sender = msg.get("from") or msg.get("sender") or msg.get("sender_email")

            # Recipients extraction (to, cc, bcc, recipients)
            recipients_raw = msg.get("to") or msg.get("recipients") or []
            if "cc" in msg and msg["cc"]:
                if isinstance(recipients_raw, list):
                    recipients_raw = recipients_raw + (msg["cc"] if isinstance(msg["cc"], list) else [msg["cc"]])
                elif isinstance(recipients_raw, str):
                    recipients_raw = [recipients_raw, msg["cc"]] if isinstance(msg["cc"], str) else [recipients_raw] + msg["cc"]

            # URLs extraction
            urls = msg.get("urls") or msg.get("extracted_urls") or []

            metadata = input_data.get("metadata", {})
            return subject, body, sender, recipients_raw, urls, metadata

        # Fallback for arbitrary object with attributes
        subject = getattr(input_data, "subject", None)
        body = getattr(input_data, "body", getattr(input_data, "content", str(input_data)))
        sender = getattr(input_data, "sender", getattr(input_data, "from_address", None))
        recipients = getattr(input_data, "recipients", getattr(input_data, "to", []))
        urls = getattr(input_data, "urls", [])

        return subject, body, sender, recipients, urls, {}

    def _parse_recipients(self, recipients_raw: Any) -> List[str]:
        """Normalizes recipients string or list into list of valid email strings."""
        if not recipients_raw:
            return []
        
        raw_list: List[str] = []
        if isinstance(recipients_raw, str):
            # Split comma or semicolon separated recipient strings
            raw_list = re.split(r'[,;]\s*', recipients_raw)
        elif isinstance(recipients_raw, list):
            for item in recipients_raw:
                if isinstance(item, str):
                    raw_list.extend(re.split(r'[,;]\s*', item))

        result = []
        for item in raw_list:
            match = self.EMAIL_REGEX.search(item)
            if match:
                result.append(match.group(0).lower())
            elif "@" in item:
                result.append(item.strip().lower())
        return list(dict.fromkeys(result))

    def _extract_first_email(self, sender_raw: Optional[str]) -> Optional[str]:
        """Extracts primary email address from sender string."""
        if not sender_raw:
            return None
        match = self.EMAIL_REGEX.search(str(sender_raw))
        if match:
            return match.group(0).lower()
        if "@" in str(sender_raw):
            return str(sender_raw).strip().lower()
        return None

    def _extract_domain(self, email_address: Optional[str]) -> Optional[str]:
        """Extracts domain part from email address."""
        if not email_address or "@" not in email_address:
            return None
        parts = email_address.split("@")
        if len(parts) >= 2:
            return parts[-1].lower()
        return None

    def _extract_urls(self, raw_subject: Optional[str], raw_body: Optional[str], explicit_urls: Any) -> List[str]:
        """Combines explicitly provided URLs and regex-extracted URLs."""
        urls: List[str] = []

        if isinstance(explicit_urls, list):
            urls.extend([str(u) for u in explicit_urls if u])
        elif isinstance(explicit_urls, str) and explicit_urls:
            urls.append(explicit_urls)

        if raw_subject:
            urls.extend(self.URL_REGEX.findall(raw_subject))
        if raw_body:
            urls.extend(self.URL_REGEX.findall(raw_body))

        return list(dict.fromkeys(urls))

    def _extract_embedded_emails(self, raw_subject: Optional[str], raw_body: Optional[str]) -> List[str]:
        """Extracts email addresses mentioned in subject and body."""
        found: List[str] = []
        if raw_subject:
            found.extend(self.EMAIL_REGEX.findall(raw_subject))
        if raw_body:
            found.extend(self.EMAIL_REGEX.findall(raw_body))
        return list(dict.fromkeys([e.lower() for e in found]))
