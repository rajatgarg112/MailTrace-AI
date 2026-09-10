import unittest
from ml.config.ml_config import MLConfig, ModelConfig, FeatureConfig


class TestMLConfig(unittest.TestCase):

    def test_default_config(self):
        config = MLConfig()
        self.assertEqual(config.environment, "development")
        self.assertEqual(config.model.model_name, "placeholder_detector")
        self.assertEqual(config.model.threshold_malicious, 0.70)
        self.assertTrue(config.features.enable_keyword_matching)

    def test_from_dict(self):
        data = {
            "environment": "production",
            "failsafe_fallback_enabled": False,
            "model": {
                "model_name": "deberta_v2",
                "threshold_malicious": 0.85
            }
        }
        config = MLConfig.from_dict(data)
        self.assertEqual(config.environment, "production")
        self.assertFalse(config.failsafe_fallback_enabled)
        self.assertEqual(config.model.model_name, "deberta_v2")
        self.assertEqual(config.model.threshold_malicious, 0.85)


if __name__ == "__main__":
    unittest.main()
