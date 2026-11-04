"""
Rule-based fraud detection engine.
Uses hand-crafted heuristics as a baseline model.
"""
import logging

logger = logging.getLogger(__name__)

# High-risk merchant categories
HIGH_RISK_CATEGORIES = {
    "Gambling", "Cryptocurrency", "Wire Transfer", "Money Order",
    "Pawn Shop", "Check Cashing"
}

# High-risk device types
HIGH_RISK_DEVICES = {"Unknown", "Emulator", "Rooted"}

AMOUNT_THRESHOLD_HIGH = 5000.0
AMOUNT_THRESHOLD_VERY_HIGH = 10000.0


class RuleBasedDetector:
    """Simple rule engine that flags suspicious transactions."""

    def predict(self, features: dict) -> tuple[int, float]:
        """
        Returns (prediction, confidence).
        prediction: 1=fraud, 0=legitimate
        confidence: float in [0, 1]
        """
        score = 0.0
        reasons = []

        amount = features.get("amount", 0)
        category = features.get("merchant_category", "")
        device = features.get("device_type", "")
        user_age = features.get("user_age")

        # Rule 1: Very high amount
        if amount > AMOUNT_THRESHOLD_VERY_HIGH:
            score += 0.5
            reasons.append("very_high_amount")
        elif amount > AMOUNT_THRESHOLD_HIGH:
            score += 0.3
            reasons.append("high_amount")

        # Rule 2: High-risk merchant category
        if category in HIGH_RISK_CATEGORIES:
            score += 0.4
            reasons.append("high_risk_category")

        # Rule 3: High-risk device
        if device in HIGH_RISK_DEVICES:
            score += 0.3
            reasons.append("high_risk_device")

        # Rule 4: Missing user age (anonymous transaction)
        if user_age is None:
            score += 0.1
            reasons.append("missing_user_age")

        # Normalize to [0, 1]
        confidence = min(score, 1.0)
        prediction = 1 if confidence >= 0.5 else 0

        if reasons:
            logger.debug("Rule flags: %s (score=%.2f)", reasons, confidence)

        return prediction, round(confidence, 4)
