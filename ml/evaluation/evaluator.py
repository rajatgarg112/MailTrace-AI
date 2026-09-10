"""
High-level Model Evaluator for running metric benchmarks against test datasets.
"""

from typing import List, Dict, Any, Optional
from .metrics import (
    EvaluationReport,
    compute_accuracy,
    compute_precision,
    compute_recall,
    compute_f1_score,
    compute_precision_recall_f1,
    compute_confusion_matrix,
    compute_multiclass_metrics
)
from ..models.base import BaseModel
from ..classifiers.base import BaseClassifier
from ..features.base import FeatureVector


class ModelEvaluator:
    """
    Evaluates trained models or classifiers against benchmark datasets.
    Can evaluate real prediction lists, feature vectors, or synthetic benchmarks.
    """

    def evaluate_predictions(
        self,
        y_true: List[Any],
        y_pred: List[Any],
        is_synthetic: bool = False,
        model_name: str = "unknown"
    ) -> EvaluationReport:
        """
        Evaluates a list of ground truth labels vs model predictions.
        
        Args:
            y_true: Ground truth labels (strings or ints)
            y_pred: Predicted labels (strings or ints)
            is_synthetic: Flag indicating whether input data is mock/synthetic
            model_name: Model identifier string
            
        Returns:
            EvaluationReport object
        """
        if not y_true or len(y_true) != len(y_pred):
            return EvaluationReport(
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                confusion_matrix={},
                total_samples=0,
                is_synthetic=is_synthetic,
                metadata={"error": "Empty or mismatched prediction lists"}
            )

        acc = compute_accuracy(y_true, y_pred)
        cm = compute_confusion_matrix(y_true, y_pred)

        # Check if binary or multi-class
        if set(y_true).issubset({0, 1}) and set(y_pred).issubset({0, 1}):
            prec, rec, f1 = compute_precision_recall_f1(y_true, y_pred, pos_label=1)
            per_class = {}
        else:
            multiclass_res = compute_multiclass_metrics(y_true, y_pred)
            macro = multiclass_res["macro_avg"]
            prec, rec, f1 = macro["precision"], macro["recall"], macro["f1_score"]
            per_class = multiclass_res["per_class"]

        return EvaluationReport(
            accuracy=acc,
            precision=prec,
            recall=rec,
            f1_score=f1,
            confusion_matrix=cm,
            total_samples=len(y_true),
            per_class_metrics=per_class,
            is_synthetic=is_synthetic,
            metadata={
                "model_name": model_name,
                "is_synthetic": is_synthetic
            }
        )

    def evaluate_classifier(
        self,
        classifier: BaseClassifier,
        test_dataset: List[Dict[str, Any]],
        is_synthetic: bool = False
    ) -> EvaluationReport:
        """
        Runs a classifier on a list of test emails with ground truth labels.
        Each test item should be a dict: {"email": {...}, "label": "phishing" | "benign" | ...}
        """
        y_true = []
        y_pred = []

        for item in test_dataset:
            email_payload = item.get("email", item)
            true_label = item.get("label", "unknown")
            verdict = classifier.predict_verdict(email_payload)
            y_true.append(true_label)
            y_pred.append(verdict.label)

        model_name = getattr(classifier, "name", classifier.__class__.__name__)
        return self.evaluate_predictions(y_true, y_pred, is_synthetic=is_synthetic, model_name=model_name)

    def evaluate_vectors(
        self,
        model: BaseModel,
        test_vectors: List[FeatureVector],
        ground_truth: List[int],
        is_synthetic: bool = False
    ) -> EvaluationReport:
        """
        Runs model predictions on test vectors and returns an EvaluationReport.
        """
        predictions = [model.predict(vec) for vec in test_vectors]
        model_name = model.get_metadata().get("model_name", "unknown")
        return self.evaluate_predictions(ground_truth, predictions, is_synthetic=is_synthetic, model_name=model_name)

    def generate_synthetic_benchmark(self) -> EvaluationReport:
        """
        Generates a synthetic evaluation report clearly tagged as mock/synthetic data for Phase 1.
        Does NOT claim or fabricate real model accuracy.
        """
        synthetic_y_true = ["phishing", "phishing", "benign", "benign", "suspicious", "phishing"]
        synthetic_y_pred = ["phishing", "benign", "benign", "benign", "suspicious", "phishing"]

        report = self.evaluate_predictions(
            y_true=synthetic_y_true,
            y_pred=synthetic_y_pred,
            is_synthetic=True,
            model_name="mock_classifier_placeholder"
        )
        report.metadata["description"] = "Phase 1 synthetic evaluation benchmark for testing evaluation utilities."
        return report
