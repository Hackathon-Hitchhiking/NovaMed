from __future__ import annotations

import httpx

from configs.Environment import get_environment_variables


env = get_environment_variables()

# A single configured AsyncClient for the external Medical Service
ml_http_client = httpx.AsyncClient(
    base_url=env.MEDICAL_SERVICE_URL.rstrip("/"),
    timeout=float(env.ML_HTTP_TIMEOUT),
)


def get_ml_http_client() -> httpx.AsyncClient:
    return ml_http_client

