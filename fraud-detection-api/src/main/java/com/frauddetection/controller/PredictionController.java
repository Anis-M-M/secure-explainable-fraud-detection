package com.frauddetection.controller;

import com.frauddetection.dto.PredictionResponse;
import com.frauddetection.exception.ResourceNotFoundException;
import com.frauddetection.model.FraudPrediction;
import com.frauddetection.repository.PredictionRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/predictions")
@RequiredArgsConstructor
@Tag(name = "Predictions", description = "Fraud prediction results")
@SecurityRequirement(name = "bearerAuth")
public class PredictionController {

    private final PredictionRepository predictionRepository;

    @GetMapping("/transaction/{transactionId}")
    @Operation(summary = "Get fraud prediction for a transaction")
    public ResponseEntity<PredictionResponse> getPrediction(@PathVariable Long transactionId) {
        FraudPrediction prediction = predictionRepository.findByTransaction_Id(transactionId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "No prediction found for transaction: " + transactionId));
        return ResponseEntity.ok(PredictionResponse.from(prediction));
    }

    @GetMapping("/stats")
    @Operation(summary = "Get aggregate prediction statistics")
    public ResponseEntity<?> getStats() {
        long total = predictionRepository.count();
        long fraudulent = predictionRepository.countFraudulent();
        Double avgInference = predictionRepository.avgInferenceTimeMs();

        return ResponseEntity.ok(java.util.Map.of(
                "total_predictions", total,
                "fraudulent", fraudulent,
                "legitimate", total - fraudulent,
                "fraud_rate", total > 0 ? (double) fraudulent / total : 0.0,
                "avg_inference_ms", avgInference != null ? avgInference : 0.0
        ));
    }
}
