from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.schemas.pipeline import LayerExtraction, OcrResult
from app.services.image_utils import image_size, public_path_from_url, to_vision_url


class _ProductDetection(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(ge=1)
    height: float = Field(ge=1)
    confidence: float = Field(ge=0, le=1, default=0.7)
    label: str = "Product"


async def _detect_product_bounds_ai(image_url: str, img_w: int, img_h: int) -> _ProductDetection:
    """Use the NVIDIA vision model to locate the main product or subject in the image."""
    from app.services.nvidia_client import nvidia_chat_json

    vision_url = to_vision_url(image_url)
    if not vision_url or vision_url == image_url and not image_url.startswith("data:"):
        raise ValueError("Image is not available for vision analysis.")

    return await nvidia_chat_json(
        model=settings.nvidia_vision_model,
        schema=_ProductDetection,
        temperature=0.1,
        max_tokens=256,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an object detection agent. Identify the main product, subject, or focal element "
                    "in the image and return its bounding box in pixels. Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Image dimensions: {img_w}×{img_h} pixels. "
                            "Identify the primary product, subject, or focal element. "
                            "Return JSON with: x (left edge pixels), y (top edge pixels), "
                            "width (pixels), height (pixels), confidence (0.0-1.0), label (short name)."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": vision_url}},
                ],
            },
        ],
    )


async def run_layer_extraction_engine(image_url: str, ocr: OcrResult | None) -> LayerExtraction:
    width, height = image_size(public_path_from_url(image_url), image_url=image_url)

    # ── Attempt AI-powered product bounding box detection ─────────────────
    product_x = round(width * 0.18)
    product_y = round(height * 0.18)
    product_w = round(width * 0.64)
    product_h = round(height * 0.58)
    product_confidence = 0.72

    try:
        detection = await _detect_product_bounds_ai(image_url, width, height)
        # Clamp to image bounds
        px = max(0, min(int(detection.x), width - 1))
        py = max(0, min(int(detection.y), height - 1))
        pw = max(1, min(int(detection.width), width - px))
        ph = max(1, min(int(detection.height), height - py))
        product_x, product_y, product_w, product_h = px, py, pw, ph
        product_confidence = detection.confidence
        logger.info(
            "AI product detection succeeded",
            extra={"label": detection.label, "bounds": f"{px},{py},{pw},{ph}"},
        )
    except Exception as err:
        logger.warning(
            "AI product detection failed; using geometric fallback bounds",
            extra={"error": str(err)},
        )

    # ── Text layers from OCR words ─────────────────────────────────────────
    text_layers = []
    for index, word in enumerate((ocr.words if ocr else [])[:12]):
        if len(word.text.strip()) <= 1 or word.confidence <= 0.45:
            continue
        text_layers.append(
            {
                "id": f"text-{index + 1}",
                "type": "text",
                "label": f"Text {index + 1}",
                "bounds": word.bounds.model_dump(),
                "confidence": word.confidence,
                "text": word.text,
            }
        )

    return LayerExtraction.model_validate(
        {
            "image": {"width": width, "height": height},
            "layers": [
                {
                    "id": "background",
                    "type": "background",
                    "label": "Background plate",
                    "bounds": {"x": 0, "y": 0, "width": width, "height": height},
                    "confidence": 1,
                },
                {
                    "id": "product-primary",
                    "type": "product",
                    "label": "Primary product region",
                    "bounds": {
                        "x": product_x,
                        "y": product_y,
                        "width": product_w,
                        "height": product_h,
                    },
                    "confidence": product_confidence,
                },
                *text_layers,
            ],
        }
    )
