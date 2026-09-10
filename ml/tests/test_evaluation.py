import unittest
from ml.evaluation.metrics import (
    compute_accuracy,
    compute_precision_recall_f1,
    compute_confusion_matrix,
    EvaluationReport
)


class TestEvaluationMetrics(unittest.TestCase):

    def test_metrics_calculation(self):
        y_true = [1, 1, 0, 0, 1]
        y_pred = [1, 0, 0, 0, 1]

        acc = compute_accuracy(y_true, y_pred)
        prec, rec, f1 = compute_precision_recall_f1(y_true, y_pred)
        cm = compute_confusion_matrix(y_true, y_pred)

        self.assertEqual(acc, 0.8)
        self.assertEqual(prec, 1.0)
        self.assertAlmostEqual(rec, 2 / 3, places=2)
        self.assertEqual(cm["true_positives"], 2)
        self.assertEqual(cm["true_negatives"], 2)
        self.assertEqual(cm["false_negatives"], 1)

    def test_report_serialization(self):
        report = EvaluationReport(
            accuracy=0.9,
            precision=0.95,
            recall=0.85,
            f1_score=0.90,
            confusion_matrix={"true_positives": 17, "true_negatives": 18, "false_positives": 1, "false_negatives": 3},
            total_samples=39
        )
        data = report.to_dict()
        self.assertEqual(data["accuracy"], 0.9)
        self.assertEqual(data["total_samples"], 39)


if __name__ == "__main__":
    unittest.main()
