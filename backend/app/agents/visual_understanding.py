from app.core.config import settings
from app.core.logging import logger
from app.schemas.pipeline import VisualAnalysis
from app.services.image_utils import to_vision_url
from app.services.nvidia_client import nvidia_chat_json


async def run_visual_understanding_agent(image_url: str, prompt: str | None) -> VisualAnalysis:
    try:
        return await nvidia_chat_json(
            model=settings.nvidia_vision_model,
            schema=VisualAnalysis,
            messages=[
                {
                    "role": "system",
                    "content": "You are MotionForge's Visual Understanding Agent. Analyze marketing creatives for a controllable motion graphics pipeline. Return only valid JSON.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this static creative. Optional user intent: {prompt or 'none'}. Return JSON with product, brand, colors, detectedText, style, composition {{ focalPoint, hierarchy, layout }}, and productCategory.",
                        },
                        {"type": "image_url", "image_url": {"url": to_vision_url(image_url)}},
                    ],
                },
            ],
        )
    except Exception as error:
        logger.warning("Visual analysis failed; using simplified fallback analysis", extra={"error": str(error)})
        # NOTE: Do NOT use `prompt` as the product — the raw user prompt is a
        # creative direction string (e.g. "Create a premium tech reel...") and
        # would be displayed verbatim as on-screen text in the video. We always
        # fall back to a generic product label here.
        return VisualAnalysis.model_validate(
            {
                "product": "Featured Product",
                "brand": None,
                "colors": ["#000000", "#ffffff"],
                "detectedText": [],
                "style": "Marketing creative",
                "composition": {
                    "focalPoint": "Center of uploaded creative",
                    "hierarchy": ["Primary visual", "Supporting text", "Call to action"],
                    "layout": "Static creative layout",
                },
                "productCategory": "Marketing",
            }
        )

