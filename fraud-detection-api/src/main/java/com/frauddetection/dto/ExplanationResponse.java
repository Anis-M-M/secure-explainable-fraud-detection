package com.frauddetection.dto;

import com.frauddetection.model.Explanation;
import lombok.Builder;
import lombok.Value;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Value
@Builder
public class ExplanationResponse {
    Long id;
    Long predictionId;
    String modelType;
    String explanationType;
    String featureImportanceJson;
    String topFeatures;
    String explanationHtml;
    BigDecimal stabilityScore;
    LocalDateTime createdAt;

    public static ExplanationResponse from(Explanation explanation) {
        return ExplanationResponse.builder()
                .id(explanation.getId())
                .predictionId(explanation.getPrediction() != null ? explanation.getPrediction().getId() : null)
                .modelType(explanation.getModelType())
                .explanationType(explanation.getExplanationType())
                .featureImportanceJson(explanation.getFeatureImportanceJson())
                .topFeatures(explanation.getTopFeatures())
                .explanationHtml(explanation.getExplanationHtml())
                .stabilityScore(explanation.getStabilityScore())
                .createdAt(explanation.getCreatedAt())
                .build();
    }
}
