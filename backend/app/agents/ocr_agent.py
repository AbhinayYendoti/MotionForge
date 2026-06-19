from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.schemas.pipeline import Bounds, OcrImage, OcrResult, OcrWord
from app.services.image_utils import image_size, public_path_from_url, to_vision_url


# ── NVIDIA vision-model OCR schema ─────────────────────────────────────────────

class _NvidiaOcrWord(BaseModel):
    text: str
    x: float = Field(ge=0, default=0)
    y: float = Field(ge=0, default=0)
    width: float = Field(ge=1, default=50)
    height: float = Field(ge=1, default=20)
    confidence: float = Field(ge=0, le=1, default=0.85)


class _NvidiaOcrResponse(BaseModel):
    words: list[_NvidiaOcrWord] = Field(default_factory=list)
    fullText: str = ""


async def _run_nvidia_ocr(image_url: str, img_w: int, img_h: int) -> OcrResult:
    """Fallback OCR using the NVIDIA vision model — works for remote images too."""
    from app.services.nvidia_client import nvidia_chat_json

    vision_url = to_vision_url(image_url)
    result: _NvidiaOcrResponse = await nvidia_chat_json(
        model=settings.nvidia_vision_model,
        schema=_NvidiaOcrResponse,
        temperature=0.05,
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an OCR agent. Extract all visible text from the image "
                    "with approximate pixel-level bounding boxes. Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Image dimensions: {img_w}×{img_h} pixels. "
                            "Extract ALL visible text. For each distinct word or short phrase return: "
                            "text (the string), x (left edge px), y (top edge px), "
                            "width (approx px), height (approx px), confidence (0–1). "
                            "Also return fullText as one concatenated string."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": vision_url}},
                ],
            },
        ],
    )

    words = [
        OcrWord(
            text=w.text,
            confidence=w.confidence,
            bounds=Bounds(x=w.x, y=w.y, width=w.width, height=w.height),
        )
        for w in result.words
        if len(w.text.strip()) > 1
    ]

    return OcrResult(
        image=OcrImage(width=img_w, height=img_h),
        text=result.fullText or " ".join(w.text for w in words),
        words=words,
    )


# ── Main agent ─────────────────────────────────────────────────────────────────

async def run_ocr_agent(image_url: str) -> OcrResult:
    path = public_path_from_url(image_url)
    img_w, img_h = image_size(path)

    # ── Attempt 1: local pytesseract (fast, offline) ───────────────────────
    if path and path.exists():
        try:
            import pytesseract  # type: ignore
            from PIL import Image

            with Image.open(path) as image:
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                words = []
                for idx, raw_text in enumerate(data.get("text", [])):
                    text = str(raw_text).strip()
                    raw_conf = str(data["conf"][idx])
                    confidence = float(raw_conf) if raw_conf.replace(".", "", 1).lstrip("-").isdigit() else -1
                    if len(text) <= 1 or confidence <= 0:
                        continue
                    words.append(
                        OcrWord(
                            text=text,
                            confidence=min(1.0, max(0.0, confidence / 100)),
                            bounds=Bounds(
                                x=data["left"][idx],
                                y=data["top"][idx],
                                width=data["width"][idx],
                                height=data["height"][idx],
                            ),
                        )
                    )
                if words:
                    return OcrResult(
                        image=OcrImage(width=img_w, height=img_h),
                        text=" ".join(w.text for w in words),
                        words=words,
                    )
        except Exception as err:
            logger.warning("pytesseract OCR failed; trying NVIDIA vision OCR", extra={"error": str(err)})

    # ── Attempt 2: NVIDIA vision model OCR (works for remote URLs too) ────
    try:
        result = await _run_nvidia_ocr(image_url, img_w, img_h)
        if result.words:
            logger.info("NVIDIA vision OCR succeeded", extra={"word_count": len(result.words)})
            return result
    except Exception as err:
        logger.warning("NVIDIA vision OCR failed; continuing with empty OCR", extra={"error": str(err)})

    # ── Fallback: empty OCR ────────────────────────────────────────────────
    return OcrResult(
        image=OcrImage(width=img_w, height=img_h),
        text="",
        words=[],
        warning="All OCR methods failed; pipeline continued with empty text extraction.",
    )
