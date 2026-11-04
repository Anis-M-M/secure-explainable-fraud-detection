"""
Data loader for fraud detection dataset.

Supports:
  - Kaggle Credit Card Fraud dataset (creditcard.csv)
  - Synthetic data generation for testing / local dev
"""
import logging
import os

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

try:
    import kagglehub
    KAGGLEHUB_AVAILABLE = True
except ImportError:
    KAGGLEHUB_AVAILABLE = False

logger = logging.getLogger(__name__)

# Column names when using the project's custom feature set
CUSTOM_FEATURES = [
    "amount", "user_age", "merchant_category", "device_type",
    "merchant", "user_location",
]
LABEL_COLUMN = "is_fraud"

# Kaggle dataset column mapping
KAGGLE_AMOUNT_COL = "Amount"
KAGGLE_LABEL_COL = "Class"
KAGGLE_TIME_COL = "Time"


class DataLoader:
    """Load and split fraud detection data."""

    def __init__(self, data_path: str = None):
        self.data_path = data_path


    def load(self) -> pd.DataFrame:
        """
        Load dataset from disk or fall back to synthetic data.
        Always returns a DataFrame with columns normalised to the
        project's feature schema.
        """
        if self.data_path and os.path.exists(self.data_path):
            ext = os.path.splitext(self.data_path)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(self.data_path)
                logger.info("Loaded %d rows from %s", len(df), self.data_path)
                return self._normalise(df)
            else:
                raise ValueError(f"Unsupported file type: {ext}")

        if KAGGLEHUB_AVAILABLE:
            try:
                logger.info("Downloading dataset from Kaggle...")
                path = kagglehub.dataset_download("samayashar/fraud-detection-transactions-dataset")
                logger.info("Kaggle dataset downloaded to: %s", path)
                # Find the CSV file in the downloaded path
                for fname in os.listdir(path):
                    if fname.endswith(".csv"):
                        csv_path = os.path.join(path, fname)
                        df = pd.read_csv(csv_path)
                        logger.info("Loaded %d rows from Kaggle dataset (%s)", len(df), fname)
                        return self._normalise(df)
            except Exception as e:
                logger.warning("Kaggle download failed: %s – falling back to synthetic data", e)

        logger.warning("Dataset not found at '%s' – generating synthetic data", self.data_path)
        return self._generate_synthetic(n_samples=10_000, fraud_rate=0.02)

    def split(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Return (train_df, val_df, test_df) with stratified splits.
        """
        y = df[LABEL_COLUMN]
        train_val, test = train_test_split(
            df, test_size=test_size, stratify=y, random_state=random_state
        )
        relative_val = val_size / (1 - test_size)
        train, val = train_test_split(
            train_val,
            test_size=relative_val,
            stratify=train_val[LABEL_COLUMN],
            random_state=random_state,
        )
        logger.info(
            "Split sizes – train: %d | val: %d | test: %d", len(train), len(val), len(test)
        )
        return train, val, test


    def _normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map Kaggle or custom CSV columns to the project schema."""
        # samayashar/fraud-detection-transactions-dataset
        if "Fraud_Label" in df.columns:
            df = df.rename(columns={
                "Transaction_Amount": "amount",
                "Fraud_Label": LABEL_COLUMN,
                "Device_Type": "device_type",
                "Location": "user_location",
                "Merchant_Category": "merchant_category",
                "Account_Balance": "account_balance",
                "Risk_Score": "risk_score",
                "IP_Address_Flag": "ip_address_flag",
                "Previous_Fraudulent_Activity": "previous_fraudulent_activity",
                "Daily_Transaction_Count": "daily_transaction_count",
                "Avg_Transaction_Amount_7d": "avg_transaction_amount_7d",
                "Failed_Transaction_Count_7d": "failed_transaction_count_7d",
                "Card_Age": "card_age",
                "Transaction_Distance": "transaction_distance",
                "Is_Weekend": "is_weekend",
                "Transaction_Type": "transaction_type",
                "Authentication_Method": "authentication_method",
            })
            if "user_age" not in df.columns:
                rng = np.random.default_rng(42)
                df["user_age"] = rng.integers(18, 75, size=len(df))
            if "merchant" not in df.columns:
                df["merchant"] = "Unknown"
        elif KAGGLE_LABEL_COL in df.columns:
            # Standard creditcard.csv (PCA features + Amount + Class)
            df = df.rename(columns={KAGGLE_AMOUNT_COL: "amount", KAGGLE_LABEL_COL: LABEL_COLUMN})
            if KAGGLE_TIME_COL in df.columns:
                df = df.drop(columns=[KAGGLE_TIME_COL])
            for col in ["merchant_category", "device_type", "merchant", "user_location"]:
                if col not in df.columns:
                    df[col] = "Unknown"
            if "user_age" not in df.columns:
                rng = np.random.default_rng(42)
                df["user_age"] = rng.integers(18, 75, size=len(df))
        else:
            if LABEL_COLUMN not in df.columns:
                raise ValueError(f"Label column '{LABEL_COLUMN}' not found in dataset")
        return df

    @staticmethod
    def _generate_synthetic(n_samples: int = 10_000, fraud_rate: float = 0.02) -> pd.DataFrame:
        """
        Generate a synthetic fraud dataset that mimics real-world distributions.
        Used for local development and CI when the real dataset is not available.
        """
        rng = np.random.default_rng(42)
        n_fraud = int(n_samples * fraud_rate)
        n_legit = n_samples - n_fraud

        merchants = ["Amazon", "Walmart", "Target", "Best Buy", "Apple Store", "Unknown"]
        categories = [
            "Electronics", "Groceries", "Travel", "Gambling",
            "Cryptocurrency", "Clothing", "Utilities", "Unknown",
        ]
        devices = ["Mobile", "Desktop", "Tablet", "Unknown"]
        locations = ["New York", "Los Angeles", "Chicago", "Houston", "Unknown"]

        def _sample_rows(n: int, is_fraud: bool) -> pd.DataFrame:
            if is_fraud:
                amounts = rng.exponential(scale=3000, size=n).clip(10, 20_000)
                ages = rng.integers(18, 40, size=n)
                cat_idx = rng.choice([3, 4, 7], size=n)  # high-risk categories
                dev_idx = rng.choice([3], size=n)           # Unknown device
            else:
                amounts = rng.exponential(scale=150, size=n).clip(1, 4_999)
                ages = rng.integers(18, 75, size=n)
                cat_idx = rng.choice([0, 1, 2, 5, 6], size=n)
                dev_idx = rng.choice([0, 1, 2], size=n)

            return pd.DataFrame(
                {
                    "amount": amounts.round(2),
                    "user_age": ages,
                    "merchant": rng.choice(merchants, size=n),
                    "merchant_category": [categories[i] for i in cat_idx],
                    "device_type": [devices[i] for i in dev_idx],
                    "user_location": rng.choice(locations, size=n),
                    LABEL_COLUMN: int(is_fraud),
                }
            )

        df = pd.concat([
            _sample_rows(n_legit, is_fraud=False),
            _sample_rows(n_fraud, is_fraud=True),
        ], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

        logger.info(
            "Generated synthetic dataset: %d total (%d fraud, %d legit)",
            len(df), n_fraud, n_legit,
        )
        return df
