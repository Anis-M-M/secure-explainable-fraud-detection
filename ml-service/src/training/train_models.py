"""
Model training pipeline.

Usage:
    python -m training.train_models [--data-path path/to/creditcard.csv]

Trains:
  - Logistic Regression
  - XGBoost
  - Neural Network (TensorFlow/Keras)

Saves all artefacts to models/saved/.
"""
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import xgboost as xgb

from utils.data_loader import DataLoader, LABEL_COLUMN
from utils.preprocessing import Preprocessor
from training.evaluate import Evaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAVED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models", "saved")


def train_logistic_regression(X_train, y_train) -> LogisticRegression:
    logger.info("Training Logistic Regression...")
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        random_state=42,
    )
    model.fit(X_train, y_train)
    logger.info("LR training complete")
    return model


def train_xgboost(X_train, y_train) -> xgb.XGBClassifier:
    logger.info("Training XGBoost...")
    fraud_count = int(y_train.sum())
    legit_count = int(len(y_train) - fraud_count)
    scale_pos = legit_count / max(fraud_count, 1)

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        eval_metric="aucpr",
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_train, y_train)],
        verbose=False,
    )
    logger.info("XGBoost training complete")
    return model


def train_neural_network(X_train, y_train, X_val=None, y_val=None):
    """Train a Keras binary classification network."""
    try:
        import tensorflow as tf
        from tensorflow import keras

        logger.info("Training Neural Network (TensorFlow %s)...", tf.__version__)

        n_features = X_train.shape[1]

        model = keras.Sequential([
            keras.layers.Input(shape=(n_features,)),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation="relu"),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(1, activation="sigmoid"),
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-3),
            loss="binary_crossentropy",
            metrics=["AUC", "Precision", "Recall"],
        )

        # Class weights for imbalance (before SMOTE on raw y)
        fraud_w = len(y_train) / (2 * max(y_train.sum(), 1))
        legit_w = len(y_train) / (2 * max(len(y_train) - y_train.sum(), 1))
        class_weight = {0: legit_w, 1: fraud_w}

        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss" if X_val is not None else "loss",
                patience=10,
                restore_best_weights=True,
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss" if X_val is not None else "loss",
                factor=0.5,
                patience=5,
            ),
        ]

        validation_data = (X_val, y_val) if X_val is not None else None

        model.fit(
            X_train,
            y_train,
            epochs=100,
            batch_size=256,
            validation_data=validation_data,
            class_weight=class_weight,
            callbacks=callbacks,
            verbose=1,
        )
        logger.info("Neural Network training complete")
        return model

    except ImportError:
        logger.error("TensorFlow not installed – skipping Neural Network training")
        return None


def save_artefacts(lr_model, xgb_model, nn_model, preprocessor):
    os.makedirs(SAVED_DIR, exist_ok=True)

    joblib.dump({"model": lr_model}, os.path.join(SAVED_DIR, "lr_model.pkl"))
    logger.info("Saved LR model")

    joblib.dump({"model": xgb_model}, os.path.join(SAVED_DIR, "xgb_model.pkl"))
    logger.info("Saved XGBoost model")

    if nn_model is not None:
        nn_path = os.path.join(SAVED_DIR, "nn_model")
        nn_model.save(nn_path)
        logger.info("Saved Neural Network to %s", nn_path)

    preprocessor.save(os.path.join(SAVED_DIR, "preprocessor.pkl"))


def main(data_path: str = None):
    # 1. Load data
    loader = DataLoader(data_path=data_path)
    df = loader.load()
    train_df, val_df, test_df = loader.split(df)

    # 2. Preprocess
    preprocessor = Preprocessor()
    X_train, y_train = preprocessor.fit_transform(train_df, apply_smote=True)
    X_val, y_val = preprocessor.transform(val_df)
    X_test, y_test = preprocessor.transform(test_df)

    # 3. Train models
    lr_model = train_logistic_regression(X_train, y_train)
    xgb_model = train_xgboost(X_train, y_train)
    nn_model = train_neural_network(X_train, y_train, X_val, y_val)

    # 4. Evaluate all models on test set
    evaluator = Evaluator()
    print("\n" + "=" * 60)
    print("TEST SET EVALUATION")
    print("=" * 60)

    for name, model in [("Logistic Regression", lr_model), ("XGBoost", xgb_model)]:
        metrics = evaluator.evaluate(model, X_test, y_test, model_name=name)
        evaluator.print_report(metrics)

    if nn_model is not None:
        y_prob_nn = nn_model.predict(X_test, verbose=0).ravel()
        metrics = evaluator.evaluate_from_probs(y_prob_nn, y_test, model_name="Neural Network")
        evaluator.print_report(metrics)

    # 5. Save artefacts
    save_artefacts(lr_model, xgb_model, nn_model, preprocessor)
    logger.info("All models saved to %s", SAVED_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train fraud detection models")
    parser.add_argument("--data-path", default=None, help="Path to creditcard.csv")
    args = parser.parse_args()
    main(data_path=args.data_path)
