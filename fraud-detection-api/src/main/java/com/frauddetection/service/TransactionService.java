package com.frauddetection.service;

import com.frauddetection.dto.TransactionDTO;
import com.frauddetection.dto.TransactionResponse;
import com.frauddetection.exception.DuplicateTransactionException;
import com.frauddetection.exception.ResourceNotFoundException;
import com.frauddetection.model.Transaction;
import com.frauddetection.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@Slf4j
@RequiredArgsConstructor
public class TransactionService {

    private final TransactionRepository transactionRepository;
    private final AuditService auditService;
    private final ModelInferenceService modelInferenceService;

    @Transactional
    public Transaction createTransaction(TransactionDTO dto) {
        if (transactionRepository.existsByTransactionId(dto.getTransactionId())) {
            throw new DuplicateTransactionException(
                    "Transaction already exists: " + dto.getTransactionId());
        }

        Transaction transaction = Transaction.builder()
                .transactionId(dto.getTransactionId())
                .amount(dto.getAmount())
                .merchant(dto.getMerchant())
                .merchantCategory(dto.getMerchantCategory())
                .transactionDate(dto.getTransactionDate())
                .userAge(dto.getUserAge())
                .userLocation(dto.getUserLocation())
                .deviceType(dto.getDeviceType())
                .build();

        transaction = transactionRepository.save(transaction);

        // Trigger async fraud detection
        modelInferenceService.predictAsync(transaction);

        auditService.logAction("CREATE_TRANSACTION", "TRANSACTION",
                transaction.getId().toString(),
                "Transaction created: " + dto.getTransactionId());
        log.info("Transaction created: {}", dto.getTransactionId());
        return transaction;
    }

    @Transactional(readOnly = true)
    public TransactionResponse getTransaction(Long id) {
        Transaction transaction = transactionRepository.findWithPredictionById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Transaction not found: " + id));
        return TransactionResponse.from(transaction);
    }

    @Transactional(readOnly = true)
    public Page<TransactionResponse> getTransactions(Pageable pageable) {
        return transactionRepository.findAll(pageable).map(TransactionResponse::from);
    }

    @Transactional(readOnly = true)
    public Page<TransactionResponse> getTransactionsByDateRange(LocalDateTime startDate,
                                                                LocalDateTime endDate,
                                                                Pageable pageable) {
        return transactionRepository.findByDateRange(startDate, endDate, pageable)
                .map(TransactionResponse::from);
    }
}
