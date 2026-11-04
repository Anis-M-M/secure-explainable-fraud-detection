"""
LIME explainer for fraud detection models.
Provides local interpretable model-agnostic explanations.
"""
import logging
import numpy as np
import lime
import lime.lime_tabular

logger = logging.getLogger(__name__)

FEATURE_NAMES = ["amount", "user_age", "merchant_category", "device_type"]
CLASS_NAMES = ["legitimate", "fraud"]


class LIMEExplainer:
    def __init__(self, model=None):
        self.model = model
        self.explainer = None

    def fit(self, X_train: np.ndarray):
        """Fit LIME explainer on training data."""
        if self.model is None:
            return
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_train,
            feature_names=FEATURE_NAMES,
            class_names=CLASS_NAMES,
            mode="classification",
        )
        logger.info("LIME explainer fitted on %d training samples", len(X_train))

    def explain(self, X: np.ndarray, num_features: int = 4) -> dict:
        """
        Generate LIME explanation for a single instance.
        Returns dict with local feature weights.
        """
        if self.explainer is None:
            logger.warning("LIME explainer not fitted, returning empty explanation")
            return {}

        exp = self.explainer.explain_instance(
            X[0],
            self.model.predict_proba,
            num_features=num_features,
            num_samples=500,
        )

        local_weights = dict(exp.as_list())
        top_features = [
            {
                "feature": feat.split(" ")[0],
                "weight": round(float(weight), 6),
                "contribution": "Increases fraud probability" if weight > 0 else "Decreases fraud probability",
            }
            for feat, weight in exp.as_list()
        ]

        return {
            "local_weights": {k: round(float(v), 6) for k, v in local_weights.items()},
            "top_features": top_features,
            "intercept": round(float(exp.intercept[1]), 6),
            "score": round(float(exp.score), 4),
        }
