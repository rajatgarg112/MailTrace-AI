import unittest
from ml.service.inference_service import MLInferenceService
from ml.classifiers.schemas import ClassificationCategory


class TestInferenceService(unittest.TestCase):

    def setUp(self):
        self.service = MLInferenceService()

    def test_analyze_email_success(self):
        payload = {
            "subject": "Invoice attached",
            "body_text": "Please see attached wire transfer invoice for CEO approval."
        }
        result = self.service.analyze_email(payload)

        self.assertIsNotNone(result.execution_time_ms)
        self.assertGreater(result.execution_time_ms, 0.0)
        self.assertEqual(result.model_version, "1.0.0-phase1")
        self.assertTrue(isinstance(result.to_dict(), dict))

    def test_failsafe_fallback(self):
        # Force classifier failure by passing invalid object if needed
        class BrokenClassifier:
            def classify(self, inp):
                raise ValueError("Simulated unexpected ML failure")

        service = MLInferenceService(classifier=BrokenClassifier())
        result = service.analyze_email("some input")

        self.assertEqual(result.classification, ClassificationCategory.UNKNOWN.value)
        self.assertIn("FAILSAFE", result.signals[0])
        self.assertTrue(result.metadata.get("failsafe"))


if __name__ == "__main__":
    unittest.main()
