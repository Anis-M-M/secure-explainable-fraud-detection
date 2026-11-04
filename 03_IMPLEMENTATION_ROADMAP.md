# Secure & Explainable Fraud Detection System
## Implementation Roadmap & Code Templates

---

## Development Timeline

### Phase 1: Foundation (Weeks 1-2)
- [x] Project structure setup
- [x] Database schema creation
- [ ] Spring Boot configuration
- [ ] JWT authentication
- [ ] Basic CRUD APIs

**Deliverable:** Working backend with user authentication

### Phase 2: ML Integration (Weeks 3-4)
- [ ] Python ML service setup
- [ ] Model training pipeline
- [ ] gRPC service implementation
- [ ] Model inference API
- [ ] Prediction storage

**Deliverable:** ML service callable from Java backend

### Phase 3: Explainability (Weeks 5-6)
- [ ] SHAP integration
- [ ] LIME integration
- [ ] Stability analysis
- [ ] Explanation endpoints
- [ ] Visualization preparation

**Deliverable:** Explanation generation for all models

### Phase 4: Frontend (Weeks 7-8)
- [ ] React project setup
- [ ] Authentication UI
- [ ] Dashboard components
- [ ] Model comparison views
- [ ] Explanation visualizations

**Deliverable:** Professional React frontend

### Phase 5: Testing & Optimization (Weeks 9-10)
- [ ] Unit tests (70%+ coverage)
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation

**Deliverable:** Production-ready system

### Phase 6: Evaluation & Reporting (Weeks 11-12)
- [ ] Comprehensive testing
- [ ] Results analysis
- [ ] Report writing
- [ ] Presentation preparation
- [ ] Code cleanup

**Deliverable:** Final project submission

---

## Code Templates

### 1. Spring Boot Main Application

**FraudDetectionApplication.java**
```java
package com.frauddetection;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@SpringBootApplication
public class FraudDetectionApplication {

    public static void main(String[] args) {
        SpringApplication.run(FraudDetectionApplication.class, args);
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

---

### 2. Security Configuration

**SecurityConfig.java**
```java
package com.frauddetection.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import com.frauddetection.security.JwtAuthenticationFilter;
import com.frauddetection.security.JwtAuthenticationEntryPoint;

@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class SecurityConfig {

    @Autowired
    private UserDetailsService userDetailsService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;

    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter();
    }

    @Bean
    public AuthenticationManager authenticationManager(HttpSecurity http) throws Exception {
        return http.getSharedObject(AuthenticationManagerBuilder.class)
                .userDetailsService(userDetailsService)
                .passwordEncoder(passwordEncoder)
                .and()
                .build();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
                .cors()
                .and()
                .exceptionHandling()
                .authenticationEntryPoint(jwtAuthenticationEntryPoint)
                .and()
                .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
                .authorizeRequests()
                .antMatchers("/api/v1/auth/**").permitAll()
                .antMatchers("/swagger-ui/**", "/v3/api-docs/**").permitAll()
                .antMatchers(HttpMethod.GET, "/api/v1/health").permitAll()
                .anyRequest().authenticated()
                .and()
                .addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(java.util.Arrays.asList("http://localhost:3000", "http://localhost:5173"));
        configuration.setAllowedMethods(java.util.Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(java.util.Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

---

### 3. JWT Token Provider

**JwtTokenProvider.java**
```java
package com.frauddetection.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.stream.Collectors;

@Component
@Slf4j
public class JwtTokenProvider {

    @Value("${spring.security.jwt.secret:your-super-secret-key-change-in-production}")
    private String jwtSecret;

    @Value("${spring.security.jwt.expiration:86400000}")  // 24 hours
    private long jwtExpirationMs;

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes());
    }

    public String generateToken(Authentication authentication) {
        String username = authentication.getName();
        String roles = authentication.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.joining(","));

        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + jwtExpirationMs);

        return Jwts.builder()
                .setSubject(username)
                .claim("roles", roles)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public String generateTokenFromUsername(String username) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + jwtExpirationMs);

        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public String getUsernameFromJWT(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getSubject();
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(getSigningKey())
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (SecurityException e) {
            log.error("Invalid JWT signature: {}", e.getMessage());
        } catch (MalformedJwtException e) {
            log.error("Invalid JWT token: {}", e.getMessage());
        } catch (ExpiredJwtException e) {
            log.error("Expired JWT token: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            log.error("Unsupported JWT token: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            log.error("JWT claims string is empty: {}", e.getMessage());
        }
        return false;
    }
}
```

---

### 4. User Entity

**User.java**
```java
package com.frauddetection.model;

import lombok.*;
import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String passwordHash;

    @Column(name = "first_name")
    private String firstName;

    @Column(name = "last_name")
    private String lastName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role = Role.ANALYST;

    @Column(name = "is_active")
    private Boolean isActive = true;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    public enum Role {
        ADMIN, ANALYST, VIEWER, AUDITOR
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

---

### 5. Authentication Controller

**AuthController.java**
```java
package com.frauddetection.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import com.frauddetection.dto.LoginRequest;
import com.frauddetection.dto.AuthResponse;
import com.frauddetection.security.JwtTokenProvider;
import com.frauddetection.service.AuthService;

import javax.validation.Valid;

@RestController
@RequestMapping("/api/v1/auth")
@Slf4j
public class AuthController {

    @Autowired
    private AuthService authService;

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtTokenProvider tokenProvider;

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest loginRequest) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            loginRequest.getUsername(),
                            loginRequest.getPassword()
                    )
            );

            String jwt = tokenProvider.generateToken(authentication);

            return ResponseEntity.ok(new AuthResponse(
                    jwt,
                    "Bearer",
                    86400,
                    authentication.getName()
            ));

        } catch (Exception e) {
            log.warn("Login failed for user: {}", loginRequest.getUsername());
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid credentials");
        }
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refreshToken(@RequestHeader("Authorization") String tokenHeader) {
        if (tokenHeader == null || !tokenHeader.startsWith("Bearer ")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing or invalid token");
        }

        String token = tokenHeader.substring(7);
        if (!tokenProvider.validateToken(token)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid token");
        }

        String username = tokenProvider.getUsernameFromJWT(token);
        String newToken = tokenProvider.generateTokenFromUsername(username);

        return ResponseEntity.ok(new AuthResponse(
                newToken,
                "Bearer",
                86400,
                username
        ));
    }

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser(@RequestHeader("Authorization") String tokenHeader) {
        if (tokenHeader == null || !tokenHeader.startsWith("Bearer ")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing token");
        }

        String token = tokenHeader.substring(7);
        String username = tokenProvider.getUsernameFromJWT(token);

        return ResponseEntity.ok(authService.getUserByUsername(username));
    }
}
```

---

### 6. Transaction Entity & Repository

**Transaction.java**
```java
package com.frauddetection.model;

import lombok.*;
import javax.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "transactions")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String transactionId;

    @Column(nullable = false)
    private BigDecimal amount;

    private String merchant;

    @Column(name = "merchant_category")
    private String merchantCategory;

    @Column(name = "transaction_date", nullable = false)
    private LocalDateTime transactionDate;

    @Column(name = "user_age")
    private Integer userAge;

    @Column(name = "user_location")
    private String userLocation;

    @Column(name = "device_type")
    private String deviceType;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

**TransactionRepository.java**
```java
package com.frauddetection.repository;

import com.frauddetection.model.Transaction;
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

    Page<Transaction> findAll(Pageable pageable);

    @Query("SELECT t FROM Transaction t WHERE t.transactionDate BETWEEN ?1 AND ?2")
    Page<Transaction> findByDateRange(LocalDateTime startDate, LocalDateTime endDate, Pageable pageable);

    long countByTransactionDateBetween(LocalDateTime startDate, LocalDateTime endDate);
}
```

---

### 7. Transaction Service

**TransactionService.java**
```java
package com.frauddetection.service;

import com.frauddetection.dto.TransactionDTO;
import com.frauddetection.exception.DuplicateTransactionException;
import com.frauddetection.exception.ResourceNotFoundException;
import com.frauddetection.model.Transaction;
import com.frauddetection.repository.TransactionRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@Slf4j
public class TransactionService {

    @Autowired
    private TransactionRepository transactionRepository;

    @Autowired
    private AuditService auditService;

    @Autowired
    private ModelInferenceService modelInferenceService;

    @Transactional
    public Transaction createTransaction(TransactionDTO dto) {
        // Check for duplicates
        if (transactionRepository.findByTransactionId(dto.getTransactionId()).isPresent()) {
            throw new DuplicateTransactionException("Transaction already exists");
        }

        // Create transaction
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

        // Trigger fraud detection asynchronously
        modelInferenceService.predictAsync(transaction);

        // Audit log
        auditService.logAction("CREATE_TRANSACTION", "TRANSACTION", transaction.getId().toString(),
                "Transaction created: " + dto.getTransactionId());

        log.info("Transaction created: {}", dto.getTransactionId());
        return transaction;
    }

    @Transactional(readOnly = true)
    public Transaction getTransaction(Long id) {
        return transactionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Transaction not found"));
    }

    @Transactional(readOnly = true)
    public Page<Transaction> getTransactions(Pageable pageable) {
        return transactionRepository.findAll(pageable);
    }

    @Transactional(readOnly = true)
    public Page<Transaction> getTransactionsByDateRange(LocalDateTime startDate, LocalDateTime endDate, Pageable pageable) {
        return transactionRepository.findByDateRange(startDate, endDate, pageable);
    }
}
```

---

### 8. Model Inference Service

**ModelInferenceService.java**
```java
package com.frauddetection.service;

import com.frauddetection.model.Transaction;
import com.frauddetection.model.FraudPrediction;
import com.frauddetection.repository.PredictionRepository;
import com.frauddetection.dto.MLPredictionRequest;
import com.frauddetection.dto.MLPredictionResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.concurrent.CompletableFuture;

@Service
@Slf4j
public class ModelInferenceService {

    @Autowired
    private PredictionRepository predictionRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private AuditService auditService;

    @Value("${ml.service.url:http://localhost:8001}")
    private String mlServiceUrl;

    @Async
    public void predictAsync(Transaction transaction) {
        try {
            // Call Python ML service
            MLPredictionRequest request = MLPredictionRequest.builder()
                    .amount(transaction.getAmount())
                    .merchant(transaction.getMerchant())
                    .merchantCategory(transaction.getMerchantCategory())
                    .userAge(transaction.getUserAge())
                    .userLocation(transaction.getUserLocation())
                    .deviceType(transaction.getDeviceType())
                    .build();

            String url = mlServiceUrl + "/predict";
            MLPredictionResponse response = restTemplate.postForObject(url, request, MLPredictionResponse.class);

            // Store prediction
            FraudPrediction prediction = FraudPrediction.builder()
                    .transactionId(transaction.getId())
                    .ruleBasedPrediction(response.getRuleBasedPrediction())
                    .ruleBasedConfidence(response.getRuleBasedConfidence())
                    .logisticRegressionPrediction(response.getLogisticRegressionPrediction())
                    .logisticRegressionProbability(response.getLogisticRegressionProbability())
                    .xgboostPrediction(response.getXgboostPrediction())
                    .xgboostProbability(response.getXgboostProbability())
                    .neuralNetworkPrediction(response.getNeuralNetworkPrediction())
                    .neuralNetworkProbability(response.getNeuralNetworkProbability())
                    .finalPrediction(response.getFinalPrediction())
                    .finalConfidence(response.getFinalConfidence())
                    .modelVersion(response.getModelVersion())
                    .inferenceTimeMs(response.getInferenceTimeMs())
                    .build();

            predictionRepository.save(prediction);

            // Audit log
            auditService.logAction("MODEL_INFERENCE", "PREDICTION", prediction.getId().toString(),
                    "Prediction: " + (prediction.getFinalPrediction() == 1 ? "FRAUD" : "LEGITIMATE"));

            log.info("Prediction stored for transaction: {}", transaction.getTransactionId());

        } catch (Exception e) {
            log.error("Error during model inference", e);
            auditService.logAction("MODEL_INFERENCE_ERROR", "PREDICTION", transaction.getId().toString(),
                    "Error: " + e.getMessage());
        }
    }

    public FraudPrediction getPrediction(Long transactionId) {
        return predictionRepository.findByTransactionId(transactionId)
                .orElseThrow(() -> new RuntimeException("Prediction not found"));
    }
}
```

---

### 9. Audit Service

**AuditService.java**
```java
package com.frauddetection.service;

import com.frauddetection.model.AuditLog;
import com.frauddetection.repository.AuditLogRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.servlet.http.HttpServletRequest;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
public class AuditService {

    @Autowired
    private AuditLogRepository auditLogRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Async
    public void logAction(String action, String resourceType, String resourceId, String details) {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            Long userId = null;
            String username = "SYSTEM";

            if (authentication != null && authentication.isAuthenticated()) {
                username = authentication.getName();
                // Get user ID if available from principal
            }

            String ipAddress = getClientIpAddress();

            Map<String, Object> detailsMap = new HashMap<>();
            detailsMap.put("message", details);
            detailsMap.put("timestamp", LocalDateTime.now());

            AuditLog auditLog = AuditLog.builder()
                    .userId(userId)
                    .username(username)
                    .action(action)
                    .resourceType(resourceType)
                    .resourceId(resourceId)
                    .details(objectMapper.writeValueAsString(detailsMap))
                    .ipAddress(ipAddress)
                    .timestamp(LocalDateTime.now())
                    .build();

            auditLogRepository.save(auditLog);
            log.debug("Audit log recorded: {} by {}", action, username);

        } catch (Exception e) {
            log.error("Error recording audit log", e);
        }
    }

    private String getClientIpAddress() {
        try {
            ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attributes != null) {
                HttpServletRequest request = attributes.getRequest();
                String clientIp = request.getHeader("X-Forwarded-For");
                if (clientIp == null || clientIp.isEmpty()) {
                    clientIp = request.getRemoteAddr();
                }
                return clientIp;
            }
        } catch (Exception e) {
            log.debug("Could not determine client IP");
        }
        return "UNKNOWN";
    }
}
```

---

## Key Code Patterns

### Dependency Injection Example
```java
@Service
public class MyService {
    @Autowired
    private SomeDependency dependency;
    
    // or Constructor Injection (preferred)
    private final SomeDependency dependency;
    
    public MyService(SomeDependency dependency) {
        this.dependency = dependency;
    }
}
```

### Custom Exception Handling
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(ResourceNotFoundException e) {
        ErrorResponse error = new ErrorResponse(404, e.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGlobalException(Exception e) {
        ErrorResponse error = new ErrorResponse(500, "Internal server error");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

### DTOs Pattern
```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TransactionDTO {
    @NotBlank(message = "Transaction ID is required")
    private String transactionId;
    
    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.0", inclusive = false)
    private BigDecimal amount;
    
    // getters, setters...
}
```

---

## Testing Templates

### Unit Test Example
```java
@SpringBootTest
class TransactionServiceTest {
    
    @MockBean
    private TransactionRepository transactionRepository;
    
    @InjectMocks
    private TransactionService service;
    
    @Test
    void testCreateTransaction() {
        // Arrange
        TransactionDTO dto = new TransactionDTO("TXN-001", ...);
        Transaction expected = new Transaction(...);
        given(transactionRepository.save(any())).willReturn(expected);
        
        // Act
        Transaction result = service.createTransaction(dto);
        
        // Assert
        assertThat(result).isEqualTo(expected);
        verify(transactionRepository, times(1)).save(any());
    }
}
```

### Integration Test Example
```java
@SpringBootTest
@AutoConfigureMockMvc
class AuthControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testLoginEndpoint() throws Exception {
        // Arrange
        LoginRequest request = new LoginRequest("user", "password");
        
        // Act & Assert
        mockMvc.perform(post("/api/v1/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(new ObjectMapper().writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").exists());
    }
}
```

---

## Documentation Checklist

- [ ] API documentation (Swagger/OpenAPI)
- [ ] Database schema documentation
- [ ] Deployment guide
- [ ] Security best practices document
- [ ] Team onboarding guide
- [ ] Code style guide
- [ ] Troubleshooting guide

---

## Quick Start Commands

```bash
# Build
./mvnw clean package -DskipTests

# Run tests
./mvnw test

# Run with specific profile
./mvnw spring-boot:run -Dspring-boot.run.arguments="--spring.profiles.active=dev"

# Run with Docker
docker build -t fraud-detection-api .
docker run -p 8080:8080 fraud-detection-api
```

---

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** In Progress
