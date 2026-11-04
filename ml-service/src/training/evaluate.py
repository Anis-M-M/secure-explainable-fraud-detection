"""
Model evaluation module.

Computes Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC and
confusion matrix.  Answers RQ1: comparative model performance.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    classification_report,
)

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    confusion_matrix: list = field(default_factory=list)
    threshold: float = 0.5

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "roc_auc": round(self.roc_auc, 4),
            "pr_auc": round(self.pr_auc, 4),
            "confusion_matrix": {
                "tn": int(self.confusion_matrix[0][0]),
                "fp": int(self.confusion_matrix[0][1]),
                "fn": int(self.confusion_matrix[1][0]),
                "tp": int(self.confusion_matrix[1][1]),
            },
        }


class Evaluator:
    """Evaluate a trained classifier on a held-out test set."""

    def evaluate(
        self,
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_name: str = "Model",
        threshold: float = 0.5,
    ) -> ModelMetrics:
        """Evaluate sklearn-compatible model (has predict_proba)."""
        y_prob = model.predict_proba(X_test)[:, 1]
        return self.evaluate_from_probs(y_prob, y_test, model_name, threshold)

    def evaluate_from_probs(
        self,
        y_prob: np.ndarray,
        y_test: np.ndarray,
        model_name: str = "Model",
        threshold: float = 0.5,
    ) -> ModelMetrics:
        y_pred = (y_prob >= threshold).astype(int)
        cm = confusion_matrix(y_test, y_pred)

        metrics = ModelMetrics(
            model_name=model_name,
            accuracy=accuracy_score(y_test, y_pred),
            precision=precision_score(y_test, y_pred, zero_division=0),
            recall=recall_score(y_test, y_pred, zero_division=0),
            f1_score=f1_score(y_test, y_pred, zero_division=0),
            roc_auc=roc_auc_score(y_test, y_prob),
            pr_auc=average_precision_score(y_test, y_prob),
            confusion_matrix=cm.tolist(),
            threshold=threshold,
        )
        logger.info(
            "%s → Acc=%.4f Prec=%.4f Rec=%.4f F1=%.4f AUC=%.4f",
            model_name,
            metrics.accuracy,
            metrics.precision,
            metrics.recall,
            metrics.f1_score,
            metrics.roc_auc,
        )
        return metrics

    @staticmethod
    def print_report(metrics: ModelMetrics):
        sep = "─" * 50
        print(f"\n{sep}")
        print(f"  {metrics.model_name}")
        print(sep)
        print(f"  Accuracy  : {metrics.accuracy:.4f}")
        print(f"  Precision : {metrics.precision:.4f}")
        print(f"  Recall    : {metrics.recall:.4f}")
        print(f"  F1-Score  : {metrics.f1_score:.4f}")
        print(f"  ROC-AUC   : {metrics.roc_auc:.4f}")
        print(f"  PR-AUC    : {metrics.pr_auc:.4f}")
        cm = metrics.confusion_matrix
        if cm:
            print(f"  Confusion Matrix:")
            print(f"    TN={cm[0][0]:>6}  FP={cm[0][1]:>6}")
            print(f"    FN={cm[1][0]:>6}  TP={cm[1][1]:>6}")
        print(sep)

    def compare_models(self, metrics_list: list[ModelMetrics]) -> dict:
        """Return a comparison table dict sorted by F1-Score."""
        rows = sorted(
            [m.to_dict() for m in metrics_list],
            key=lambda x: x["f1_score"],
            reverse=True,
        )
        return {"models": rows, "best_model": rows[0]["model_name"] if rows else None}
