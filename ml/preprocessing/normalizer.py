"""
Modular text normalizer for cleaning HTML, unescaping entities,
normalizing whitespace, and generating token lists.
"""

import html
import re
from typing import List, Optional


class TextNormalizer:
    """
    Handles text cleaning, HTML stripping, entity decoding,
    whitespace normalization, and tokenization.
    """

    HTML_TAG_REGEX = re.compile(r'<[^>]+>')
    WHITESPACE_REGEX = re.compile(r'\s+')
    TOKEN_REGEX = re.compile(r'\b\w+\b')

    def clean_text(self, text: Optional[str]) -> str:
        """
        Strips HTML tags, decodes HTML entities, and collapses excessive whitespace.
        Returns empty string if input is None or empty.
        """
        if not text:
            return ""

        # 1. Strip HTML tags first
        no_html = self.HTML_TAG_REGEX.sub(' ', text)
        # 2. Decode HTML entities (e.g. &amp; -> &, &lt; -> <)
        decoded = html.unescape(no_html)
        # 3. Normalize whitespace and strip leading/trailing spaces
        normalized = self.WHITESPACE_REGEX.sub(' ', decoded).strip()
        return normalized

    def normalize_for_nlp(self, text: str) -> str:
        """
        Converts cleaned text to lowercase for downstream NLP feature processing.
        """
        return text.lower().strip() if text else ""

    def tokenize(self, text: str) -> List[str]:
        """
        Extracts lowercase word tokens from text.
        """
        if not text:
            return []
        return [token.lower() for token in self.TOKEN_REGEX.findall(text)]
