from typing import Optional

from pydantic import BaseModel


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class CamelModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = to_camel


class PredictionRequest(CamelModel):
    transaction_id: str
    amount: float
    merchant: Optional[str] = None
    merchant_category: Optional[str] = None
    user_age: Optional[int] = None
    user_location: Optional[str] = None
    device_type: Optional[str] = None


class PredictionResponse(CamelModel):
    rule_based_prediction: int
    rule_based_confidence: float
    logistic_regression_prediction: int
    logistic_regression_probability: float
    xgboost_prediction: int
    xgboost_probability: float
    neural_network_prediction: int
    neural_network_probability: float
    final_prediction: int
    final_confidence: float
    model_version: str
    inference_time_ms: int


class HealthResponse(CamelModel):
    status: str
    models_loaded: bool
