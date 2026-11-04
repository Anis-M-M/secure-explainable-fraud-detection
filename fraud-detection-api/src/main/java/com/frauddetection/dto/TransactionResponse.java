package com.frauddetection.dto;

import com.frauddetection.model.Transaction;
import lombok.Builder;
import lombok.Value;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Value
@Builder
public class TransactionResponse {
    Long id;
    String transactionId;
    BigDecimal amount;
    String merchant;
    String merchantCategory;
    LocalDateTime transactionDate;
    Integer userAge;
    String userLocation;
    String deviceType;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
    PredictionSummaryResponse prediction;

    public static TransactionResponse from(Transaction transaction) {
        return TransactionResponse.builder()
                .id(transaction.getId())
                .transactionId(transaction.getTransactionId())
                .amount(transaction.getAmount())
                .merchant(transaction.getMerchant())
                .merchantCategory(transaction.getMerchantCategory())
                .transactionDate(transaction.getTransactionDate())
                .userAge(transaction.getUserAge())
                .userLocation(transaction.getUserLocation())
                .deviceType(transaction.getDeviceType())
                .createdAt(transaction.getCreatedAt())
                .updatedAt(transaction.getUpdatedAt())
                .prediction(PredictionSummaryResponse.from(transaction.getPrediction()))
                .build();
    }
}
