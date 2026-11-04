"""
Unit tests for the prediction service.
Run with: pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import pytest

from models.rule_engine import RuleBasedDetector
from models.schemas import PredictionRequest
from services.prediction_service import PredictionService


class TestRuleEngine:
    def setup_method(self):
        self.engine = RuleBasedDetector()

    def test_low_amount_legitimate(self):
        pred, conf = self.engine.predict({"amount": 50.0, "merchant_category": "Groceries"})
        assert pred == 0

    def test_very_high_amount_fraud(self):
        pred, conf = self.engine.predict({"amount": 15000.0})
        assert pred == 1
        assert conf >= 0.5

    def test_high_risk_category(self):
        pred, conf = self.engine.predict({
            "amount": 5001.0,
            "merchant_category": "Gambling",
        })
        assert pred == 1

    def test_unknown_device_raises_score(self):
        _, conf_known = self.engine.predict({"amount": 100, "device_type": "Mobile"})
        _, conf_unknown = self.engine.predict({"amount": 100, "device_type": "Unknown"})
        assert conf_unknown > conf_known


class TestPredictionService:
    def setup_method(self):
        self.service = PredictionService()
        # Don't load real models – test with fallback behaviour
        self.service.models_loaded = True

    def test_predict_returns_valid_response(self):
        request = PredictionRequest(
            transaction_id="TXN-TEST-001",
            amount=150.0,
            merchant="Amazon",
            merchant_category="Electronics",
            user_age=35,
            device_type="Mobile",
        )
        response = self.service.predict(request)
        assert response.final_prediction in (0, 1)
        assert 0.0 <= response.final_confidence <= 1.0
        assert response.inference_time_ms >= 0
        assert response.model_version == "v1.0"

    def test_high_amount_increases_fraud_probability(self):
        low_req = PredictionRequest(transaction_id="T1", amount=50.0)
        high_req = PredictionRequest(transaction_id="T2", amount=15000.0)

        low_resp  = self.service.predict(low_req)
        high_resp = self.service.predict(high_req)

        assert high_resp.rule_based_confidence >= low_resp.rule_based_confidence
