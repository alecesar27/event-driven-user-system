# core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    JWT_SECRET: str = Field("secret", env="JWT_SECRET")
    KAFKA_BROKER: str = Field("localhost:9092", env="KAFKA_BROKER")
    METRICS_PORT: int = Field(8001, env="METRICS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
