"""File upload storage — local disk (dev) or rejected in production.

In production (UPLOADTHING_SECRET set), all image uploads must go through the
UploadThing client on the frontend. The backend accepts the resulting CDN URL
via the ``imageUrl`` form field; raw file uploads are explicitly rejected to
prevent silent failures on Render's ephemeral filesystem.

In development (no UPLOADTHING_SECRET), raw file uploads are stored in
``public/uploads/`` as before.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image

from app.core.config import REPO_ROOT, settings
from app.database import models

ALLOWED_IMAGE_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
MAX_UPLOAD_BYTES = 12 * 1024 * 1024  # 12 MB


async def store_upload(file: UploadFile) -> dict:
    """Save an uploaded image and return metadata.

    Raises HTTPException(400) in production where local storage is unavailable.
    """
    # ── Production guard ──────────────────────────────────────────────────────
    if settings.uploadthing_secret:
        raise HTTPException(
            status_code=400,
            detail=(
                "Direct file uploads are disabled in production. "
                "Upload your image via the UploadThing widget and pass the returned URL "
                "as the 'imageUrl' field instead."
            ),
        )

    # ── Dev-only: write to local public/uploads/ ───────────────────────────────
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Upload must be a PNG, JPEG, or WEBP image.")

    data = await file.read()
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload must be between 1 byte and 12 MB.")

    upload_dir = REPO_ROOT / settings.upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_id = models.cuid()
    suffix = ALLOWED_IMAGE_TYPES[file.content_type]
    file_name = f"{upload_id}{suffix}"
    path = upload_dir / file_name
    path.write_bytes(data)

    width: int | None = None
    height: int | None = None
    try:
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
    except Exception:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Uploaded file is not a valid image.")

    return {
        "image_url": f"/uploads/{file_name}",
        "file_name": file.filename or file_name,
        "mime_type": file.content_type,
        "width": width,
        "height": height,
        "size": len(data),
    }
