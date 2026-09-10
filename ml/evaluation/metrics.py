"""
Metrics calculator utilities for evaluating classification performance.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


@dataclass
class EvaluationReport:
    """Standardized metric report container."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: Dict[str, int]
    total_samples: int
    signal_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "confusion_matrix": self.confusion_matrix,
            "total_samples": self.total_samples,
            "signal_metrics": self.signal_metrics
        }


def compute_accuracy(y_true: List[int], y_pred: List[int]) -> float:
    """Computes overall accuracy."""
    if not y_true or len(y_true) != len(y_pred):
        return 0.0
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return correct / len(y_true)


def compute_precision_recall_f1(y_true: List[int], y_pred: List[int], pos_label: int = 1) -> Tuple[float, float, float]:
    """Computes binary precision, recall, and F1 score."""
    if not y_true or len(y_true) != len(y_pred):
        return 0.0, 0.0, 0.0

    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == pos_label and yp == pos_label)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != pos_label and yp == pos_label)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == pos_label and yp != pos_label)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def compute_confusion_matrix(y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
    """Computes binary confusion matrix counts."""
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    return {"true_positives": tp, "true_negatives": tn, "false_positives": fp, "false_negatives": fn}
