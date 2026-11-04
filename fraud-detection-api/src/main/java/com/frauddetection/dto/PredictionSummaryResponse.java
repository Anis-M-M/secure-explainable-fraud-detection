package com.frauddetection.dto;

import com.frauddetection.model.FraudPrediction;
import lombok.Builder;
import lombok.Value;

import java.math.BigDecimal;

@Value
@Builder
public class PredictionSummaryResponse {
    Long id;
    Integer finalPrediction;
    BigDecimal finalConfidence;
    String modelVersion;
    Integer inferenceTimeMs;

    public static PredictionSummaryResponse from(FraudPrediction prediction) {
        if (prediction == null) {
            return null;
        }

        return PredictionSummaryResponse.builder()
                .id(prediction.getId())
                .finalPrediction(prediction.getFinalPrediction())
                .finalConfidence(prediction.getFinalConfidence())
                .modelVersion(prediction.getModelVersion())
                .inferenceTimeMs(prediction.getInferenceTimeMs())
                .build();
    }
}
