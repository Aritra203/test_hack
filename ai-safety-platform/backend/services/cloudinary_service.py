from __future__ import annotations

import base64
from dataclasses import dataclass

import cloudinary.uploader
from fastapi import UploadFile

from backend.config.settings import settings


@dataclass
class CloudinaryUploadResult:
    url: str
    public_id: str
    resource_type: str
    content: bytes


class CloudinaryUploadService:
    async def upload_fastapi_file(
        self,
        file: UploadFile,
        folder_override: str | None = None,
    ) -> CloudinaryUploadResult:
        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty.")

        max_size = settings.max_upload_mb * 1024 * 1024
        if len(content) > max_size:
            raise ValueError(f"File exceeds maximum upload limit of {settings.max_upload_mb} MB.")

        content_type = file.content_type or "application/octet-stream"
        data_uri = f"data:{content_type};base64,{base64.b64encode(content).decode('utf-8')}"
        response = cloudinary.uploader.upload(
            data_uri,
            folder=folder_override or settings.cloudinary_folder,
            resource_type="auto",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )

        secure_url = response.get("secure_url")
        public_id = response.get("public_id")
        if not secure_url or not public_id:
            raise RuntimeError("Cloudinary upload failed: missing secure_url or public_id.")

        return CloudinaryUploadResult(
            url=secure_url,
            public_id=public_id,
            resource_type=str(response.get("resource_type", "raw")),
            content=content,
        )


cloudinary_upload_service = CloudinaryUploadService()

