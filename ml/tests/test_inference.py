import unittest
from ml.service.inference_service import MLInferenceService, MLInferenceResult
from ml.classifiers.mock_classifier import MockClassifier
from ml.classifiers.email_classifier import EmailClassifier
from ml.preprocessing.email_preprocessor import EmailPreprocessor
from ml.features.composite_extractor import EmailFeatureExtractor


class TestInferenceService(unittest.TestCase):

    def setUp(self):
        self.service = MLInferenceService()

    def test_end_to_end_phishing_inference(self):
        payload = {
            "from": "phisher@fakebank.xyz",
            "subject": "URGENT: Account Security Verification Required",
            "body_text": "Click here http://192.168.1.50/verify to update your password immediately.",
            "urls": ["http://192.168.1.50/verify"]
        }
        result = self.service.run_inference_pipeline(payload)

        self.assertIsInstance(result, MLInferenceResult)
        self.assertEqual(result.source, "ml")
        self.assertEqual(result.label, "phishing")
        self.assertGreater(result.confidence, 0.5)
        self.assertGreater(len(result.signals), 0)
        self.assertTrue(result.is_placeholder)
        self.assertGreaterEqual(result.execution_time_ms, 0.0)

        # Dictionary format serialization check
        res_dict = result.to_dict()
        self.assertEqual(res_dict["source"], "ml")
        self.assertEqual(res_dict["label"], "phishing")
        self.assertIn("execution_time_ms", res_dict)
        self.assertTrue(res_dict["is_placeholder"])

    def test_end_to_end_benign_inference(self):
        payload = {
            "from": "friend@company.com",
            "subject": "Coffee catchup",
            "body_text": "Are you free for coffee later today?"
        }
        result = self.service.analyze_email(payload)

        self.assertEqual(result.source, "ml")
        self.assertEqual(result.label, "benign")
        self.assertGreater(result.confidence, 0.5)
        self.assertTrue(result.is_placeholder)

    def test_modularity_injection(self):
        # Inject custom components explicitly into service
        custom_preprocessor = EmailPreprocessor()
        custom_extractor = EmailFeatureExtractor()
        custom_classifier = MockClassifier()

        custom_service = MLInferenceService(
            preprocessor=custom_preprocessor,
            feature_extractor=custom_extractor,
            classifier=custom_classifier
        )

        res = custom_service.run_inference_pipeline({"subject": "Hello", "body": "World"})
        self.assertEqual(res.source, "ml")
        self.assertIsNotNone(res.execution_time_ms)

    def test_failsafe_fallback_on_error(self):
        # Force classifier exception
        class BrokenClassifier:
            def predict_verdict(self, inp):
                raise ValueError("Simulated unexpected classifier error")

        service = MLInferenceService(classifier=BrokenClassifier())
        result = service.analyze_email("some input")

        self.assertEqual(result.source, "ml")
        self.assertEqual(result.label, "unknown")
        self.assertEqual(result.confidence, 0.0)
        self.assertIn("FAILSAFE", result.signals[0])
        self.assertTrue(result.metadata.get("failsafe"))


if __name__ == "__main__":
    unittest.main()
