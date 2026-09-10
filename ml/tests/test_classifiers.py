import unittest
from ml.classifiers.email_classifier import EmailClassifier
from ml.classifiers.mock_classifier import MockClassifier
from ml.classifiers.base import BaseClassifier
from ml.classifiers.schemas import (
    ClassificationCategory,
    ClassifierLabel,
    ClassifierOutput
)
from ml.service.inference_service import MLInferenceService


class TestClassifierAbstractionAndMock(unittest.TestCase):

    def setUp(self):
        self.email_classifier = EmailClassifier()
        self.mock_classifier = MockClassifier()

    def test_interface_inheritance(self):
        self.assertIsInstance(self.email_classifier, BaseClassifier)
        self.assertIsInstance(self.mock_classifier, BaseClassifier)

    def test_mock_classifier_output_structure(self):
        email_payload = {
            "from": "attacker@phish.xyz",
            "subject": "URGENT: Verify Your Account Password",
            "body_text": "Click here to login now and confirm password immediately.",
            "urls": ["http://192.168.1.50/login"]
        }
        output = self.mock_classifier.predict_verdict(email_payload)

        self.assertIsInstance(output, ClassifierOutput)
        self.assertEqual(output.label, ClassifierLabel.PHISHING.value)
        self.assertTrue(0.0 <= output.confidence <= 1.0)
        self.assertTrue(output.is_placeholder)
        self.assertGreater(len(output.signals), 0)

        # Verify dictionary format matching exact required keys
        out_dict = output.to_dict()
        self.assertIn("label", out_dict)
        self.assertIn("confidence", out_dict)
        self.assertIn("signals", out_dict)
        self.assertIn("is_placeholder", out_dict)
        self.assertEqual(out_dict["label"], "phishing")
        self.assertTrue(out_dict["is_placeholder"])

    def test_confidence_validation(self):
        # Valid confidence scores
        valid_out = ClassifierOutput(label="benign", confidence=0.75, signals=["No threat"])
        self.assertEqual(valid_out.confidence, 0.75)

        # Invalid negative confidence score
        with self.assertRaises(ValueError):
            ClassifierOutput(label="benign", confidence=-0.1, signals=[])

        # Invalid > 1.0 confidence score
        with self.assertRaises(ValueError):
            ClassifierOutput(label="phishing", confidence=1.5, signals=[])

    def test_mock_classifier_benign_email(self):
        benign_payload = {
            "from": "colleague@company.com",
            "subject": "Lunch Plans",
            "body_text": "Hi, let's grab lunch at 12:30 today."
        }
        output = self.mock_classifier.predict_verdict(benign_payload)

        self.assertEqual(output.label, ClassifierLabel.BENIGN.value)
        self.assertTrue(0.0 <= output.confidence <= 1.0)
        self.assertTrue(output.is_placeholder)
        self.assertIn("No overt security threat indicators detected.", output.signals[0])

    def test_pluggability_in_inference_service(self):
        # Verify MLInferenceService works seamlessly with MockClassifier
        service = MLInferenceService(classifier=self.mock_classifier)
        res = service.analyze_email({"subject": "Hello", "body": "World"})

        self.assertIsNotNone(res)
        self.assertTrue(res.metadata.get("is_placeholder", True))


if __name__ == "__main__":
    unittest.main()
