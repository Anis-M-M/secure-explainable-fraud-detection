import os

REST_PORT = int(os.getenv("REST_PORT", "8001"))
MODEL_DIR = os.getenv(
    "MODEL_DIR",
    os.path.join(os.path.dirname(__file__), "..", "models", "saved"),
)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class Settings:
    REST_PORT: int = REST_PORT
    MODEL_DIR: str = MODEL_DIR
    LOG_LEVEL: str = LOG_LEVEL


settings = Settings()
