from __future__ import annotations

import base64
import json
from typing import List, Optional, Tuple

import httpx
from loguru import logger

from configs.ML import get_ml_http_client
from services.storage import MinioStorage, StorageClient
from schemas.anamnesis import AnamnesisIn
from schemas.prediction import (
    DiagnosisSuggestionOut,
    ReferralSuggestionOut,
    PredictionsOut,
)


class MLClient:
    """
    HTTP client for the external Medical Service RAG search.

    Integration details:
    - Endpoint: POST {BASE_URL}/v1/search
    - Request body (subset used):
        { anamnesis: str, image_base64?: str, image_mime_type?: str, top_k?: int }
    - Response body: { suggestions: [...], referrals: [...] }

    Configuration:
    - Base URL is taken from one of the env vars (first present wins):
        MEDICAL_SERVICE_URL, RAG_SERVICE_URL, ML_SERVICE_URL
      Fallback: http://ml:8000
    - Optional: ML_SEARCH_TOP_K to override top_k, if set.
    """

    def __init__(
        self,
        *,
        storage: Optional[StorageClient] = None,
        top_k: int = 5,
    ) -> None:
        # Use configured httpx client from configs/ML.py
        self._client = get_ml_http_client()
        self._top_k = top_k

        # Storage for optional exam image retrieval
        self._storage: StorageClient = storage or MinioStorage()

    async def predict(
        self,
        anamnesis: AnamnesisIn,
        exam_path: Optional[str] = None,
    ) -> Tuple[List[DiagnosisSuggestionOut], List[ReferralSuggestionOut]]:
        payload: dict[str, object] = {
            "anamnesis": self._anamnesis_to_text(anamnesis),
        }

        # Optional image attachment if we can resolve bytes from Minio
        if exam_path:
            try:
                img_base64, img_mime = await self._maybe_fetch_image(exam_path)
                if img_base64:
                    payload["image_base64"] = img_base64
                if img_mime:
                    payload["image_mime_type"] = img_mime
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Failed to attach exam image to search payload: path={} err={}",
                    exam_path,
                    exc,
                )

        # Respect optional top_k override via env
        # Optional top_k override via environment config
        if self._top_k is not None:
            try:
                payload["top_k"] = self._top_k
            except (TypeError, ValueError):
                logger.debug("Invalid ML_SEARCH_TOP_K value: {}", self._top_k)

        logger.debug("ML search request path=/v1/search payload={}", payload)

        try:
            resp = await self._client.post("/v1/search", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.error("ML search request failed: path=/v1/search err={}", exc)
            return [], []
        except ValueError as exc:
            logger.error("ML search response is not JSON: path=/v1/search err={}", exc)
            return [], []
        
        logger.debug(f"ML search response {data}")

        # Parse and validate via Pydantic schema
        try:
            parsed = PredictionsOut.model_validate(data)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("ML search response validation failed: err={}", exc)
            return [], []

        # Deduplicate referrals by (specialty, note) while preserving order
        seen = set()
        dedup_referrals: List[ReferralSuggestionOut] = []
        for r in parsed.referrals:
            key = (r.specialty, r.note)
            if key in seen:
                continue
            seen.add(key)
            dedup_referrals.append(r)

        return list(parsed.suggestions), dedup_referrals

    def _anamnesis_to_text(self, anamnesis: AnamnesisIn) -> str:
        """Convert structured AnamnesisIn into a textual string for RAG search.

        Keeps it simple and robust by serialising non-empty fields to JSON.
        """
        try:
            data = anamnesis.model_dump(exclude_none=True)
            if not data:
                return ""
            return json.dumps(data, ensure_ascii=False)
        except Exception:  # pragma: no cover - defensive
            return ""

    async def _maybe_fetch_image(self, s3_path: str) -> tuple[Optional[str], Optional[str]]:
        """Try to fetch an image referred by a minio-style URL and return base64 and mime.

        Accepted formats are typical images (png, jpg, jpeg, webp, bmp, tiff).
        Returns (None, None) if path cannot be resolved or is not an image.
        """
        # Infer mime from extension; only include images
        mime = self._guess_mime_from_key(s3_path)
        if not mime or not mime.startswith("image/"):
            return None, None

        try:
            content = await self._storage.get_bytes(s3_path)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug(
                "Failed to download image from storage: path={} err={}",
                s3_path,
                exc,
            )
            return None, None

        encoded = base64.b64encode(content).decode("ascii")
        return encoded, mime

    @staticmethod
    def _guess_mime_from_key(key: str) -> Optional[str]:
        lower = key.lower()
        mapping = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
        }
        for ext, mime in mapping.items():
            if lower.endswith(ext):
                return mime
        return None
