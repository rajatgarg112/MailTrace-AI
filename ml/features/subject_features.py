"""
Feature extractor for subject line text characteristics.
"""

from typing import Dict, Any, List
from .base import BaseFeatureExtractor, FeatureVector
from ..preprocessing.base import ProcessedEmail


class SubjectFeatureExtractor(BaseFeatureExtractor):
    """
    Extracts statistical, structural, and indicator features from subject lines.
    """

    URGENT_SUBJECT_KEYWORDS = {
        "urgent", "alert", "action required", "immediately", "important",
        "verify", "warning", "attention", "suspended", "notice", "critical"
    }

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        subject = processed_email.cleaned_subject or ""
        raw_subject = processed_email.raw_subject or ""

        char_len = len(subject)
        tokens = [t.lower() for t in subject.split()]
        word_count = len(tokens)

        upper_count = sum(1 for c in raw_subject if c.isupper())
        upper_ratio = round(upper_count / len(raw_subject), 4) if raw_subject else 0.0

        digit_count = sum(1 for c in raw_subject if c.isdigit())
        digit_ratio = round(digit_count / len(raw_subject), 4) if raw_subject else 0.0

        exclamations = raw_subject.count('!')
        questions = raw_subject.count('?')

        is_missing = processed_email.text_indicators.get("is_missing_subject", not bool(subject))
        has_urgency = any(kw in subject.lower() for kw in self.URGENT_SUBJECT_KEYWORDS)

        numerical = {
            "subject_char_length": float(char_len),
            "subject_word_count": float(word_count),
            "subject_uppercase_ratio": upper_ratio,
            "subject_digit_ratio": digit_ratio,
            "subject_exclamation_count": float(exclamations),
            "subject_question_count": float(questions)
        }

        booleans = {
            "is_missing_subject": is_missing,
            "has_subject": not is_missing,
            "has_subject_urgency_keyword": has_urgency,
            "has_subject_high_uppercase": upper_ratio > 0.3
        }

        feature_names = list(numerical.keys()) + list(booleans.keys())
        raw_vec = list(numerical.values()) + [1.0 if v else 0.0 for v in booleans.values()]

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            feature_names=feature_names,
            raw_vector=raw_vec
        )
