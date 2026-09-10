"""
Composite Email Feature Extractor uniting all specialized feature extractors.
"""

from typing import List, Optional
from .base import BaseFeatureExtractor, FeatureVector
from .subject_features import SubjectFeatureExtractor
from .body_features import BodyFeatureExtractor
from .url_features import UrlFeatureExtractor
from .sender_features import SenderFeatureExtractor
from .structure_features import StructureFeatureExtractor
from .keyword_features import KeywordFeatureExtractor
from ..preprocessing.base import ProcessedEmail


class EmailFeatureExtractor(BaseFeatureExtractor):
    """
    Master Composite Feature Extractor.
    Aggregates features across all 6 core categories:
    1. Subject text characteristics
    2. Body text characteristics
    3. URL-related indicators
    4. Sender-related indicators
    5. Suspicious-language indicators
    6. Message structure indicators
    """

    def __init__(self, extractors: Optional[List[BaseFeatureExtractor]] = None):
        self.extractors = extractors or [
            SubjectFeatureExtractor(),
            BodyFeatureExtractor(),
            UrlFeatureExtractor(),
            SenderFeatureExtractor(),
            StructureFeatureExtractor(),
            KeywordFeatureExtractor()
        ]

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        merged_numerics = {}
        merged_categoricals = {}
        merged_booleans = {}
        merged_signals = {}
        merged_names = []
        raw_values = []

        for extractor in self.extractors:
            vec = extractor.extract(processed_email)
            merged_numerics.update(vec.numerical_features)
            merged_categoricals.update(vec.categorical_features)
            merged_booleans.update(vec.boolean_features)
            merged_signals.update(vec.signal_counts)
            merged_names.extend(vec.feature_names)
            raw_values.extend(vec.raw_vector)

        # Deduplicate feature names while preserving order
        merged_names = list(dict.fromkeys(merged_names))

        return FeatureVector(
            numerical_features=merged_numerics,
            categorical_features=merged_categoricals,
            boolean_features=merged_booleans,
            signal_counts=merged_signals,
            feature_names=merged_names,
            raw_vector=raw_values
        )
