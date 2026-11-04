package com.frauddetection.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "explanations")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Explanation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "prediction_id", nullable = false)
    private FraudPrediction prediction;

    @Column(name = "model_type", nullable = false)
    private String modelType;

    @Column(name = "explanation_type", nullable = false)
    private String explanationType; // SHAP or LIME

    @Column(name = "feature_importance_json", columnDefinition = "jsonb")
    private String featureImportanceJson;

    @Column(name = "top_features", columnDefinition = "jsonb")
    private String topFeatures;

    @Column(name = "explanation_html", columnDefinition = "TEXT")
    private String explanationHtml;

    @Column(name = "stability_score", precision = 5, scale = 4)
    private BigDecimal stabilityScore;

    @Column(name = "created_at", nullable = false, updatable = false)
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}
