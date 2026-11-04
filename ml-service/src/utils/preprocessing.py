"""
Feature engineering and preprocessing pipeline.

Transforms raw transaction DataFrames into numeric feature matrices
ready for sklearn / XGBoost / TensorFlow models.
"""
import logging
import os
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE

logger = logging.getLogger(__name__)

NUMERIC_FEATURES = [
    "amount", "user_age", "account_balance", "risk_score",
    "ip_address_flag", "previous_fraudulent_activity",
    "daily_transaction_count", "avg_transaction_amount_7d",
    "failed_transaction_count_7d", "card_age", "transaction_distance",
    "is_weekend",
]
CATEGORICAL_FEATURES = ["merchant_category", "device_type", "transaction_type", "authentication_method"]
LABEL_COLUMN = "is_fraud"

ALL_FEATURES = NUMERIC_FEATURES + [f"{c}_enc" for c in CATEGORICAL_FEATURES]


class Preprocessor:
    """Fit-once, transform-many preprocessor."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders: dict[str, LabelEncoder] = {
            col: LabelEncoder() for col in CATEGORICAL_FEATURES
        }
        self.is_fitted = False
        # Map category → integer (for use by models at inference time)
        self.encoding_maps: dict[str, dict] = {}


    def fit_transform(
        self,
        df: pd.DataFrame,
        apply_smote: bool = True,
        smote_random_state: int = 42,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Fit on training data and return (X, y).
        Optionally applies SMOTE to address class imbalance.
        """
        X, y = self._encode_and_scale(df, fit=True)
        logger.info("Class distribution before SMOTE: %s", np.bincount(y.astype(int)))

        if apply_smote and y.sum() > 0:
            smote = SMOTE(random_state=smote_random_state)
            X, y = smote.fit_resample(X, y)
            logger.info("After SMOTE: %s", np.bincount(y.astype(int)))

        self.is_fitted = True
        return X, y

    def transform(self, df: pd.DataFrame) -> tuple[np.ndarray, Optional[np.ndarray]]:
        """Transform new data using already-fitted encoders/scaler."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before calling transform()")
        return self._encode_and_scale(df, fit=False)

    def transform_single(self, features: dict) -> np.ndarray:
        """
        Convert a raw transaction dict to a feature vector.
        Used at inference time by the prediction service.
        """
        numeric_defaults = {
            "amount": 0, "user_age": 35, "account_balance": 0, "risk_score": 0.5,
            "ip_address_flag": 0, "previous_fraudulent_activity": 0,
            "daily_transaction_count": 1, "avg_transaction_amount_7d": 0,
            "failed_transaction_count_7d": 0, "card_age": 12,
            "transaction_distance": 0, "is_weekend": 0,
        }
        numeric_vals = [float(features.get(col) or default)
                        for col, default in numeric_defaults.items()]

        cat_vals = []
        for col in CATEGORICAL_FEATURES:
            val = features.get(col) or "Unknown"
            enc = float(self.encoding_maps.get(col, {}).get(val, 0))
            cat_vals.append(enc)

        raw = np.array([numeric_vals + cat_vals], dtype=float)
        return self.scaler.transform(raw)

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(
            {
                "scaler": self.scaler,
                "label_encoders": self.label_encoders,
                "encoding_maps": self.encoding_maps,
                "is_fitted": self.is_fitted,
            },
            path,
        )
        logger.info("Preprocessor saved to %s", path)

    @classmethod
    def load(cls, path: str) -> "Preprocessor":
        data = joblib.load(path)
        p = cls()
        p.scaler = data["scaler"]
        p.label_encoders = data["label_encoders"]
        p.encoding_maps = data["encoding_maps"]
        p.is_fitted = data["is_fitted"]
        logger.info("Preprocessor loaded from %s", path)
        return p


    def _encode_and_scale(
        self, df: pd.DataFrame, fit: bool
    ) -> tuple[np.ndarray, Optional[np.ndarray]]:
        df = df.copy()

        # Fill nulls
        numeric_defaults = {
            "amount": 0, "user_age": 35, "account_balance": 0, "risk_score": 0.5,
            "ip_address_flag": 0, "previous_fraudulent_activity": 0,
            "daily_transaction_count": 1, "avg_transaction_amount_7d": 0,
            "failed_transaction_count_7d": 0, "card_age": 12,
            "transaction_distance": 0, "is_weekend": 0,
        }
        for col, default in numeric_defaults.items():
            if col in df.columns:
                df[col] = df[col].fillna(default)
            else:
                df[col] = default
        for col in CATEGORICAL_FEATURES:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown")
            else:
                df[col] = "Unknown"

        # Encode categoricals
        for col in CATEGORICAL_FEATURES:
            enc_col = f"{col}_enc"
            if fit:
                df[enc_col] = self.label_encoders[col].fit_transform(df[col])
                self.encoding_maps[col] = {
                    label: int(code)
                    for code, label in enumerate(self.label_encoders[col].classes_)
                }
            else:
                known = set(self.label_encoders[col].classes_)
                df[col] = df[col].apply(lambda x: x if x in known else "Unknown")
                df[enc_col] = self.label_encoders[col].transform(df[col])

        # Assemble feature matrix
        feature_cols = NUMERIC_FEATURES + [f"{c}_enc" for c in CATEGORICAL_FEATURES]
        X_raw = df[feature_cols].values.astype(float)

        X = self.scaler.fit_transform(X_raw) if fit else self.scaler.transform(X_raw)

        y = df[LABEL_COLUMN].values.astype(float) if LABEL_COLUMN in df.columns else None
        return X, y
