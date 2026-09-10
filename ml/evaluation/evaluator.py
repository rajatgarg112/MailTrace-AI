"""
High-level Model Evaluator for running metric benchmarks against test datasets.
"""

from typing import List, Dict, Any
from .metrics import (
    EvaluationReport,
    compute_accuracy,
    compute_precision_recall_f1,
    compute_confusion_matrix
)
from ..models.base import BaseModel
from ..features.base import FeatureVector


class ModelEvaluator:
    """
    Evaluates a trained model or classifier against a benchmark dataset.
    """

    def evaluate_vectors(
        self,
        model: BaseModel,
        test_vectors: List[FeatureVector],
        ground_truth: List[int]
    ) -> EvaluationReport:
        """
        Runs model predictions on test vectors and returns an EvaluationReport.
        """
        predictions = [model.predict(vec) for vec in test_vectors]

        # Convert multi-class (0=Safe, 1=Suspicious, 2=Malicious) to binary for simple metrics
        binary_true = [1 if y > 0 else 0 for y in ground_truth]
        binary_pred = [1 if p > 0 else 0 for p in predictions]

        acc = compute_accuracy(binary_true, binary_pred)
        prec, rec, f1 = compute_precision_recall_f1(binary_true, binary_pred)
        cm = compute_confusion_matrix(binary_true, binary_pred)

        return EvaluationReport(
            accuracy=acc,
            precision=prec,
            recall=rec,
            f1_score=f1,
            confusion_matrix=cm,
            total_samples=len(ground_truth),
            signal_metrics={
                "binary_accuracy": acc,
                "evaluated_model": model.get_metadata().get("model_name", "unknown")
            }
        )
