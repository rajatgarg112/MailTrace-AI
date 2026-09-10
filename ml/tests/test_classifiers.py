import unittest
from ml.classifiers.email_classifier import EmailClassifier
from ml.classifiers.schemas import ClassificationCategory


class TestEmailClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = EmailClassifier()

    def test_benign_email_classification(self):
        email_payload = {
            "subject": "Weekly Team Catchup",
            "body_text": "Hi team, please find attached the agenda for tomorrow's meeting."
        }
        result = self.classifier.classify(email_payload)

        self.assertEqual(result.classification, ClassificationCategory.SAFE.value)
        self.assertLess(result.overall_risk_score, 40.0)
        self.assertFalse(result.phishing_verdict.detected)

    def test_phishing_email_classification(self):
        email_payload = {
            "subject": "URGENT: Account Suspended Within 24 Hours",
            "body_text": "Click here https://verify-login.com to confirm password and verify account immediately."
        }
        result = self.classifier.classify(email_payload)

        self.assertIn(result.classification, [ClassificationCategory.SUSPICIOUS.value, ClassificationCategory.MALICIOUS.value])
        self.assertTrue(result.phishing_verdict.detected)
        self.assertTrue(result.suspicious_language_verdict.detected)
        self.assertGreater(len(result.signals), 0)


if __name__ == "__main__":
    unittest.main()
