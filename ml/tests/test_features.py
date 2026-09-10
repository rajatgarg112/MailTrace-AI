import unittest
from ml.preprocessing.email_preprocessor import EmailPreprocessor
from ml.features.text_features import TextFeatureExtractor
from ml.features.keyword_features import KeywordFeatureExtractor


class TestFeatureExtractors(unittest.TestCase):

    def setUp(self):
        self.preprocessor = EmailPreprocessor()
        self.text_extractor = TextFeatureExtractor()
        self.keyword_extractor = KeywordFeatureExtractor()

    def test_text_features(self):
        email_dict = {
            "subject": "URGENT ACTION REQUIRED!!!",
            "body_text": "Click here https://example.com/login"
        }
        processed = self.preprocessor.preprocess(email_dict)
        features = self.text_extractor.extract(processed)

        self.assertGreater(features.numerical_features["uppercase_ratio"], 0.20)
        self.assertEqual(features.numerical_features["exclamation_count"], 3.0)
        self.assertTrue(features.boolean_features["has_urls"])
        self.assertTrue(features.boolean_features["has_excessive_exclamation"])

    def test_keyword_features(self):
        email_dict = {
            "subject": "Confidential CEO Wire Transfer Request",
            "body_text": "URGENT: Verify account and confirm password immediately for executive request."
        }
        processed = self.preprocessor.preprocess(email_dict)
        features = self.keyword_extractor.extract(processed)

        self.assertGreater(features.signal_counts["urgency_count"], 0)
        self.assertGreater(features.signal_counts["phishing_credentials_count"], 0)
        self.assertGreater(features.signal_counts["social_engineering_count"], 0)
        self.assertTrue(features.boolean_features["has_urgency_keywords"])


if __name__ == "__main__":
    unittest.main()
