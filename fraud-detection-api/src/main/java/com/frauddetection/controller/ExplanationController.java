package com.frauddetection.controller;

import com.frauddetection.dto.ExplanationResponse;
import com.frauddetection.model.Explanation;
import com.frauddetection.service.ExplanationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/explanations")
@RequiredArgsConstructor
@Tag(name = "Explanations", description = "XAI explanation endpoints (SHAP, LIME, Stability)")
@SecurityRequirement(name = "bearerAuth")
public class ExplanationController {

    private final ExplanationService explanationService;

    @GetMapping("/transaction/{transactionId}")
    @Operation(summary = "List all explanations for a transaction")
    public ResponseEntity<List<ExplanationResponse>> getExplanations(@PathVariable Long transactionId) {
        return ResponseEntity.ok(explanationService.getExplanationsForTransaction(transactionId).stream()
                .map(ExplanationResponse::from)
                .toList());
    }

    @GetMapping("/transaction/{transactionId}/shap")
    @Operation(summary = "Get or generate SHAP explanation")
    public ResponseEntity<ExplanationResponse> getShap(@PathVariable Long transactionId) {
        return ResponseEntity.ok(ExplanationResponse.from(explanationService.getOrGenerateShap(transactionId)));
    }

    @GetMapping("/transaction/{transactionId}/lime")
    @Operation(summary = "Get or generate LIME explanation")
    public ResponseEntity<ExplanationResponse> getLime(@PathVariable Long transactionId) {
        return ResponseEntity.ok(ExplanationResponse.from(explanationService.getOrGenerateLime(transactionId)));
    }

    @GetMapping("/transaction/{transactionId}/stability")
    @Operation(summary = "Run perturbation-based stability analysis (RQ2)")
    public ResponseEntity<Map<String, Object>> getStability(@PathVariable Long transactionId) {
        return ResponseEntity.ok(explanationService.getStabilityReport(transactionId));
    }
}
