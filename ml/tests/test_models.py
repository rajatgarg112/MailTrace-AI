import unittest
from ml.models.placeholder_model import PlaceholderModel
from ml.models.mock_model import MockClassifierModel
from ml.models.base import BaseModel
from ml.features.base import FeatureVector


class TestModelsAndPlaceholderTagging(unittest.TestCase):

    def setUp(self):
        self.placeholder_model = PlaceholderModel()
        self.mock_model = MockClassifierModel()

    def test_base_model_inheritance(self):
        self.assertIsInstance(self.placeholder_model, BaseModel)
        self.assertIsInstance(self.mock_model, BaseModel)
        self.assertTrue(self.placeholder_model.is_placeholder())
        self.assertTrue(self.mock_model.is_placeholder())

    def test_mock_model_predict_proba(self):
        vec = FeatureVector(
            signal_counts={"phishing_credentials_count": 2, "urgency_count": 1},
            numerical_features={"num_urls": 2.0},
            boolean_features={"has_ip_urls": True}
        )
        proba = self.mock_model.predict_proba(vec)

        self.assertIn("phishing", proba)
        self.assertIn("suspicious", proba)
        self.assertIn("benign", proba)
        self.assertGreater(proba["phishing"], 0.5)

    def test_mock_model_metadata(self):
        meta = self.mock_model.get_metadata()
        self.assertEqual(meta["model_name"], "mock_classifier_placeholder")
        self.assertTrue(meta["is_placeholder"])
        self.assertEqual(meta["type"], "MockPlaceholderClassifier")


if __name__ == "__main__":
    unittest.main()
