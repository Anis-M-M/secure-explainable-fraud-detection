"""
Prediction service: orchestrates all models, builds ensemble, and
stores SHAP/LIME explainers for on-demand explanation generation.
"""
import logging
import os
import time

import joblib
import numpy as np

from models.rule_engine import RuleBasedDetector
from models.schemas import PredictionRequest, PredictionResponse
from explainability.shap_explainer import SHAPExplainer
from explainability.lime_explainer import LIMEExplainer
from explainability.stability_analyzer import StabilityAnalyzer
from utils.preprocessing import Preprocessor
from config import settings

logger = logging.getLogger(__name__)

MODEL_VERSION = "v1.0"
SAVED_DIR = settings.MODEL_DIR

# Ensemble weights (Rule, LR, XGB, NN)
WEIGHTS = (0.15, 0.20, 0.35, 0.30)


class PredictionService:
    def __init__(self):
        self.rule_engine = RuleBasedDetector()
        self.preprocessor: Preprocessor = None
        self.lr_model = None
        self.xgb_model = None
        self.nn_model = None
        self.shap_explainer: SHAPExplainer = None
        self.lime_explainer: LIMEExplainer = None
        self.stability_analyzer: StabilityAnalyzer = None
        self.models_loaded = False
        self._metrics: dict = {}

    # loading

    def load_models(self):
        logger.info("Loading ML models from %s", SAVED_DIR)

        prep_path = os.path.join(SAVED_DIR, "preprocessor.pkl")
        if os.path.exists(prep_path):
            self.preprocessor = Preprocessor.load(prep_path)
        else:
            logger.warning("Preprocessor not found – using default (untrained) preprocessor")
            self.preprocessor = Preprocessor()

        self.lr_model = self._load_sklearn(os.path.join(SAVED_DIR, "lr_model.pkl"), "LR")
        self.xgb_model = self._load_sklearn(os.path.join(SAVED_DIR, "xgb_model.pkl"), "XGB")
        self.nn_model = self._load_keras(os.path.join(SAVED_DIR, "nn_model"))

        # Wire explainers to the best sklearn model (XGBoost)
        if self.xgb_model is not None:
            self.shap_explainer = SHAPExplainer(model=self.xgb_model)
            self.lime_explainer = LIMEExplainer(model=self.xgb_model)
            # Fit on a small synthetic background if real background not stored
            background = self._synthetic_background(n=100)
            self.shap_explainer.fit(background)
            self.lime_explainer.fit(background)
            self.stability_analyzer = StabilityAnalyzer(
                shap_explainer=self.shap_explainer,
                lime_explainer=self.lime_explainer,
                n_perturbations=100,
            )

        self.models_loaded = True
        logger.info("All models loaded")

    # prediction

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        start = time.time()

        features = request.dict()

        # Rule-based
        rb_pred, rb_conf = self.rule_engine.predict(features)

        # Transform to numeric
        if self.preprocessor.is_fitted:
            X = self.preprocessor.transform_single(features)
        else:
            X = self._fallback_vector(features)

        # LR
        lr_pred, lr_prob = self._sklearn_predict(self.lr_model, X)

        # XGBoost
        xgb_pred, xgb_prob = self._sklearn_predict(self.xgb_model, X)

        # Neural Network
        nn_pred, nn_prob = self._nn_predict(self.nn_model, X, features)

        # Weighted ensemble
        ensemble = (
            rb_conf * WEIGHTS[0]
            + lr_prob * WEIGHTS[1]
            + xgb_prob * WEIGHTS[2]
            + nn_prob * WEIGHTS[3]
        )
        final_pred = int(ensemble >= 0.5)
        final_conf = round(ensemble, 4)

        return PredictionResponse(
            rule_based_prediction=rb_pred,
            rule_based_confidence=rb_conf,
            logistic_regression_prediction=lr_pred,
            logistic_regression_probability=lr_prob,
            xgboost_prediction=xgb_pred,
            xgboost_probability=xgb_prob,
            neural_network_prediction=nn_pred,
            neural_network_probability=nn_prob,
            final_prediction=final_pred,
            final_confidence=final_conf,
            model_version=MODEL_VERSION,
            inference_time_ms=int((time.time() - start) * 1000),
        )

    # explanation endpoints

    def explain_shap(self, request: PredictionRequest) -> dict:
        if self.shap_explainer is None:
            return {"error": "SHAP explainer not available"}
        X = self._features_to_vector(request)
        return self.shap_explainer.explain(X)

    def explain_lime(self, request: PredictionRequest) -> dict:
        if self.lime_explainer is None:
            return {"error": "LIME explainer not available"}
        X = self._features_to_vector(request)
        return self.lime_explainer.explain(X)

    def explain_stability(self, request: PredictionRequest) -> dict:
        if self.stability_analyzer is None:
            return {"error": "Stability analyzer not available"}
        X = self._features_to_vector(request)
        return self.stability_analyzer.analyze(X)

    def get_metrics(self) -> dict:
        return self._metrics

    # helpers

    def _features_to_vector(self, request: PredictionRequest) -> np.ndarray:
        features = request.dict()
        if self.preprocessor.is_fitted:
            return self.preprocessor.transform_single(features)
        return self._fallback_vector(features)

    @staticmethod
    def _load_sklearn(path: str, name: str):
        if os.path.exists(path):
            data = joblib.load(path)
            logger.info("%s model loaded from %s", name, path)
            return data["model"]
        logger.warning("%s model not found at %s", name, path)
        return None

    @staticmethod
    def _load_keras(path: str):
        if os.path.exists(path):
            try:
                import tensorflow as tf
                model = tf.keras.models.load_model(path)
                logger.info("Neural Network loaded from %s", path)
                return model
            except Exception as e:
                logger.error("Failed to load NN: %s", e)
        else:
            logger.warning("Neural Network model not found at %s", path)
        return None

    @staticmethod
    def _sklearn_predict(model, X: np.ndarray) -> tuple[int, float]:
        if model is None:
            return 0, 0.5
        prob = float(model.predict_proba(X)[0][1])
        return int(prob >= 0.5), round(prob, 4)

    @staticmethod
    def _nn_predict(model, X: np.ndarray, features: dict) -> tuple[int, float]:
        if model is None:
            amount = float(features.get("amount") or 0)
            prob = min(amount / 20_000.0, 0.95)
            return int(prob >= 0.5), round(prob, 4)
        prob = float(model.predict(X, verbose=0)[0][0])
        return int(prob >= 0.5), round(prob, 4)

    @staticmethod
    def _fallback_vector(features: dict) -> np.ndarray:
        return np.array([[
            float(features.get("amount") or 0),
            float(features.get("user_age") or 35),
            0.0,
            0.0,
        ]], dtype=float)

    @staticmethod
    def _synthetic_background(n: int = 100) -> np.ndarray:
        """Small synthetic background dataset for SHAP/LIME fitting."""
        rng = np.random.default_rng(0)
        return np.column_stack([
            rng.exponential(150, n),   # amount
            rng.integers(18, 75, n),   # user_age
            rng.integers(0, 8, n),     # merchant_category_enc
            rng.integers(0, 4, n),     # device_type_enc
        ]).astype(float)
