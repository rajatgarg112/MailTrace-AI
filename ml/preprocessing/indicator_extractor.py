"""
Extracts basic text indicators and structural metadata from emails.
"""

from typing import Dict, Any, List, Optional


class IndicatorExtractor:
    """
    Computes text indicators, quality metrics, and missing field flags.
    """

    def extract_indicators(
        self,
        raw_subject: Optional[str],
        raw_body: Optional[str],
        cleaned_subject: str,
        cleaned_body: str,
        sender_email: Optional[str],
        recipients: List[str],
        urls: List[str],
        tokens: List[str]
    ) -> Dict[str, Any]:
        """
        Extracts structural flags and basic text statistical indicators.
        """
        raw_combined = f"{raw_subject or ''} {raw_body or ''}"
        total_chars = len(raw_combined)

        uppercase_count = sum(1 for c in raw_combined if c.isupper())
        digit_count = sum(1 for c in raw_combined if c.isdigit())
        exclamation_count = raw_combined.count('!')
        question_count = raw_combined.count('?')
        special_char_count = sum(1 for c in raw_combined if not c.isalnum() and not c.isspace())

        uppercase_ratio = round(uppercase_count / total_chars, 4) if total_chars > 0 else 0.0
        digit_ratio = round(digit_count / total_chars, 4) if total_chars > 0 else 0.0
        special_char_ratio = round(special_char_count / total_chars, 4) if total_chars > 0 else 0.0

        is_missing_subject = not bool(cleaned_subject)
        is_empty_body = not bool(cleaned_body)
        is_missing_sender = not bool(sender_email)
        has_urls = len(urls) > 0
        has_recipients = len(recipients) > 0

        return {
            "has_subject": not is_missing_subject,
            "is_missing_subject": is_missing_subject,
            "has_body": not is_empty_body,
            "is_empty_body": is_empty_body,
            "has_sender": not is_missing_sender,
            "is_missing_sender": is_missing_sender,
            "has_urls": has_urls,
            "num_urls": len(urls),
            "has_recipients": has_recipients,
            "num_recipients": len(recipients),
            "subject_char_length": len(cleaned_subject),
            "body_char_length": len(cleaned_body),
            "token_count": len(tokens),
            "uppercase_count": uppercase_count,
            "uppercase_ratio": uppercase_ratio,
            "digit_count": digit_count,
            "digit_ratio": digit_ratio,
            "special_char_count": special_char_count,
            "special_char_ratio": special_char_ratio,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
        }
