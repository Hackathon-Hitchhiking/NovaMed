from __future__ import annotations

import io
import os
import uuid
from pathlib import Path
from typing import Optional

from errors.errors import ErrBadRequest
from repositories.minio import MinioRepository
from schemas.minio import MinioContentType
from configs.Minio import base_bucket, get_minio_client


class StorageClient:
    async def upload_bytes(
        self,
        data: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> str:
        raise NotImplementedError


class MinioStorage(StorageClient):
    def __init__(self, bucket: str = base_bucket) -> None:
        self.bucket = bucket
        self._repo = MinioRepository(client=get_minio_client())

    async def upload_bytes(
        self,
        data: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> str:
        ct = _to_minio_content_type(filename, content_type)
        ext = _guess_extension(filename, content_type)
        key = f"uploads/{uuid.uuid4().hex}{ext}"
        self._repo.create_object_from_byte(
            object_path=key,
            file=io.BytesIO(data),
            content_type=ct,
        )
        return f"minio://{self.bucket}/{key}"


class FileStorage(StorageClient):
    """
    Legacy local stub that writes to .storage and returns s3-style URL.
    Kept for backward compatibility if needed.
    """

    def __init__(self, bucket: str = "nova-med", root: str | Path = ".storage") -> None:
        self.bucket = bucket
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    async def upload_bytes(
        self,
        data: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> str:
        ext = _guess_extension(filename, content_type)
        key = f"uploads/{uuid.uuid4().hex}{ext}"
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return f"s3://{self.bucket}/{key}"


def _guess_extension(filename: Optional[str], content_type: Optional[str]) -> str:
    if filename and "." in filename:
        return os.path.splitext(filename)[1]
    mapping = {
        "image/png": ".png",
        "image/jpeg": ".jpeg",
        "video/mp4": ".mp4",
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    }
    return mapping.get(content_type or "", "")


def _to_minio_content_type(
    filename: Optional[str], content_type: Optional[str]
) -> MinioContentType:
    mapping: dict[str, MinioContentType] = {
        "image/png": MinioContentType.PNG,
        "image/jpeg": MinioContentType.JPEG,
        "video/mp4": MinioContentType.MP4,
        "application/pdf": MinioContentType.PDF,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": MinioContentType.DOCX,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": MinioContentType.PPTX,
    }
    if content_type in mapping:
        return mapping[content_type]  # type: ignore[index]

    ext = os.path.splitext(filename)[1].lower() if filename else ""
    ext_map: dict[str, MinioContentType] = {
        ".png": MinioContentType.PNG,
        ".jpeg": MinioContentType.JPEG,
        ".jpg": MinioContentType.JPEG,
        ".mp4": MinioContentType.MP4,
        ".pdf": MinioContentType.PDF,
        ".docx": MinioContentType.DOCX,
        ".pptx": MinioContentType.PPTX,
    }
    if ext in ext_map:
        return ext_map[ext]
    raise ErrBadRequest(
        f"Unsupported content-type: {content_type} (filename={filename})"
    )
