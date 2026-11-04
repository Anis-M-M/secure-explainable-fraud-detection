"""
SHAP explainer for fraud detection models.
Generates feature attribution values for individual predictions.
"""
import logging
import numpy as np
import shap

logger = logging.getLogger(__name__)

FEATURE_NAMES = [
    "amount", "user_age", "account_balance", "risk_score",
    "ip_address_flag", "previous_fraudulent_activity",
    "daily_transaction_count", "avg_transaction_amount_7d",
    "failed_transaction_count_7d", "card_age", "transaction_distance",
    "is_weekend", "merchant_category_enc", "device_type_enc",
    "transaction_type_enc", "authentication_method_enc",
]


class SHAPExplainer:
    def __init__(self, model=None):
        self.model = model
        self.explainer = None

    def fit(self, X_background: np.ndarray):
        """Fit explainer on background dataset samples."""
        if self.model is None:
            return
        self.explainer = shap.Explainer(self.model.predict_proba, X_background)
        logger.info("SHAP explainer fitted on %d background samples", len(X_background))

    def explain(self, X: np.ndarray) -> dict:
        """
        Generate SHAP explanation for a single instance.
        Returns dict with feature importances.
        """
        if self.explainer is None:
            logger.warning("SHAP explainer not fitted, returning empty explanation")
            return {}

        shap_values = self.explainer(X)
        values = shap_values.values[0]
        # SHAP with predict_proba returns shape (n_features, n_classes) — take fraud class (index 1)
        if values.ndim == 2:
            values = values[:, 1]

        result = {
            "shap_values": dict(zip(FEATURE_NAMES, [round(float(v), 6) for v in values])),
            "base_value": round(float(np.atleast_1d(shap_values.base_values[0])[-1]), 6),
            "top_features": self._get_top_features(values),
        }
        return result

    def _get_top_features(self, shap_values: np.ndarray, top_n: int = 3) -> list:
        """Return top N features by absolute SHAP value."""
        vals = shap_values if shap_values.ndim == 1 else shap_values[:, 1]
        indices = np.argsort(np.abs(vals))[::-1][:top_n]
        return [
            {
                "feature": FEATURE_NAMES[i],
                "shap_value": round(float(vals[i]), 6),
                "impact": "HIGH" if abs(vals[i]) > 0.1 else "MEDIUM",
            }
            for i in indices
        ]
