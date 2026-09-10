import unittest
import json
from ml.preprocessing.email_preprocessor import EmailPreprocessor
from ml.features.subject_features import SubjectFeatureExtractor
from ml.features.body_features import BodyFeatureExtractor
from ml.features.url_features import UrlFeatureExtractor
from ml.features.sender_features import SenderFeatureExtractor
from ml.features.structure_features import StructureFeatureExtractor
from ml.features.keyword_features import KeywordFeatureExtractor
from ml.features.composite_extractor import EmailFeatureExtractor
from ml.features.base import FeatureVector


class TestFeatureExtractors(unittest.TestCase):

    def setUp(self):
        self.preprocessor = EmailPreprocessor()
        self.composite_extractor = EmailFeatureExtractor()

    def test_normal_email_feature_extraction(self):
        email_payload = {
            "from": "CEO <ceo@company.com>",
            "to": ["finance@company.com"],
            "subject": "URGENT WIRE TRANSFER REQUEST!!!",
            "body_html": "<div>Confidential request: Please verify account and transfer funds to http://192.168.1.100/login immediately.</div>",
            "urls": ["http://192.168.1.100/login"]
        }
        processed = self.preprocessor.preprocess(email_payload)
        vector = self.composite_extractor.extract(processed)

        # Subject features
        self.assertEqual(vector.numerical_features["subject_word_count"], 4.0)
        self.assertTrue(vector.boolean_features["has_subject_urgency_keyword"])

        # Body features
        self.assertFalse(vector.boolean_features["is_empty_body"])
        self.assertEqual(vector.numerical_features["body_exclamation_count"], 0.0)

        # URL features
        self.assertTrue(vector.boolean_features["has_urls"])
        self.assertEqual(vector.numerical_features["ip_url_count"], 1.0)
        self.assertTrue(vector.boolean_features["has_ip_urls"])

        # Sender features
        self.assertTrue(vector.boolean_features["has_sender"])
        self.assertFalse(vector.boolean_features["is_freemail_provider"])

        # Structure features
        self.assertEqual(vector.numerical_features["recipient_count"], 1.0)
        self.assertTrue(vector.boolean_features["has_html"])

        # Keyword / Suspicious Language features
        self.assertGreater(vector.signal_counts["urgency_count"], 0)
        self.assertGreater(vector.signal_counts["social_engineering_count"], 0)

    def test_minimal_empty_email_input(self):
        # Empty/minimal email input with None subject, empty body, missing sender
        processed = self.preprocessor.preprocess("")
        vector = self.composite_extractor.extract(processed)

        self.assertTrue(vector.boolean_features["is_missing_subject"])
        self.assertTrue(vector.boolean_features["is_empty_body"])
        self.assertTrue(vector.boolean_features["is_missing_sender"])
        self.assertFalse(vector.boolean_features["has_urls"])
        self.assertEqual(vector.numerical_features["num_urls"], 0.0)
        self.assertEqual(vector.numerical_features["recipient_count"], 0.0)

    def test_feature_vector_serialization(self):
        processed = self.preprocessor.preprocess("Simple text http://test.xyz/login")
        vector = self.composite_extractor.extract(processed)

        # Dictionary serialization
        feature_dict = vector.to_dict()
        self.assertIsInstance(feature_dict, dict)
        self.assertIn("num_urls", feature_dict)
        self.assertIn("has_urls", feature_dict)

        # JSON serialization
        json_str = vector.to_json()
        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["num_urls"], 1.0)

        # Flat vector serialization
        flat_vec = vector.to_flat_vector()
        self.assertIsInstance(flat_vec, list)
        self.assertGreater(len(flat_vec), 0)
        for val in flat_vec:
            self.assertIsInstance(val, float)


if __name__ == "__main__":
    unittest.main()
