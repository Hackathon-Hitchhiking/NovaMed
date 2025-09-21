from functools import lru_cache

from pydantic_settings import BaseSettings


class EnvironmentSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    DEBUG: bool

    MINIO_HOST: str
    MINIO_ACCESS: str
    MINIO_SECRET: str
    MINIO_BASE_BUCKET: str
    MINIO_SECURE: bool

    # External Medical Service (RAG/ML) configuration
    MEDICAL_SERVICE_URL: str = "http://ml:8000"
    ML_SEARCH_TOP_K: int | None = None
    ML_HTTP_TIMEOUT: float = 15.0

    class Config:
        env_file = "configs/.env"
        env_file_encoding = "utf-8"


@lru_cache
def get_environment_variables() -> EnvironmentSettings:
    return EnvironmentSettings()
