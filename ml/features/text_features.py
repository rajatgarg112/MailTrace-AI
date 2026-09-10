"""
Extracts statistical and structural text metrics from processed emails.
"""

from typing import Dict
from .base import BaseFeatureExtractor, FeatureVector
from ..preprocessing.base import ProcessedEmail


class TextFeatureExtractor(BaseFeatureExtractor):
    """
    Computes statistical text properties such as word counts, uppercase ratio,
    punctuation ratios, link density, and length indicators.
    """

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        text = processed_email.combined_text
        subject = processed_email.cleaned_subject
        body = processed_email.cleaned_body

        char_count = len(text)
        word_count = len(processed_email.tokens)
        
        # Uppercase ratio in raw subject/body
        raw_full = f"{processed_email.raw_subject or ''} {processed_email.raw_body or ''}"
        upper_count = sum(1 for c in raw_full if c.isupper())
        uppercase_ratio = (upper_count / len(raw_full)) if raw_full else 0.0

        # Exclamations and question marks count
        exclamation_count = raw_full.count('!')
        question_count = raw_full.count('?')

        # Digit ratio
        digit_count = sum(1 for c in raw_full if c.isdigit())
        digit_ratio = (digit_count / len(raw_full)) if raw_full else 0.0

        num_urls = len(processed_email.extracted_urls)
        url_to_word_ratio = (num_urls / word_count) if word_count > 0 else float(num_urls)

        numerical = {
            "char_count": float(char_count),
            "word_count": float(word_count),
            "subject_length": float(len(subject)),
            "body_length": float(len(body)),
            "uppercase_ratio": round(uppercase_ratio, 4),
            "exclamation_count": float(exclamation_count),
            "question_count": float(question_count),
            "digit_ratio": round(digit_ratio, 4),
            "num_urls": float(num_urls),
            "url_to_word_ratio": round(url_to_word_ratio, 4)
        }

        booleans = {
            "has_urls": num_urls > 0,
            "has_high_uppercase": uppercase_ratio > 0.25,
            "has_excessive_exclamation": exclamation_count >= 3,
            "is_empty_body": len(body.strip()) == 0
        }

        raw_vec = list(numerical.values())

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            feature_names=list(numerical.keys()),
            raw_vector=raw_vec
        )
