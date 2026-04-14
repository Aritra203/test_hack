from __future__ import annotations

import base64
from dataclasses import dataclass
from importlib import import_module

from fastapi import HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from backend.config.settings import settings


@dataclass
class CloudinaryUploadResult:
    url: str
    public_id: str
    resource_type: str
    original_filename: str | None


class CloudinaryUploadService:
    async def upload_fastapi_file(
        self,
        file: UploadFile,
        folder_override: str | None = None,
    ) -> CloudinaryUploadResult:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        max_upload_bytes = settings.max_upload_mb * 1024 * 1024
        if len(file_bytes) > max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds {settings.max_upload_mb} MB upload limit.",
            )

        content_type = file.content_type or "application/octet-stream"
        folder = folder_override or settings.cloudinary_folder

        upload_result = await run_in_threadpool(
            self._upload_bytes,
            file_bytes,
            content_type,
            folder,
        )

        secure_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        if not secure_url or not public_id:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Cloudinary upload failed to return required metadata.",
            )

        return CloudinaryUploadResult(
            url=secure_url,
            public_id=public_id,
            resource_type=str(upload_result.get("resource_type", "raw")),
            original_filename=file.filename,
        )

    @staticmethod
    def _upload_bytes(file_bytes: bytes, content_type: str, folder: str) -> dict:
        try:
            uploader = import_module("cloudinary.uploader")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "cloudinary SDK is not installed. Install backend requirements before uploading evidence."
            ) from exc

        data_uri = f"data:{content_type};base64,{base64.b64encode(file_bytes).decode('utf-8')}"
        return uploader.upload(
            data_uri,
            folder=folder,
            resource_type="auto",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )


cloudinary_upload_service = CloudinaryUploadService()
