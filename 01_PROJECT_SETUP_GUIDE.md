# Project Setup Guide

Anis Mohammed Metkari & Sharwari Rajendra Nimbalkar  
Supervisor: Irina Tal

---

## Overview

The system has three main components talking to each other:
- Java Spring Boot backend handling auth, transaction storage and routing requests to the ML service
- Python FastAPI service doing the actual model inference and generating SHAP/LIME explanations
- React frontend for the dashboard and visualisations
- PostgreSQL for storing everything

```
React (port 3000)
       |
Spring Boot API (port 8080)
       |           |
  PostgreSQL    Python ML Service (port 8001)
  (port 5432)
```

---

## Prerequisites

- Java JDK 17
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+ (or just use Docker)
- Maven (the mvnw wrapper is included so you don't need to install it separately)

---

## Java Backend Setup

### Project structure

```
fraud-detection-api/
├── src/main/java/com/frauddetection/
│   ├── FraudDetectionApplication.java
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   └── MLServiceConfig.java
│   ├── controller/
│   │   ├── AuthController.java
│   │   ├── TransactionController.java
│   │   └── ExplanationController.java
│   ├── service/
│   │   ├── AuthService.java
│   │   ├── TransactionService.java
│   │   ├── ModelInferenceService.java
│   │   └── AuditService.java
│   ├── model/
│   │   ├── User.java
│   │   ├── Transaction.java
│   │   ├── FraudPrediction.java
│   │   └── AuditLog.java
│   ├── repository/
│   ├── dto/
│   └── security/
│       ├── JwtTokenProvider.java
│       └── JwtAuthenticationFilter.java
└── src/main/resources/
    ├── application.yml
    └── db/migration/
        ├── V1__init.sql
        ├── V2__auth.sql
        └── V3__audit.sql
```

### pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.frauddetection</groupId>
    <artifactId>fraud-detection-api</artifactId>
    <version>1.0.0</version>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>17</java.version>
        <jwt.version>0.12.3</jwt.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>${jwt.version}</version>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <version>${jwt.version}</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <version>${jwt.version}</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.0.2</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.security</groupId>
            <artifactId>spring-security-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### application.yml

```yaml
spring:
  application:
    name: fraud-detection-api
  datasource:
    url: jdbc:postgresql://localhost:5432/fraud_detection_db
    username: fraud_user
    password: ${DB_PASSWORD}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
  flyway:
    enabled: true
    locations: classpath:db/migration
  security:
    jwt:
      secret: ${JWT_SECRET}
      expiration: 86400000

server:
  port: 8080
  servlet:
    context-path: /api/v1
```

### Running the backend

```bash
cd fraud-detection-api
./mvnw spring-boot:run
```

---

## Python ML Service Setup

### Installing dependencies

```bash
cd ml-service
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Running the service

```bash
python src/main.py
```

The service starts on port 8001. You can check it's working at http://localhost:8001/health

### Training the models

If you need to retrain from scratch (model files are in models/saved/):

```bash
python -m training.train_models --data-path ../data/creditcard.csv
```

This trains LR, XGBoost and the neural network and saves them to models/saved/.

---

## PostgreSQL Setup

```sql
CREATE DATABASE fraud_detection_db;
CREATE USER fraud_user WITH PASSWORD 'your-db-password';
GRANT ALL PRIVILEGES ON DATABASE fraud_detection_db TO fraud_user;
\c fraud_detection_db
GRANT ALL ON SCHEMA public TO fraud_user;
```

### Schema (V1__init.sql)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'ANALYST',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    merchant VARCHAR(255),
    merchant_category VARCHAR(100),
    transaction_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fraud_predictions (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER UNIQUE NOT NULL REFERENCES transactions(id),
    rule_based_prediction INT,
    rule_based_confidence DECIMAL(5,4),
    logistic_regression_prediction INT,
    logistic_regression_probability DECIMAL(5,4),
    xgboost_prediction INT,
    xgboost_probability DECIMAL(5,4),
    neural_network_prediction INT,
    neural_network_probability DECIMAL(5,4),
    final_prediction INT NOT NULL,
    final_confidence DECIMAL(5,4) NOT NULL,
    inference_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE explanations (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER NOT NULL REFERENCES fraud_predictions(id),
    model_type VARCHAR(50) NOT NULL,
    explanation_type VARCHAR(50) NOT NULL,
    feature_importance_json JSONB,
    top_features JSONB,
    stability_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transaction_date ON transactions(transaction_date);
CREATE INDEX idx_prediction_created ON fraud_predictions(created_at);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
```

---

## React Frontend Setup

```bash
cd fraud-detection-frontend
npm install
npm run dev
```

Runs on http://localhost:5173 in development.

---

## Docker (run everything together)

```bash
docker-compose up -d
```

To stop:
```bash
docker-compose down
```

---

## Common issues

**Port 5432 in use** — change the port in docker-compose.yml or stop whatever is already using it.

**JWT validation errors** — make sure JWT_SECRET is set in your environment (see .env.example).

**ML service unreachable** — check it's running first with `curl http://localhost:8001/health`.

**CORS errors from React** — the allowed origins in SecurityConfig.java need to match where the frontend is running (localhost:3000 or 5173 depending on how you started it).

**Flyway migration fails** — usually a permissions issue on the database user. Run the GRANT commands from the setup section again.
