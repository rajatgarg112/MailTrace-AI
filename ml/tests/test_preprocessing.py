import unittest
from ml.preprocessing.email_preprocessor import EmailPreprocessor
from ml.preprocessing.normalizer import TextNormalizer
from ml.preprocessing.indicator_extractor import IndicatorExtractor


class TestEmailPreprocessor(unittest.TestCase):

    def setUp(self):
        self.preprocessor = EmailPreprocessor()
        self.normalizer = TextNormalizer()
        self.indicator_extractor = IndicatorExtractor()

    def test_text_normalizer(self):
        html_input = "<html><body><h1>URGENT &amp; IMPORTANT</h1><p>Check   link &lt;here&gt;.</p></body></html>"
        cleaned = self.normalizer.clean_text(html_input)
        self.assertEqual(cleaned, "URGENT & IMPORTANT Check link <here>.")

        tokens = self.normalizer.tokenize(cleaned)
        self.assertIn("urgent", tokens)
        self.assertIn("important", tokens)

    def test_full_email_preprocessing(self):
        payload = {
            "from": "Alice Smith <alice@example.com>",
            "to": ["bob@example.com", "carol@example.com"],
            "cc": "dave@example.com",
            "subject": "  Project Status Update  ",
            "body_html": "<div>Hello Team,<br>Please review the link at https://work.example.com/docs</div>",
            "urls": ["https://work.example.com/docs"]
        }

        processed = self.preprocessor.preprocess(payload)

        self.assertEqual(processed.cleaned_subject, "Project Status Update")
        self.assertEqual(processed.sender_email, "alice@example.com")
        self.assertEqual(processed.sender_domain, "example.com")
        self.assertEqual(len(processed.recipients), 3)
        self.assertIn("bob@example.com", processed.recipients)
        self.assertIn("carol@example.com", processed.recipients)
        self.assertIn("dave@example.com", processed.recipients)
        self.assertIn("example.com", processed.recipient_domains)
        self.assertEqual(len(processed.extracted_urls), 1)
        self.assertEqual(processed.extracted_urls[0], "https://work.example.com/docs")
        self.assertFalse(processed.text_indicators["is_missing_subject"])
        self.assertFalse(processed.text_indicators["is_empty_body"])
        self.assertFalse(processed.text_indicators["is_missing_sender"])
        self.assertTrue(processed.text_indicators["has_urls"])

    def test_missing_subject_handling(self):
        payload = {
            "from": "sender@test.org",
            "to": "user@test.org",
            "body_text": "Email without a subject line."
        }
        processed = self.preprocessor.preprocess(payload)

        self.assertEqual(processed.cleaned_subject, "")
        self.assertTrue(processed.text_indicators["is_missing_subject"])
        self.assertFalse(processed.text_indicators["has_subject"])

    def test_empty_body_handling(self):
        payload = {
            "from": "sender@test.org",
            "subject": "No Content Email",
            "body_text": ""
        }
        processed = self.preprocessor.preprocess(payload)

        self.assertEqual(processed.cleaned_body, "")
        self.assertTrue(processed.text_indicators["is_empty_body"])
        self.assertFalse(processed.text_indicators["has_body"])
        self.assertEqual(processed.metadata["token_count"], 3)  # Tokens from subject

    def test_missing_sender_handling(self):
        payload = {
            "subject": "Anonymous Email",
            "body_text": "Sender is omitted."
        }
        processed = self.preprocessor.preprocess(payload)

        self.assertIsNone(processed.sender_email)
        self.assertIsNone(processed.sender_domain)
        self.assertTrue(processed.text_indicators["is_missing_sender"])
        self.assertFalse(processed.text_indicators["has_sender"])

    def test_empty_url_list_handling(self):
        payload = {
            "from": "sender@test.org",
            "subject": "Plain Text Email",
            "body_text": "Just plain text without any links.",
            "urls": []
        }
        processed = self.preprocessor.preprocess(payload)

        self.assertEqual(processed.extracted_urls, [])
        self.assertFalse(processed.text_indicators["has_urls"])
        self.assertEqual(processed.text_indicators["num_urls"], 0)

    def test_raw_string_input(self):
        raw_text = "Check out https://test.com now!"
        processed = self.preprocessor.preprocess(raw_text)

        self.assertEqual(processed.cleaned_body, "Check out https://test.com now!")
        self.assertEqual(len(processed.extracted_urls), 1)
        self.assertTrue(processed.text_indicators["is_missing_subject"])
        self.assertTrue(processed.text_indicators["is_missing_sender"])


if __name__ == "__main__":
    unittest.main()
