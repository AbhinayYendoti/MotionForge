"""UploadThing server-side upload helper (synchronous, pure-httpx).

Called from the render worker after Remotion writes a local MP4.
Uploads the file to UploadThing CDN and returns the public URL.

Flow:
    1. POST /v6/uploadFiles  → get S3 presigned URL + file key
    2. PUT  presignedUrl     → stream file bytes to S3
    3. POST pollingUrl       → confirm completion with UploadThing
    4. Return https://utfs.io/f/<key>
"""
from __future__ import annotations

import mimetypes
from pathlib import Path

import httpx

from app.core.logging import logger

_UT_API_BASE = "https://api.uploadthing.com"

_EXT_TO_MIME: dict[str, str] = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def upload_file_to_ut(secret: str, path: Path, file_name: str | None = None) -> str:
    """Upload a local file to UploadThing CDN and return the public URL.

    Args:
        secret:    UPLOADTHING_SECRET (``sk_live_...`` / ``sk_test_...``).
        path:      Absolute path to the file on disk.
        file_name: Override for the stored file name. Defaults to ``path.name``.

    Returns:
        The permanent CDN URL, e.g. ``https://utfs.io/f/<key>``.

    Raises:
        RuntimeError: On any HTTP or API-level failure.
    """
    name = file_name or path.name
    size = path.stat().st_size
    suffix = path.suffix.lower()
    content_type = _EXT_TO_MIME.get(suffix) or mimetypes.guess_type(name)[0] or "application/octet-stream"

    api_headers = {
        "x-uploadthing-api-key": secret,
        "Content-Type": "application/json",
    }

    # Use a long timeout: large MP4 PUT can take time.
    with httpx.Client(timeout=httpx.Timeout(connect=15, read=300, write=300, pool=15)) as client:

        # ── Step 1: Request pre-signed upload URL from UploadThing ──────────
        logger.info(
            "Requesting UploadThing presigned URL",
            extra={"file_name": name, "size_bytes": size, "content_type": content_type},
        )
        prepare = client.post(
            f"{_UT_API_BASE}/v6/uploadFiles",
            headers=api_headers,
            json={
                "files": [{"name": name, "size": size, "type": content_type}],
                "acl": "public-read",
                "contentDisposition": "inline",
            },
        )
        if not prepare.is_success:
            raise RuntimeError(
                f"UploadThing prepare request failed [{prepare.status_code}]: "
                f"{prepare.text[:400]}"
            )

        payload = prepare.json()
        try:
            file_info: dict = payload["data"][0]
            key: str = file_info["key"]
            presigned_urls: list[str] = file_info["presignedUrls"]
            # fileUrl may already be returned by the API (v6 sometimes includes it)
            cdn_url: str = file_info.get("fileUrl") or f"https://ufs.sh/f/{key}"
            polling_url: str | None = file_info.get("pollingUrl")
            polling_jwt: str | None = file_info.get("pollingJwt")
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"UploadThing returned unexpected response structure: {payload!r}"
            ) from exc

        if not presigned_urls:
            raise RuntimeError("UploadThing returned no presigned URLs.")

        # ── Step 2: PUT file bytes to S3 pre-signed URL ──────────────────────
        logger.info("Uploading file to S3 via UploadThing presigned URL", extra={"key": key})
        file_bytes = path.read_bytes()
        put_resp = client.put(
            presigned_urls[0],
            content=file_bytes,
            headers={"Content-Type": content_type},
        )
        if not put_resp.is_success:
            raise RuntimeError(
                f"S3 upload failed [{put_resp.status_code}]: {put_resp.text[:200]}"
            )

        # ── Step 3: Confirm upload completion with UploadThing ───────────────
        if polling_url and polling_jwt:
            try:
                confirm = client.post(
                    polling_url,
                    headers=api_headers,
                    json={"jwt": polling_jwt},
                    timeout=30,
                )
                if not confirm.is_success:
                    logger.warning(
                        "UploadThing polling confirmation returned non-success (non-fatal)",
                        extra={"status": confirm.status_code, "body": confirm.text[:200]},
                    )
            except Exception as exc:
                # Non-fatal: the file is already on S3; CDN propagation will occur.
                logger.warning(
                    "UploadThing polling confirmation failed (non-fatal)",
                    extra={"error": str(exc)},
                )

    logger.info(
        "File successfully uploaded to UploadThing",
        extra={"file_name": name, "size_bytes": size, "cdn_url": cdn_url},
    )
    return cdn_url
