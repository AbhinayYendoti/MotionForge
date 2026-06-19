import base64
from pathlib import Path

from PIL import Image

from app.core.config import REPO_ROOT, settings


def public_path_from_url(image_url: str) -> Path | None:
    if image_url.startswith("/"):
        return REPO_ROOT / "public" / image_url.lstrip("/")
    if image_url.startswith(settings.app_url):
        suffix = image_url.removeprefix(settings.app_url).lstrip("/")
        return REPO_ROOT / suffix
    return None


def image_size(path: Path | None) -> tuple[int, int]:
    if not path or not path.exists():
        return 1080, 1080
    with Image.open(path) as image:
        return image.size


def to_vision_url(image_url: str) -> str:
    path = public_path_from_url(image_url)
    if not path or not path.exists():
        return image_url
    suffix = path.suffix.lower()
    mime = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/webp" if suffix == ".webp" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
