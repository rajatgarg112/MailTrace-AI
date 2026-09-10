"""
Metrics calculator utilities for evaluating classification performance.
Provides accuracy, precision, recall, F1 score, confusion matrix, and multi-class report utilities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional, Union


@dataclass
class EvaluationReport:
    """Standardized metric report container."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: Dict[str, Any]
    total_samples: int
    per_class_metrics: Dict[str, Any] = field(default_factory=dict)
    is_synthetic: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert EvaluationReport to a JSON-serializable dictionary."""
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "confusion_matrix": self.confusion_matrix,
            "total_samples": self.total_samples,
            "per_class_metrics": self.per_class_metrics,
            "is_synthetic": self.is_synthetic,
            "metadata": self.metadata
        }


def compute_accuracy(y_true: List[Any], y_pred: List[Any]) -> float:
    """Computes overall classification accuracy."""
    if not y_true or len(y_true) != len(y_pred):
        return 0.0
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return round(correct / len(y_true), 4)


def compute_precision(y_true: List[Any], y_pred: List[Any], pos_label: Any = 1) -> float:
    """Computes precision score for target positive label."""
    if not y_true or len(y_true) != len(y_pred):
        return 0.0
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == pos_label and yp == pos_label)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != pos_label and yp == pos_label)
    return round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0


def compute_recall(y_true: List[Any], y_pred: List[Any], pos_label: Any = 1) -> float:
    """Computes recall score for target positive label."""
    if not y_true or len(y_true) != len(y_pred):
        return 0.0
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == pos_label and yp == pos_label)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == pos_label and yp != pos_label)
    return round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0


def compute_f1_score(y_true: List[Any], y_pred: List[Any], pos_label: Any = 1) -> float:
    """Computes F1 score for target positive label."""
    prec = compute_precision(y_true, y_pred, pos_label=pos_label)
    rec = compute_recall(y_true, y_pred, pos_label=pos_label)
    return round((2 * prec * rec) / (prec + rec), 4) if (prec + rec) > 0 else 0.0


def compute_precision_recall_f1(y_true: List[Any], y_pred: List[Any], pos_label: Any = 1) -> Tuple[float, float, float]:
    """Computes binary precision, recall, and F1 score."""
    prec = compute_precision(y_true, y_pred, pos_label=pos_label)
    rec = compute_recall(y_true, y_pred, pos_label=pos_label)
    f1 = compute_f1_score(y_true, y_pred, pos_label=pos_label)
    return prec, rec, f1


def compute_confusion_matrix(y_true: List[Any], y_pred: List[Any], labels: Optional[List[Any]] = None) -> Dict[str, Any]:
    """
    Computes binary or multi-class confusion matrix breakdown.
    For binary (0/1 or benign/phishing), returns true_positives, true_negatives, false_positives, false_negatives.
    For multi-class, returns nested label mapping counts.
    """
    if not y_true or len(y_true) != len(y_pred):
        return {"error": "Empty or mismatched prediction lists"}

    # Binary case
    if set(y_true).issubset({0, 1}) and set(y_pred).issubset({0, 1}):
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
        return {"true_positives": tp, "true_negatives": tn, "false_positives": fp, "false_negatives": fn}

    # Multi-class case
    target_labels = labels or list(dict.fromkeys(list(y_true) + list(y_pred)))
    matrix: Dict[str, Dict[str, int]] = {str(true_lbl): {str(pred_lbl): 0 for pred_lbl in target_labels} for true_lbl in target_labels}

    for yt, yp in zip(y_true, y_pred):
        s_yt, s_yp = str(yt), str(yp)
        if s_yt in matrix and s_yp in matrix[s_yt]:
            matrix[s_yt][s_yp] += 1

    return matrix


def compute_multiclass_metrics(y_true: List[str], y_pred: List[str], labels: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Computes per-class precision, recall, and F1 scores across labels (e.g. phishing, suspicious, benign, unknown).
    """
    target_labels = labels or list(dict.fromkeys(list(y_true) + list(y_pred)))
    per_class = {}

    for label in target_labels:
        prec = compute_precision(y_true, y_pred, pos_label=label)
        rec = compute_recall(y_true, y_pred, pos_label=label)
        f1 = compute_f1_score(y_true, y_pred, pos_label=label)
        per_class[label] = {
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "support": sum(1 for y in y_true if y == label)
        }

    macro_prec = round(sum(v["precision"] for v in per_class.values()) / max(len(per_class), 1), 4)
    macro_rec = round(sum(v["recall"] for v in per_class.values()) / max(len(per_class), 1), 4)
    macro_f1 = round(sum(v["f1_score"] for v in per_class.values()) / max(len(per_class), 1), 4)

    return {
        "per_class": per_class,
        "macro_avg": {
            "precision": macro_prec,
            "recall": macro_rec,
            "f1_score": macro_f1
        }
    }
