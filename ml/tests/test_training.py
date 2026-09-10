import os
import unittest
from ml.config.training_config import TrainingConfig
from ml.training.dataset_loader import EmailDatasetLoader
from ml.training.train_pipeline import TrainingPipeline


class TestTrainingStructure(unittest.TestCase):

    def test_training_config_defaults(self):
        config = TrainingConfig()
        self.assertEqual(config.dataset_name, "placeholder_email_dataset")
        self.assertEqual(config.epochs, 1)
        self.assertEqual(config.batch_size, 16)
        self.assertEqual(config.train_data_dir, "ml/data/train/")
        self.assertEqual(config.artifact_export_dir, "ml/artifacts/")

    def test_training_config_from_dict(self):
        data = {
            "dataset_name": "custom_phishing_v1",
            "epochs": 10,
            "batch_size": 32,
            "learning_rate": 0.00005
        }
        config = TrainingConfig.from_dict(data)
        self.assertEqual(config.dataset_name, "custom_phishing_v1")
        self.assertEqual(config.epochs, 10)
        self.assertEqual(config.batch_size, 32)
        self.assertEqual(config.learning_rate, 0.00005)

    def test_dataset_loader(self):
        loader = EmailDatasetLoader()
        train_split, val_split, test_split = loader.load_dataset()

        self.assertEqual(train_split.name, "train")
        self.assertEqual(val_split.name, "val")
        self.assertEqual(test_split.name, "test")
        self.assertGreater(len(train_split.inputs), 0)

    def test_training_pipeline_run(self):
        pipeline = TrainingPipeline()
        res = pipeline.run_pipeline()

        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res["is_placeholder"])
        self.assertIn("artifact_path", res)
        self.assertIn("metrics", res)

    def test_directory_placeholders_exist(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "data", "train", ".gitkeep")))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "data", "val", ".gitkeep")))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "data", "test", ".gitkeep")))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "artifacts", ".gitkeep")))


if __name__ == "__main__":
    unittest.main()
