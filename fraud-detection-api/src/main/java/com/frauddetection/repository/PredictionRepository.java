package com.frauddetection.repository;

import com.frauddetection.model.FraudPrediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PredictionRepository extends JpaRepository<FraudPrediction, Long> {
    Optional<FraudPrediction> findByTransaction_Id(Long transactionId);

    @Query("SELECT COUNT(p) FROM FraudPrediction p WHERE p.finalPrediction = 1")
    long countFraudulent();

    @Query("SELECT AVG(p.inferenceTimeMs) FROM FraudPrediction p WHERE p.inferenceTimeMs IS NOT NULL")
    Double avgInferenceTimeMs();
}
