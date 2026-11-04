package com.frauddetection.service;

import com.frauddetection.dto.MLPredictionRequest;
import com.frauddetection.dto.MLPredictionResponse;
import com.frauddetection.model.FraudPrediction;
import com.frauddetection.model.Transaction;
import com.frauddetection.repository.PredictionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
@Slf4j
@RequiredArgsConstructor
public class ModelInferenceService {

    private final PredictionRepository predictionRepository;
    private final RestTemplate restTemplate;
    private final AuditService auditService;

    @Value("${ml.service.url:http://localhost:8001}")
    private String mlServiceUrl;

    @Async
    public void predictAsync(Transaction transaction) {
        try {
            MLPredictionRequest request = MLPredictionRequest.builder()
                    .transactionId(transaction.getTransactionId())
                    .amount(transaction.getAmount())
                    .merchant(transaction.getMerchant())
                    .merchantCategory(transaction.getMerchantCategory())
                    .userAge(transaction.getUserAge())
                    .userLocation(transaction.getUserLocation())
                    .deviceType(transaction.getDeviceType())
                    .build();

            String url = mlServiceUrl + "/predict";
            MLPredictionResponse response = restTemplate.postForObject(url, request, MLPredictionResponse.class);

            if (response == null) {
                log.error("No response from ML service for transaction: {}", transaction.getTransactionId());
                return;
            }

            FraudPrediction prediction = FraudPrediction.builder()
                    .transaction(transaction)
                    .ruleBasedPrediction(response.getRuleBasedPrediction())
                    .ruleBasedConfidence(response.getRuleBasedConfidence())
                    .logisticRegressionPrediction(response.getLogisticRegressionPrediction())
                    .logisticRegressionProbability(response.getLogisticRegressionProbability())
                    .xgboostPrediction(response.getXgboostPrediction())
                    .xgboostProbability(response.getXgboostProbability())
                    .neuralNetworkPrediction(response.getNeuralNetworkPrediction())
                    .neuralNetworkProbability(response.getNeuralNetworkProbability())
                    .finalPrediction(response.getFinalPrediction())
                    .finalConfidence(response.getFinalConfidence())
                    .modelVersion(response.getModelVersion())
                    .inferenceTimeMs(response.getInferenceTimeMs())
                    .build();

            predictionRepository.save(prediction);

            String label = prediction.getFinalPrediction() == 1 ? "FRAUD" : "LEGITIMATE";
            auditService.logAction("MODEL_INFERENCE", "PREDICTION",
                    prediction.getId().toString(), "Prediction: " + label);
            log.info("Prediction stored for transaction: {} -> {}", transaction.getTransactionId(), label);

        } catch (Exception e) {
            log.error("Error during ML inference for transaction: {}", transaction.getTransactionId(), e);
            auditService.logAction("MODEL_INFERENCE_ERROR", "PREDICTION",
                    transaction.getId().toString(), "Error: " + e.getMessage());
        }
    }

    public FraudPrediction getPredictionByTransactionId(Long transactionId) {
        return predictionRepository.findByTransaction_Id(transactionId)
                .orElseThrow(() -> new RuntimeException("Prediction not found for transaction: " + transactionId));
    }
}
