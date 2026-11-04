"""FastAPI entry point for the ML service."""
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.schemas import PredictionRequest, PredictionResponse, HealthResponse
from services.prediction_service import PredictionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(
    title="Fraud Detection ML Service",
    description="ML inference and XAI (SHAP/LIME) explanation service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

prediction_service = PredictionService()


@app.on_event("startup")
async def startup_event():
    prediction_service.load_models()



@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    return HealthResponse(status="ok", models_loaded=prediction_service.models_loaded)



@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(request: PredictionRequest):
    return prediction_service.predict(request)



@app.post("/explain/shap", tags=["Explainability"])
def explain_shap(request: PredictionRequest):
    """Generate SHAP feature attributions for a transaction."""
    return prediction_service.explain_shap(request)


@app.post("/explain/lime", tags=["Explainability"])
def explain_lime(request: PredictionRequest):
    """Generate LIME local explanation for a transaction."""
    return prediction_service.explain_lime(request)


@app.post("/explain/stability", tags=["Explainability"])
def explain_stability(request: PredictionRequest):
    """Analyse explanation stability under perturbations (RQ2)."""
    return prediction_service.explain_stability(request)



@app.get("/models/metrics", tags=["Metrics"])
def get_model_metrics():
    return prediction_service.get_metrics()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.REST_PORT, reload=False)
