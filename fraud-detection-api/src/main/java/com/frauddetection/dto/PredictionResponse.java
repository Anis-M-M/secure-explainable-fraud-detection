package com.frauddetection.dto;

import com.frauddetection.model.FraudPrediction;
import lombok.Builder;
import lombok.Value;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Value
@Builder
public class PredictionResponse {
    Long id;
    Long transactionId;
    Integer ruleBasedPrediction;
    BigDecimal ruleBasedConfidence;
    Integer logisticRegressionPrediction;
    BigDecimal logisticRegressionProbability;
    Integer xgboostPrediction;
    BigDecimal xgboostProbability;
    Integer neuralNetworkPrediction;
    BigDecimal neuralNetworkProbability;
    Integer finalPrediction;
    BigDecimal finalConfidence;
    String modelVersion;
    Integer inferenceTimeMs;
    LocalDateTime createdAt;

    public static PredictionResponse from(FraudPrediction prediction) {
        return PredictionResponse.builder()
                .id(prediction.getId())
                .transactionId(prediction.getTransaction() != null ? prediction.getTransaction().getId() : null)
                .ruleBasedPrediction(prediction.getRuleBasedPrediction())
                .ruleBasedConfidence(prediction.getRuleBasedConfidence())
                .logisticRegressionPrediction(prediction.getLogisticRegressionPrediction())
                .logisticRegressionProbability(prediction.getLogisticRegressionProbability())
                .xgboostPrediction(prediction.getXgboostPrediction())
                .xgboostProbability(prediction.getXgboostProbability())
                .neuralNetworkPrediction(prediction.getNeuralNetworkPrediction())
                .neuralNetworkProbability(prediction.getNeuralNetworkProbability())
                .finalPrediction(prediction.getFinalPrediction())
                .finalConfidence(prediction.getFinalConfidence())
                .modelVersion(prediction.getModelVersion())
                .inferenceTimeMs(prediction.getInferenceTimeMs())
                .createdAt(prediction.getCreatedAt())
                .build();
    }
}
