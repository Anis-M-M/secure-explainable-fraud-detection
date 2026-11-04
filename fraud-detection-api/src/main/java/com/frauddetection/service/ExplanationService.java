package com.frauddetection.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.frauddetection.dto.MLPredictionRequest;
import com.frauddetection.exception.ResourceNotFoundException;
import com.frauddetection.model.Explanation;
import com.frauddetection.model.FraudPrediction;
import com.frauddetection.model.Transaction;
import com.frauddetection.repository.ExplanationRepository;
import com.frauddetection.repository.PredictionRepository;
import com.frauddetection.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
@Slf4j
@RequiredArgsConstructor
public class ExplanationService {

    private final ExplanationRepository explanationRepository;
    private final PredictionRepository predictionRepository;
    private final TransactionRepository transactionRepository;
    private final RestTemplate restTemplate;
    private final AuditService auditService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${ml.service.url:http://localhost:8001}")
    private String mlServiceUrl;

    @Transactional
    public Explanation getOrGenerateShap(Long transactionId) {
        return getOrGenerate(transactionId, "SHAP", "/explain/shap");
    }

    @Transactional
    public Explanation getOrGenerateLime(Long transactionId) {
        return getOrGenerate(transactionId, "LIME", "/explain/lime");
    }

    @Transactional
    public Map<String, Object> getStabilityReport(Long transactionId) {
        Transaction tx = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new ResourceNotFoundException("Transaction not found: " + transactionId));

        MLPredictionRequest request = buildRequest(tx);
        String url = mlServiceUrl + "/explain/stability";

        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> result = restTemplate.postForObject(url, request, Map.class);
            auditService.logAction("EXPLAIN_STABILITY", "TRANSACTION", transactionId.toString(),
                    "Stability analysis generated");
            return result != null ? result : Map.of("error", "No response from ML service");
        } catch (Exception e) {
            log.error("Error fetching stability report for transaction {}", transactionId, e);
            return Map.of("error", e.getMessage());
        }
    }

    @Transactional
    public List<Explanation> getExplanationsForTransaction(Long transactionId) {
        FraudPrediction prediction = getPredictionForTransaction(transactionId);
        return explanationRepository.findByPrediction_Id(prediction.getId());
    }

    // -----------------------------------------------------------------------

    private FraudPrediction getPredictionForTransaction(Long transactionId) {
        return predictionRepository.findByTransaction_Id(transactionId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "No prediction found for transaction: " + transactionId));
    }

    private Explanation getOrGenerate(Long transactionId, String type, String endpoint) {
        FraudPrediction prediction = getPredictionForTransaction(transactionId);

        Optional<Explanation> existing =
                explanationRepository.findByPrediction_IdAndExplanationType(prediction.getId(), type);
        if (existing.isPresent()) {
            return existing.get();
        }

        Transaction tx = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new ResourceNotFoundException("Transaction not found: " + transactionId));

        MLPredictionRequest request = buildRequest(tx);
        String url = mlServiceUrl + endpoint;

        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> result = restTemplate.postForObject(url, request, Map.class);
            if (result == null) {
                throw new RuntimeException("Empty response from ML service");
            }

            Explanation explanation = Explanation.builder()
                    .prediction(prediction)
                    .modelType("XGBOOST")
                    .explanationType(type)
                    .featureImportanceJson(objectMapper.writeValueAsString(result))
                    .topFeatures(objectMapper.writeValueAsString(
                            result.getOrDefault("top_features", List.of())))
                    .build();

            explanation = explanationRepository.save(explanation);
            auditService.logAction("GENERATE_EXPLANATION", "EXPLANATION",
                    explanation.getId().toString(),
                    type + " explanation generated for transaction " + transactionId);
            log.info("{} explanation generated for transaction {}", type, transactionId);
            return explanation;

        } catch (Exception e) {
            log.error("Error generating {} explanation for transaction {}", type, transactionId, e);
            throw new RuntimeException("Failed to generate " + type + " explanation: " + e.getMessage());
        }
    }

    private MLPredictionRequest buildRequest(Transaction tx) {
        return MLPredictionRequest.builder()
                .transactionId(tx.getTransactionId())
                .amount(tx.getAmount())
                .merchant(tx.getMerchant())
                .merchantCategory(tx.getMerchantCategory())
                .userAge(tx.getUserAge())
                .userLocation(tx.getUserLocation())
                .deviceType(tx.getDeviceType())
                .build();
    }
}
