package com.frauddetection.repository;

import com.frauddetection.model.Transaction;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long> {
    Optional<Transaction> findByTransactionId(String transactionId);
    boolean existsByTransactionId(String transactionId);

    @EntityGraph(attributePaths = "prediction")
    Optional<Transaction> findWithPredictionById(Long id);

    @Override
    @EntityGraph(attributePaths = "prediction")
    Page<Transaction> findAll(Pageable pageable);

    @EntityGraph(attributePaths = "prediction")
    @Query("SELECT t FROM Transaction t WHERE t.transactionDate BETWEEN ?1 AND ?2")
    Page<Transaction> findByDateRange(LocalDateTime startDate, LocalDateTime endDate, Pageable pageable);

    long countByTransactionDateBetween(LocalDateTime startDate, LocalDateTime endDate);
}
