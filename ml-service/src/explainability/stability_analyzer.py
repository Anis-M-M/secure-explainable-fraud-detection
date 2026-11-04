"""
Stability analyzer: measures consistency of SHAP and LIME explanations
under perturbations. Key metric for RQ2 of the research.
"""
import logging
import numpy as np
from scipy.stats import spearmanr

logger = logging.getLogger(__name__)


class StabilityAnalyzer:
    """Evaluate explanation stability via perturbation-based analysis."""

    def __init__(self, shap_explainer=None, lime_explainer=None, n_perturbations: int = 100):
        self.shap_explainer = shap_explainer
        self.lime_explainer = lime_explainer
        self.n_perturbations = n_perturbations

    def analyze(self, X: np.ndarray, noise_std: float = 0.05) -> dict:
        """
        Perturb the input n_perturbations times and measure feature ranking consistency.
        Returns stability report dict.
        """
        shap_rankings = []
        lime_rankings = []

        for _ in range(self.n_perturbations):
            X_perturbed = X + np.random.normal(0, noise_std, X.shape)

            if self.shap_explainer and self.shap_explainer.explainer:
                shap_result = self.shap_explainer.explain(X_perturbed)
                if shap_result:
                    vals = list(shap_result.get("shap_values", {}).values())
                    shap_rankings.append(np.argsort(np.abs(vals))[::-1].tolist())

            if self.lime_explainer and self.lime_explainer.explainer:
                lime_result = self.lime_explainer.explain(X_perturbed)
                if lime_result:
                    weights = list(lime_result.get("local_weights", {}).values())
                    lime_rankings.append(np.argsort(np.abs(weights))[::-1].tolist())

        stability_score = self._compute_ranking_stability(shap_rankings or lime_rankings)
        agreement = self._compute_shap_lime_agreement(shap_rankings, lime_rankings)

        return {
            "perturbation_count": self.n_perturbations,
            "stability_score": round(stability_score, 4),
            "shap_lime_agreement": round(agreement, 4),
            "recommendations": self._generate_recommendations(stability_score, agreement),
        }

    def _compute_ranking_stability(self, rankings: list) -> float:
        """Average pairwise Spearman correlation of feature rankings."""
        if len(rankings) < 2:
            return 0.0
        correlations = []
        for i in range(min(len(rankings), 20)):  # Sample 20 pairs for speed
            for j in range(i + 1, min(len(rankings), 20)):
                corr, _ = spearmanr(rankings[i], rankings[j])
                correlations.append(corr)
        return float(np.mean(correlations)) if correlations else 0.0

    def _compute_shap_lime_agreement(self, shap_rankings: list, lime_rankings: list) -> float:
        """Measure agreement between SHAP and LIME on top feature rankings."""
        if not shap_rankings or not lime_rankings:
            return 0.0
        shap_mean = np.mean(shap_rankings, axis=0) if len(shap_rankings) > 1 else shap_rankings[0]
        lime_mean = np.mean(lime_rankings, axis=0) if len(lime_rankings) > 1 else lime_rankings[0]
        corr, _ = spearmanr(shap_mean, lime_mean)
        return float(corr)

    def _generate_recommendations(self, stability: float, agreement: float) -> list:
        recs = []
        if stability > 0.85:
            recs.append("Explanations are highly stable under perturbations")
        elif stability > 0.70:
            recs.append("Explanations show moderate stability")
        else:
            recs.append("Low stability detected - consider model retraining or feature engineering")

        if agreement > 0.9:
            recs.append("SHAP and LIME show strong agreement on feature rankings")
        elif agreement > 0.7:
            recs.append("SHAP and LIME show moderate agreement")
        else:
            recs.append("SHAP and LIME disagree on feature importance - investigate model behavior")
        return recs
