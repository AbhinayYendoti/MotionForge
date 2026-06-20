import base64
import io
from pathlib import Path

import httpx
from PIL import Image

from app.core.config import REPO_ROOT, settings


def public_path_from_url(image_url: str) -> Path | None:
    if image_url.startswith("/"):
        return REPO_ROOT / "public" / image_url.lstrip("/")
    if image_url.startswith(settings.app_url):
        suffix = image_url.removeprefix(settings.app_url).lstrip("/")
        return REPO_ROOT / suffix
    return None


def _download_image_bytes(image_url: str) -> bytes | None:
    """Download a remote image and return its raw bytes.
    Returns None on any failure so callers can fall back gracefully.
    """
    try:
        with httpx.Client(timeout=httpx.Timeout(connect=10, read=30, write=10, pool=5)) as client:
            response = client.get(image_url, follow_redirects=True)
            response.raise_for_status()
            return response.content
    except Exception:
        return None


def image_size(path: Path | None, image_url: str | None = None) -> tuple[int, int]:
    """Return (width, height) of an image.

    Tries in order:
    1. Local file path (fast, no network)
    2. Remote URL download (production CDN images)
    3. Safe fallback of 1080×1080
    """
    if path and path.exists():
        with Image.open(path) as image:
            return image.size

    if image_url and image_url.startswith("http"):
        raw = _download_image_bytes(image_url)
        if raw:
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    return image.size
            except Exception:
                pass

    return 1080, 1080


def to_vision_url(image_url: str) -> str:
    """Convert an image URL to a base64 data URI for NVIDIA vision models.

    Priority:
    1. Local file → encode directly (fast, no network).
    2. Remote CDN URL → download bytes then encode (fixes UploadThing URLs
       that NVIDIA cannot load directly from its sandboxed environment).
    3. Pass-through if download fails (NVIDIA will try the URL itself).
    """
    # ── Attempt 1: local file ─────────────────────────────────────────────
    path = public_path_from_url(image_url)
    if path and path.exists():
        suffix = path.suffix.lower()
        mime = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/webp" if suffix == ".webp" else "image/png"
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"

    # ── Attempt 2: remote URL (production CDN) ────────────────────────────
    if image_url.startswith("http"):
        raw = _download_image_bytes(image_url)
        if raw:
            # Detect mime type from the bytes themselves using Pillow
            try:
                with Image.open(io.BytesIO(raw)) as img:
                    fmt = (img.format or "PNG").upper()
                    mime_map = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
                    mime = mime_map.get(fmt, "image/png")
            except Exception:
                mime = "image/png"
            return f"data:{mime};base64,{base64.b64encode(raw).decode()}"

    # ── Fallback: return URL unchanged, let NVIDIA try it directly ────────
    return image_url
