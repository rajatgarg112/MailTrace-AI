import unittest
from ml.evaluation.metrics import (
    compute_accuracy,
    compute_precision,
    compute_recall,
    compute_f1_score,
    compute_precision_recall_f1,
    compute_confusion_matrix,
    compute_multiclass_metrics,
    EvaluationReport
)
from ml.evaluation.evaluator import ModelEvaluator
from ml.classifiers.mock_classifier import MockClassifier


class TestEvaluationFramework(unittest.TestCase):

    def setUp(self):
        self.evaluator = ModelEvaluator()
        self.mock_classifier = MockClassifier()

    def test_binary_metrics_calculation(self):
        y_true = [1, 1, 0, 0, 1]
        y_pred = [1, 0, 0, 0, 1]

        acc = compute_accuracy(y_true, y_pred)
        prec = compute_precision(y_true, y_pred, pos_label=1)
        rec = compute_recall(y_true, y_pred, pos_label=1)
        f1 = compute_f1_score(y_true, y_pred, pos_label=1)
        cm = compute_confusion_matrix(y_true, y_pred)

        self.assertEqual(acc, 0.8)
        self.assertEqual(prec, 1.0)
        self.assertAlmostEqual(rec, 0.6667, places=3)
        self.assertAlmostEqual(f1, 0.8, places=3)
        self.assertEqual(cm["true_positives"], 2)
        self.assertEqual(cm["true_negatives"], 2)
        self.assertEqual(cm["false_negatives"], 1)

    def test_multiclass_label_metrics(self):
        y_true = ["phishing", "phishing", "benign", "benign", "suspicious"]
        y_pred = ["phishing", "suspicious", "benign", "benign", "suspicious"]

        res = compute_multiclass_metrics(y_true, y_pred)
        self.assertIn("per_class", res)
        self.assertIn("macro_avg", res)
        self.assertEqual(res["per_class"]["benign"]["precision"], 1.0)
        self.assertEqual(res["per_class"]["benign"]["recall"], 1.0)

    def test_evaluator_predictions(self):
        y_true = ["phishing", "benign", "suspicious"]
        y_pred = ["phishing", "benign", "suspicious"]

        report = self.evaluator.evaluate_predictions(y_true, y_pred, is_synthetic=True, model_name="test_model")

        self.assertEqual(report.accuracy, 1.0)
        self.assertEqual(report.precision, 1.0)
        self.assertEqual(report.recall, 1.0)
        self.assertEqual(report.f1_score, 1.0)
        self.assertTrue(report.is_synthetic)
        self.assertEqual(report.total_samples, 3)

    def test_evaluator_classifier_run(self):
        dataset = [
            {"email": {"subject": "URGENT: Verify Account", "body": "Click link http://192.168.1.1/login"}, "label": "phishing"},
            {"email": {"subject": "Lunch Plans", "body": "Let's meet for lunch."}, "label": "benign"}
        ]
        report = self.evaluator.evaluate_classifier(self.mock_classifier, dataset, is_synthetic=True)

        self.assertIsInstance(report, EvaluationReport)
        self.assertEqual(report.total_samples, 2)
        self.assertTrue(report.is_synthetic)

    def test_synthetic_benchmark_flagging(self):
        report = self.evaluator.generate_synthetic_benchmark()
        self.assertTrue(report.is_synthetic)
        self.assertEqual(report.metadata["is_synthetic"], True)
        self.assertIn("description", report.metadata)

    def test_report_serialization(self):
        report = EvaluationReport(
            accuracy=0.9,
            precision=0.95,
            recall=0.85,
            f1_score=0.90,
            confusion_matrix={"true_positives": 17, "true_negatives": 18, "false_positives": 1, "false_negatives": 3},
            total_samples=39,
            is_synthetic=True
        )
        data = report.to_dict()
        self.assertEqual(data["accuracy"], 0.9)
        self.assertEqual(data["total_samples"], 39)
        self.assertTrue(data["is_synthetic"])


if __name__ == "__main__":
    unittest.main()
