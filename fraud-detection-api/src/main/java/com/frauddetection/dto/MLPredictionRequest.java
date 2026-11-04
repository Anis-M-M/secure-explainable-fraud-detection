package com.frauddetection.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MLPredictionRequest {
    private String transactionId;
    private BigDecimal amount;
    private String merchant;
    private String merchantCategory;
    private Integer userAge;
    private String userLocation;
    private String deviceType;
}
