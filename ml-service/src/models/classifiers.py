"""
Logistic Regression and XGBoost classifiers for fraud detection.
"""
import os
import logging
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import xgboost as xgb

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = ["amount", "user_age", "merchant_category_enc", "device_type_enc"]


def build_feature_vector(features: dict, encoders: dict) -> np.ndarray:
    """Convert raw transaction features to a numeric feature vector."""
    amount = float(features.get("amount", 0))
    user_age = float(features.get("user_age") or 35)

    category = features.get("merchant_category") or "Unknown"
    device = features.get("device_type") or "Unknown"

    cat_enc = encoders.get("merchant_category", {}).get(category, 0)
    dev_enc = encoders.get("device_type", {}).get(device, 0)

    return np.array([[amount, user_age, cat_enc, dev_enc]], dtype=float)


class LogisticRegressionModel:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.pipeline: Pipeline = None
        self.encoders: dict = {}

    def load(self):
        if self.model_path and os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.pipeline = data["pipeline"]
            self.encoders = data.get("encoders", {})
            logger.info("Logistic Regression model loaded from %s", self.model_path)
        else:
            logger.warning("LR model not found, using untrained placeholder")
            self.pipeline = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(class_weight="balanced", max_iter=1000))
            ])

    def predict(self, features: dict) -> tuple[int, float]:
        if self.pipeline is None:
            return 0, 0.5
        X = build_feature_vector(features, self.encoders)
        prob = self.pipeline.predict_proba(X)[0][1]
        pred = int(prob >= 0.5)
        return pred, round(float(prob), 4)


class XGBoostModel:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model: xgb.XGBClassifier = None
        self.encoders: dict = {}

    def load(self):
        if self.model_path and os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.encoders = data.get("encoders", {})
            logger.info("XGBoost model loaded from %s", self.model_path)
        else:
            logger.warning("XGBoost model not found, using default")
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                scale_pos_weight=10,
                eval_metric="logloss",
                use_label_encoder=False,
            )

    def predict(self, features: dict) -> tuple[int, float]:
        if self.model is None:
            return 0, 0.5
        X = build_feature_vector(features, self.encoders)
        prob = self.model.predict_proba(X)[0][1]
        pred = int(prob >= 0.5)
        return pred, round(float(prob), 4)
