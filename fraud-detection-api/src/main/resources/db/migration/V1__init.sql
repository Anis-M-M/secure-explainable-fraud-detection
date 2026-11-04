-- V1: Initial schema

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'ANALYST',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    merchant VARCHAR(255),
    merchant_category VARCHAR(100),
    transaction_date TIMESTAMP NOT NULL,
    user_age INT,
    user_location VARCHAR(100),
    device_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fraud_predictions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT UNIQUE NOT NULL REFERENCES transactions(id),
    rule_based_prediction INT,
    rule_based_confidence DECIMAL(5, 4),
    logistic_regression_prediction INT,
    logistic_regression_probability DECIMAL(5, 4),
    xgboost_prediction INT,
    xgboost_probability DECIMAL(5, 4),
    neural_network_prediction INT,
    neural_network_probability DECIMAL(5, 4),
    final_prediction INT NOT NULL,
    final_confidence DECIMAL(5, 4) NOT NULL,
    model_version VARCHAR(50),
    inference_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE explanations (
    id BIGSERIAL PRIMARY KEY,
    prediction_id BIGINT NOT NULL REFERENCES fraud_predictions(id),
    model_type VARCHAR(50) NOT NULL,
    explanation_type VARCHAR(50) NOT NULL,
    feature_importance_json JSONB,
    top_features JSONB,
    explanation_html TEXT,
    stability_score DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    username VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX idx_transaction_date ON transactions(transaction_date);
CREATE INDEX idx_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_prediction_transaction ON fraud_predictions(transaction_id);
CREATE INDEX idx_prediction_final ON fraud_predictions(final_prediction);
CREATE INDEX idx_explanation_prediction ON explanations(prediction_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
