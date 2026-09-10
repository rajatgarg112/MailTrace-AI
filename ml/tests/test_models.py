import unittest
from ml.models.placeholder_model import PlaceholderModel
from ml.features.base import FeatureVector


class TestPlaceholderModel(unittest.TestCase):

    def setUp(self):
        self.model = PlaceholderModel()

    def test_predict_proba_safe(self):
        vec = FeatureVector(
            signal_counts={"phishing_credentials_count": 0, "urgency_count": 0},
            numerical_features={"num_urls": 0.0, "uppercase_ratio": 0.05}
        )
        proba = self.model.predict_proba(vec)
        self.assertGreater(proba["safe"], proba["malicious"])
        self.assertEqual(self.model.predict(vec), 0)  # Safe

    def test_predict_proba_malicious(self):
        vec = FeatureVector(
            signal_counts={
                "phishing_credentials_count": 2,
                "urgency_count": 2,
                "social_engineering_count": 1,
                "malicious_cues_count": 1
            },
            numerical_features={"num_urls": 3.0, "uppercase_ratio": 0.35}
        )
        proba = self.model.predict_proba(vec)
        self.assertGreater(proba["malicious"], 0.6)
        self.assertEqual(self.model.predict(vec), 2)  # Malicious

    def test_metadata(self):
        meta = self.model.get_metadata()
        self.assertEqual(meta["model_name"], "placeholder_detector")


if __name__ == "__main__":
    unittest.main()
