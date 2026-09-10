import unittest
from ml.preprocessing.email_preprocessor import EmailPreprocessor


class TestEmailPreprocessor(unittest.TestCase):

    def setUp(self):
        self.preprocessor = EmailPreprocessor()

    def test_preprocess_string(self):
        raw_text = "<html><body>URGENT: Verify your account at https://phish.example.com immediately!</body></html>"
        processed = self.preprocessor.preprocess(raw_text)

        self.assertIn("verify your account", processed.cleaned_body.lower())
        self.assertEqual(len(processed.extracted_urls), 1)
        self.assertEqual(processed.extracted_urls[0], "https://phish.example.com")
        self.assertTrue(processed.metadata["has_html"])

    def test_preprocess_dict(self):
        email_dict = {
            "message": {
                "subject": "Security Alert!",
                "from": "admin@security-check.com",
                "body_text": "Please update your password."
            }
        }
        processed = self.preprocessor.preprocess(email_dict)

        self.assertEqual(processed.cleaned_subject, "Security Alert!")
        self.assertEqual(processed.sender_email, "admin@security-check.com")
        self.assertEqual(processed.sender_domain, "security-check.com")
        self.assertIn("security alert!", processed.combined_text.lower())


if __name__ == "__main__":
    unittest.main()
