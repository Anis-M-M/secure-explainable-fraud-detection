package com.frauddetection.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "fraud_predictions")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FraudPrediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transaction_id", unique = true, nullable = false)
    private Transaction transaction;

    @Column(name = "rule_based_prediction")
    private Integer ruleBasedPrediction;

    @Column(name = "rule_based_confidence", precision = 5, scale = 4)
    private BigDecimal ruleBasedConfidence;

    @Column(name = "logistic_regression_prediction")
    private Integer logisticRegressionPrediction;

    @Column(name = "logistic_regression_probability", precision = 5, scale = 4)
    private BigDecimal logisticRegressionProbability;

    @Column(name = "xgboost_prediction")
    private Integer xgboostPrediction;

    @Column(name = "xgboost_probability", precision = 5, scale = 4)
    private BigDecimal xgboostProbability;

    @Column(name = "neural_network_prediction")
    private Integer neuralNetworkPrediction;

    @Column(name = "neural_network_probability", precision = 5, scale = 4)
    private BigDecimal neuralNetworkProbability;

    @Column(name = "final_prediction", nullable = false)
    private Integer finalPrediction;

    @Column(name = "final_confidence", nullable = false, precision = 5, scale = 4)
    private BigDecimal finalConfidence;

    @Column(name = "model_version")
    private String modelVersion;

    @Column(name = "inference_time_ms")
    private Integer inferenceTimeMs;

    @Column(name = "created_at", nullable = false, updatable = false)
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();

    @OneToMany(mappedBy = "prediction", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Explanation> explanations;
}
