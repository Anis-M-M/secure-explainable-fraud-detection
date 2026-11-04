"""
Neural Network classifier for fraud detection using TensorFlow/Keras.
"""
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)


class NeuralNetworkModel:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self.encoders: dict = {}

    def load(self):
        if self.model_path and os.path.exists(self.model_path):
            try:
                import tensorflow as tf
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info("Neural Network model loaded from %s", self.model_path)
            except Exception as e:
                logger.error("Failed to load NN model: %s", e)
        else:
            logger.warning("Neural Network model not found at path: %s", self.model_path)

    def predict(self, features: dict) -> tuple[int, float]:
        if self.model is None:
            # Fallback: use rule-based hint
            amount = float(features.get("amount", 0))
            prob = min(amount / 20000.0, 0.95)
            return int(prob >= 0.5), round(prob, 4)

        from models.classifiers import build_feature_vector
        X = build_feature_vector(features, self.encoders)
        prob = float(self.model.predict(X, verbose=0)[0][0])
        pred = int(prob >= 0.5)
        return pred, round(prob, 4)
