package com.frauddetection.repository;

import com.frauddetection.model.Explanation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ExplanationRepository extends JpaRepository<Explanation, Long> {
    List<Explanation> findByPrediction_Id(Long predictionId);
    Optional<Explanation> findByPrediction_IdAndExplanationType(Long predictionId, String explanationType);
}
