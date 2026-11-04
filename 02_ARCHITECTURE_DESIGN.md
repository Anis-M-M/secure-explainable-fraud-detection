# Secure & Explainable Fraud Detection System
## Architecture & Design Document

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  • Web Browser (React SPA)                                           │
│  • Mobile App (Future)                                               │
│  • Admin Dashboard                                                    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTPS/TLS
┌──────────────────────────▼──────────────────────────────────────────┐
│                      API GATEWAY LAYER                               │
├──────────────────────────────────────────────────────────────────────┤
│  • Request Validation                                                │
│  • Rate Limiting                                                     │
│  • CORS Configuration                                                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                   SPRING BOOT BACKEND                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ PRESENTATION LAYER (REST Controllers)                       │    │
│  │  • AuthController       (Login, Register, Token Refresh)    │    │
│  │  • TransactionController (CRUD, Batch Upload)              │    │
│  │  • ModelController      (Manage, Evaluate)                 │    │
│  │  • PredictionController (Inference, History)               │    │
│  │  • ExplanationController (SHAP, LIME, Stability)          │    │
│  │  • AnalyticsController  (Reports, Metrics)                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                           │                                           │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │ BUSINESS LOGIC LAYER (Services)                             │    │
│  │  • AuthService          (JWT, RBAC, User Management)       │    │
│  │  • TransactionService   (Data validation, Enrichment)      │    │
│  │  • ModelInferenceService (Call ML Service, Cache Results)  │    │
│  │  • ExplanationService   (SHAP/LIME orchestration)          │    │
│  │  • AuditService         (Logging, Compliance)              │    │
│  │  • CacheService         (Redis for performance)            │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                           │                                           │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │ DATA ACCESS LAYER (JPA Repositories)                        │    │
│  │  • UserRepository       (User management)                   │    │
│  │  • TransactionRepository (Transaction CRUD)                │    │
│  │  • PredictionRepository (Prediction storage)               │    │
│  │  • ExplanationRepository (Explanation persistence)         │    │
│  │  • AuditLogRepository   (Audit trail)                      │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                           │                                           │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │ SECURITY LAYER                                              │    │
│  │  • JWT Token Provider   (Token generation/validation)      │    │
│  │  • Custom User Details Service                              │    │
│  │  • Authorization Filters                                    │    │
│  │  • Password Encryption (BCrypt)                             │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────┬───────────────────────────────────────────────────────────┘
           │ gRPC/REST
┌──────────▼───────────────────────────────────────────────────────────┐
│                    PYTHON ML SERVICE                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ MODEL LAYER                                                 │    │
│  │  • RuleBasedDetector    (Heuristic rules)                  │    │
│  │  • LogisticRegressionModel (Probabilistic)                 │    │
│  │  • XGBoostModel         (Gradient boosting)                │    │
│  │  • NeuralNetworkModel   (Deep learning)                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                           │                                           │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │ EXPLAINABILITY LAYER                                        │    │
│  │  • SHAPExplainer        (SHAP values)                       │    │
│  │  • LIMEExplainer        (Local explanations)                │    │
│  │  • StabilityAnalyzer    (Perturbation tests)               │    │
│  │  • AttributionComparer  (SHAP vs LIME)                     │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                           │                                           │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │ FEATURE ENGINEERING & PREPROCESSING                         │    │
│  │  • DataLoader           (Kaggle dataset)                    │    │
│  │  • Preprocessor         (Scaling, encoding)                │    │
│  │  • FeatureEngineer      (Derived features)                 │    │
│  │  • ImbalanceHandler     (SMOTE, class weighting)           │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────┬───────────────────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────────────────┐
│              DATA PERSISTENCE & EXTERNAL SYSTEMS                      │
├──────────────────────────────────────────────────────────────────────┤
│  • PostgreSQL (Transactions, Predictions, Explanations)              │
│  • Redis Cache (Performance optimization)                            │
│  • Model Store (Trained model persistence)                           │
│  • Monitoring (Prometheus, ELK)                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## API Specifications

### 1. Authentication API

#### Register User
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "analyst@bank.com",
  "email": "analyst@bank.com",
  "password": "example-password",
  "firstName": "John",
  "lastName": "Analyst",
  "role": "ANALYST"  // ANALYST, ADMIN, VIEWER
}

Response (201 Created):
{
  "id": 1,
  "username": "analyst@bank.com",
  "email": "analyst@bank.com",
  "role": "ANALYST",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

#### Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "analyst@bank.com",
  "password": "example-password"
}

Response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "Bearer",
  "expiresIn": 86400,
  "user": {
    "id": 1,
    "username": "analyst@bank.com",
    "role": "ANALYST"
  }
}
```

#### Refresh Token
```
POST /api/v1/auth/refresh
Authorization: Bearer <refreshToken>

Response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 86400
}
```

---

### 2. Transaction API

#### Create Transaction
```
POST /api/v1/transactions
Authorization: Bearer <token>
Content-Type: application/json

{
  "transactionId": "TXN-20250115-001",
  "amount": 150.50,
  "merchant": "Amazon",
  "merchantCategory": "Electronics",
  "transactionDate": "2025-01-15T10:30:00Z",
  "userAge": 35,
  "userLocation": "New York",
  "deviceType": "Mobile"
}

Response (201 Created):
{
  "id": 1,
  "transactionId": "TXN-20250115-001",
  "amount": 150.50,
  "merchant": "Amazon",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

#### Get Transaction Details
```
GET /api/v1/transactions/{id}
Authorization: Bearer <token>

Response (200 OK):
{
  "id": 1,
  "transactionId": "TXN-20250115-001",
  "amount": 150.50,
  "merchant": "Amazon",
  "prediction": {
    "id": 1,
    "finalPrediction": 0,  // 0 = Legitimate, 1 = Fraud
    "finalConfidence": 0.95,
    "modelVersion": "v1.0"
  },
  "explanations": [
    {
      "id": 1,
      "modelType": "XGBoost",
      "explanationType": "SHAP",
      "topFeatures": ["amount", "merchant", "deviceType"]
    }
  ]
}
```

#### List Transactions (Pagination)
```
GET /api/v1/transactions?page=0&size=20&sort=createdAt,desc
Authorization: Bearer <token>

Response (200 OK):
{
  "content": [
    { /* transaction object */ },
    { /* transaction object */ }
  ],
  "pageable": {
    "pageNumber": 0,
    "pageSize": 20,
    "totalPages": 5,
    "totalElements": 100
  }
}
```

#### Batch Upload Transactions
```
POST /api/v1/transactions/batch
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <CSV file>

Response (202 Accepted):
{
  "jobId": "batch-001",
  "status": "PROCESSING",
  "totalRecords": 1000,
  "processedRecords": 0,
  "failedRecords": 0
}
```

---

### 3. Fraud Prediction API

#### Get Predictions for Transaction
```
GET /api/v1/predictions/{transactionId}
Authorization: Bearer <token>

Response (200 OK):
{
  "id": 1,
  "transactionId": "TXN-20250115-001",
  "predictions": {
    "ruleBased": {
      "prediction": 0,
      "confidence": 0.85
    },
    "logisticRegression": {
      "prediction": 0,
      "probability": 0.12
    },
    "xgboost": {
      "prediction": 1,
      "probability": 0.78
    },
    "neuralNetwork": {
      "prediction": 0,
      "probability": 0.42
    }
  },
  "finalPrediction": 0,
  "finalConfidence": 0.79,
  "inferenceTimeMs": 45,
  "modelVersion": "v1.0"
}
```

#### Get Model Performance Metrics
```
GET /api/v1/predictions/metrics?modelType=XGBOOST&from=2025-01-01&to=2025-01-31
Authorization: Bearer <token>

Response (200 OK):
{
  "modelType": "XGBOOST",
  "metrics": {
    "accuracy": 0.9842,
    "precision": 0.8956,
    "recall": 0.7834,
    "f1Score": 0.8357,
    "auc": 0.9567,
    "confusionMatrix": {
      "tn": 98500,
      "fp": 400,
      "fn": 650,
      "tp": 450
    }
  },
  "periodStart": "2025-01-01T00:00:00Z",
  "periodEnd": "2025-01-31T23:59:59Z"
}
```

---

### 4. Explanation API

#### Get SHAP Explanation
```
GET /api/v1/explanations/{predictionId}/shap
Authorization: Bearer <token>

Response (200 OK):
{
  "id": 1,
  "predictionId": 1,
  "modelType": "XGBOOST",
  "explanationType": "SHAP",
  "baseValue": 0.12,
  "shapeValues": {
    "amount": 0.25,
    "merchant": 0.15,
    "deviceType": 0.08,
    "userAge": 0.03,
    "transactionDate": 0.01
  },
  "topFeatures": [
    {
      "feature": "amount",
      "shapValue": 0.25,
      "baselineValue": 150.50,
      "actualValue": 250.00,
      "impact": "HIGH"
    },
    {
      "feature": "merchant",
      "shapValue": 0.15,
      "baselineValue": "Electronics",
      "actualValue": "Amazon",
      "impact": "MEDIUM"
    }
  ],
  "plotUrl": "/api/v1/explanations/1/shap/plot",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

#### Get LIME Explanation
```
GET /api/v1/explanations/{predictionId}/lime
Authorization: Bearer <token>

Response (200 OK):
{
  "id": 2,
  "predictionId": 1,
  "modelType": "XGBOOST",
  "explanationType": "LIME",
  "intercept": 0.45,
  "localWeights": {
    "amount": 0.32,
    "merchant": 0.18,
    "deviceType": 0.12,
    "userAge": 0.04,
    "transactionDate": 0.02
  },
  "topFeatures": [
    {
      "feature": "amount",
      "weight": 0.32,
      "contribution": "Increases fraud probability"
    },
    {
      "feature": "merchant",
      "weight": 0.18,
      "contribution": "Increases fraud probability"
    }
  ],
  "htmlVisualization": "<html>...</html>",
  "createdAt": "2025-01-15T10:30:00Z"
}
```

#### Get Explanation Stability Report
```
GET /api/v1/explanations/{predictionId}/stability
Authorization: Bearer <token>

Response (200 OK):
{
  "predictionId": 1,
  "stabilityAnalysis": {
    "perturbationCount": 100,
    "stabilityScore": 0.82,
    "consistencyMetric": 0.78,
    "sensitivityMetric": 0.45,
    "featureRankingAgreement": {
      "shap": ["amount", "merchant", "deviceType", "userAge"],
      "lime": ["amount", "merchant", "userAge", "deviceType"],
      "spearmanCorrelation": 0.95
    }
  },
  "recommendations": [
    "SHAP and LIME show strong agreement on top features",
    "Amount is consistently the most influential feature",
    "Low sensitivity suggests stable explanations under perturbations"
  ],
  "createdAt": "2025-01-15T10:30:00Z"
}
```

---

### 5. Analytics API

#### Dashboard Statistics
```
GET /api/v1/analytics/dashboard
Authorization: Bearer <token>

Response (200 OK):
{
  "period": {
    "from": "2025-01-01T00:00:00Z",
    "to": "2025-01-31T23:59:59Z"
  },
  "summary": {
    "totalTransactions": 1000000,
    "totalFraudulent": 2345,
    "fraudRate": 0.2345,
    "totalAmountProcessed": 125000000.00,
    "fraudulentAmount": 1250000.00
  },
  "modelComparison": {
    "ruleBased": {
      "precision": 0.75,
      "recall": 0.65,
      "f1Score": 0.70
    },
    "logisticRegression": {
      "precision": 0.82,
      "recall": 0.71,
      "f1Score": 0.76
    },
    "xgboost": {
      "precision": 0.89,
      "recall": 0.78,
      "f1Score": 0.83
    },
    "neuralNetwork": {
      "precision": 0.87,
      "recall": 0.82,
      "f1Score": 0.84
    }
  },
  "detectionTrends": {
    "byDay": [
      {
        "date": "2025-01-01",
        "fraudulent": 75,
        "legitimate": 41000,
        "fraudRate": 0.18
      }
    ]
  }
}
```

#### Feature Importance Comparison
```
GET /api/v1/analytics/feature-importance
Authorization: Bearer <token>

Response (200 OK):
{
  "features": [
    {
      "name": "amount",
      "ruleBased": 0.95,
      "logisticRegression": 0.78,
      "xgboost": 0.92,
      "neuralNetwork": 0.88,
      "averageImportance": 0.88,
      "stabilityScore": 0.94
    },
    {
      "name": "merchant",
      "ruleBased": 0.85,
      "logisticRegression": 0.65,
      "xgboost": 0.75,
      "neuralNetwork": 0.72,
      "averageImportance": 0.74,
      "stabilityScore": 0.88
    }
  ]
}
```

---

### 6. Audit & Compliance API

#### Get Audit Logs
```
GET /api/v1/audit/logs?action=LOGIN&from=2025-01-01&to=2025-01-31&page=0&size=50
Authorization: Bearer <token>
Role: ADMIN

Response (200 OK):
{
  "content": [
    {
      "id": 1,
      "userId": 1,
      "username": "analyst@bank.com",
      "action": "LOGIN",
      "resourceType": "USER_AUTH",
      "resourceId": "1",
      "details": {
        "ipAddress": "192.168.1.100",
        "userAgent": "Mozilla/5.0..."
      },
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ],
  "totalElements": 150
}
```

#### Generate Compliance Report
```
GET /api/v1/compliance/report?type=GDPR&from=2025-01-01&to=2025-01-31
Authorization: Bearer <token>
Role: ADMIN

Response (200 OK):
{
  "reportType": "GDPR",
  "period": {
    "from": "2025-01-01",
    "to": "2025-01-31"
  },
  "sections": {
    "dataProcessing": {
      "totalRecordsProcessed": 1000000,
      "dataRetention": "30 days",
      "anonymizationStatus": "COMPLIANT"
    },
    "rightToExplanation": {
      "explanationsGenerated": 2345,
      "averageGenerationTime": 125,
      "userSatisfaction": 0.87
    },
    "modelAudit": {
      "modelVersionsDeployed": 5,
      "biasAuditCompleted": true,
      "lastAuditDate": "2025-01-10T00:00:00Z"
    }
  }
}
```

---

## Security Architecture

### Authentication Flow

```
┌─────────┐                                      ┌──────────┐
│ Client  │                                      │  Server  │
└────┬────┘                                      └────┬─────┘
     │                                                │
     │  1. POST /auth/login                          │
     │  {username, password}                         │
     │──────────────────────────────────────────────>│
     │                                                │ Validate credentials
     │                                                │ Hash password
     │                                                │ Check RBAC
     │                                                │
     │  2. JWT Token + Refresh Token                 │
     │<──────────────────────────────────────────────│
     │                                                │
     │  3. Store token (HttpOnly cookie)             │
     │                                                │
     │  4. GET /api/transactions                     │
     │  Authorization: Bearer <JWT>                  │
     │──────────────────────────────────────────────>│
     │                                                │ Validate signature
     │                                                │ Check expiration
     │                                                │ Verify RBAC claims
     │                                                │
     │  5. Response (200 OK)                         │
     │<──────────────────────────────────────────────│
     │                                                │
     │  6. Token expires (after 24h)                 │
     │                                                │
     │  7. POST /auth/refresh                        │
     │  Authorization: Bearer <RefreshToken>         │
     │──────────────────────────────────────────────>│
     │                                                │ Validate refresh token
     │                                                │ Issue new JWT
     │                                                │
     │  8. New JWT Token                             │
     │<──────────────────────────────────────────────│
```

### JWT Token Structure

```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "1",
  "username": "analyst@bank.com",
  "role": "ANALYST",
  "permissions": ["READ_TRANSACTIONS", "VIEW_EXPLANATIONS"],
  "iat": 1642254600,
  "exp": 1642341000
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
```

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **ADMIN** | All permissions |
| **ANALYST** | READ_TRANSACTIONS, VIEW_PREDICTIONS, VIEW_EXPLANATIONS, EXPORT_RESULTS |
| **VIEWER** | READ_TRANSACTIONS, VIEW_PREDICTIONS |
| **AUDITOR** | READ_AUDIT_LOGS, VIEW_COMPLIANCE_REPORTS |

---

## Data Flow Diagrams

### 1. Transaction Ingestion & Prediction Flow

```
1. Transaction arrives
   ├─ Validate format
   ├─ Check for duplicates
   ├─ Enrich with features
   └─ Store in PostgreSQL
                │
                ▼
2. Call ML Service (gRPC)
   ├─ Rule-based detector → Prediction + Confidence
   ├─ Logistic Regression → Probability
   ├─ XGBoost → Probability
   └─ Neural Network → Probability
                │
                ▼
3. Aggregate Predictions
   ├─ Ensemble method (voting/average)
   ├─ Determine final prediction
   └─ Calculate overall confidence
                │
                ▼
4. Generate Explanations
   ├─ Call SHAP explainer
   ├─ Call LIME explainer
   ├─ Calculate stability
   └─ Store explanations
                │
                ▼
5. Audit & Response
   ├─ Log transaction processing
   ├─ Record predictions
   ├─ Alert if fraudulent
   └─ Return to client
```

### 2. Model Comparison & Evaluation Flow

```
Evaluation Dataset
   │
   ├─ Split into train/test
   │
   ▼
1. Train Models
   ├─ Rule-based (no training)
   ├─ Logistic Regression (sklearn)
   ├─ XGBoost (xgboost)
   └─ Neural Network (TensorFlow/PyTorch)
         │
         ▼
2. Evaluate Models
   ├─ Compute metrics (Accuracy, Precision, Recall, F1, AUC)
   ├─ Generate confusion matrices
   └─ Store model versions
         │
         ▼
3. Stability Analysis
   ├─ Perturbation-based stability
   ├─ Sensitivity analysis
   └─ Ranking consistency
         │
         ▼
4. Generate Reports
   ├─ Model comparison table
   ├─ Performance charts
   └─ Stability findings
```

---

## Database Schema

### Core Tables Relationship

```
┌──────────────────┐
│     Users        │
├──────────────────┤
│ id (PK)          │
│ username         │
│ email            │
│ password_hash    │
│ role             │
│ is_active        │
└────────┬─────────┘
         │ (1:N)
         │
┌────────▼──────────────────┐
│  AuditLogs                 │
├────────────────────────────┤
│ id (PK)                    │
│ user_id (FK)               │
│ action                     │
│ resource_type              │
│ timestamp                  │
└────────────────────────────┘

┌────────────────────┐
│  Transactions      │
├────────────────────┤
│ id (PK)            │
│ transaction_id     │
│ amount             │
│ merchant           │
│ transaction_date   │
│ features...        │
└────────┬───────────┘
         │ (1:1)
         │
┌────────▼──────────────────────┐
│ FraudPredictions               │
├────────────────────────────────┤
│ id (PK)                        │
│ transaction_id (FK)            │
│ rule_based_prediction          │
│ logistic_regression_prediction │
│ xgboost_prediction             │
│ neural_network_prediction      │
│ final_prediction               │
│ final_confidence               │
└────────┬──────────────────────┘
         │ (1:N)
         │
┌────────▼──────────────────┐
│  Explanations              │
├────────────────────────────┤
│ id (PK)                    │
│ prediction_id (FK)         │
│ model_type                 │
│ explanation_type (SHAP|LIME)│
│ feature_importance_json    │
│ stability_score            │
└────────────────────────────┘
```

---

## Deployment Architecture

### Development Environment

```
Developer Machine
├── PostgreSQL (local or Docker)
├── Python ML Service (local)
├── Java Backend (Spring Boot)
└── React Frontend (npm dev server)
```

### Staging Environment

```
Docker Compose
├── PostgreSQL Container
├── Python ML Service Container
├── Java Backend Container
└── React Frontend Container
```

### Production Environment

```
Kubernetes Cluster
├── PostgreSQL StatefulSet
├── Python ML Service Deployment (scaled)
├── Java Backend Deployment (scaled)
├── React Frontend Deployment
├── Ingress Controller (nginx)
├── Service Mesh (Istio)
├── Prometheus + Grafana (monitoring)
└── ELK Stack (logging)
```

---

## Monitoring & Observability

### Key Metrics

```
Application Metrics:
├── Request latency (95th, 99th percentile)
├── Error rates by endpoint
├── JWT validation success rate
├── Model inference latency
└── Cache hit rate

Business Metrics:
├── Fraud detection rate
├── False positive rate
├── True positive rate
├── Cost of missed fraud
└── Explanation generation rate

Security Metrics:
├── Failed authentication attempts
├── Unauthorized API calls
├── Audit log volume
└── Data access patterns
```

### Logging Strategy

```
Logs captured:
├── Authentication events (success/failure)
├── API requests/responses (redacted)
├── ML model predictions
├── Explanation generation
├── Database operations
├── Security events
└── Audit trails (immutable)

Log aggregation:
└─ ELK Stack (Elasticsearch, Logstash, Kibana)
```

---

## Testing Strategy

### Unit Testing
- Service layer business logic
- Utility function validation
- Repository mock tests

### Integration Testing
- API endpoint tests
- Database integration
- ML service communication
- Cache behavior

### End-to-End Testing
- Full transaction flow
- Authentication to prediction
- Explanation generation pipeline
- Export functionality

### Performance Testing
- Inference latency under load
- Database query optimization
- Cache effectiveness
- API throughput

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Active
