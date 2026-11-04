package com.frauddetection.dto;

import lombok.Data;

import java.math.BigDecimal;

@Data
public class MLPredictionResponse {
    private Integer ruleBasedPrediction;
    private BigDecimal ruleBasedConfidence;
    private Integer logisticRegressionPrediction;
    private BigDecimal logisticRegressionProbability;
    private Integer xgboostPrediction;
    private BigDecimal xgboostProbability;
    private Integer neuralNetworkPrediction;
    private BigDecimal neuralNetworkProbability;
    private Integer finalPrediction;
    private BigDecimal finalConfidence;
    private String modelVersion;
    private Integer inferenceTimeMs;
}
