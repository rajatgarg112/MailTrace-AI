"""
Feature extractor for body text characteristics.
"""

from typing import Dict, Any, List
from .base import BaseFeatureExtractor, FeatureVector
from ..preprocessing.base import ProcessedEmail


class BodyFeatureExtractor(BaseFeatureExtractor):
    """
    Extracts statistical and structural text characteristics from email body.
    """

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        body = processed_email.cleaned_body or ""
        raw_body = processed_email.raw_body or ""

        char_len = len(body)
        word_count = len(processed_email.tokens)
        line_count = len(raw_body.splitlines()) if raw_body else 0

        upper_count = sum(1 for c in raw_body if c.isupper())
        upper_ratio = round(upper_count / len(raw_body), 4) if raw_body else 0.0

        digit_count = sum(1 for c in raw_body if c.isdigit())
        digit_ratio = round(digit_count / len(raw_body), 4) if raw_body else 0.0

        special_count = sum(1 for c in raw_body if not c.isalnum() and not c.isspace())
        special_ratio = round(special_count / len(raw_body), 4) if raw_body else 0.0

        exclamations = raw_body.count('!')
        questions = raw_body.count('?')

        is_empty = processed_email.text_indicators.get("is_empty_body", not bool(body.strip()))

        numerical = {
            "body_char_length": float(char_len),
            "body_word_count": float(word_count),
            "body_line_count": float(line_count),
            "body_uppercase_ratio": upper_ratio,
            "body_digit_ratio": digit_ratio,
            "body_special_char_ratio": special_ratio,
            "body_exclamation_count": float(exclamations),
            "body_question_count": float(questions)
        }

        booleans = {
            "is_empty_body": is_empty,
            "has_body": not is_empty,
            "has_body_high_uppercase": upper_ratio > 0.25,
            "has_excessive_exclamation": exclamations >= 3
        }

        feature_names = list(numerical.keys()) + list(booleans.keys())
        raw_vec = list(numerical.values()) + [1.0 if v else 0.0 for v in booleans.values()]

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            feature_names=feature_names,
            raw_vector=raw_vec
        )
