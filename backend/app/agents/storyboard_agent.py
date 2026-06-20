from app.core.config import settings
from app.core.logging import logger
from app.schemas.pipeline import LayerExtraction, Storyboard, VisualAnalysis
from app.services.nvidia_client import nvidia_chat_json


async def run_storyboard_agent(
    prompt: str | None,
    analysis: VisualAnalysis,
    layers: LayerExtraction,
    negative_guidance: list[str] | None = None,
) -> Storyboard:
    avoidance = ""
    if negative_guidance:
        avoidance = f" IMPORTANT — avoid these issues from a previous failed attempt: {'; '.join(negative_guidance)}."
    try:
        return await nvidia_chat_json(
            model=settings.nvidia_text_model,
            schema=Storyboard,
            messages=[
                {"role": "system", "content": (
                    "You are MotionForge's Storyboard Agent. Create concise professional marketing-video storyboards. "
                    "CRITICAL RULE: The 'onScreenText' field for every scene must be SHORT (1-6 words max) punchy marketing copy "
                    "that would look great displayed as a text overlay on a video — like a tagline or headline. "
                    "NEVER copy the user's instruction prompt into onScreenText. Extract the product/brand from the visual analysis and write original copy. "
                    "Return only valid JSON."
                )},
                {
                    "role": "user",
                    "content": (
                        f"Creative direction (DO NOT use this as onScreenText): {prompt or 'Create a premium product motion campaign'}."
                        f"{avoidance}"
                        f" Visual analysis: {analysis.model_dump_json()}."
                        f" Extracted layers: {layers.model_dump_json()}."
                        " Create a 6-12 second storyboard with 2-4 scenes."
                        " Each scene's onScreenText must be 1-6 words of original marketing copy."
                    ),
                },
            ],
        )
    except Exception as error:
        logger.warning("Storyboard generation failed; using deterministic fallback storyboard", extra={"error": str(error)})
        # NOTE: Never use `prompt` or `analysis.product` verbatim for
        # onScreenText — those can be multi-sentence instruction strings that
        # look terrible as video overlay text. Use short, punchy marketing copy.
        product_label = analysis.brand or "Featured Product"
        return Storyboard.model_validate(
            {
                "title": product_label,
                "totalDurationSeconds": 9,
                "scenes": [
                    {
                        "id": "scene-1",
                        "name": "Product Reveal",
                        "objective": "Introduce the uploaded creative with a premium reveal.",
                        "durationSeconds": 3,
                        "narration": f"{product_label} enters with a focused reveal.",
                        "onScreenText": product_label,
                    },
                    {
                        "id": "scene-2",
                        "name": "Feature Highlight",
                        "objective": "Emphasize the product and key visual hierarchy.",
                        "durationSeconds": 3,
                        "narration": "Motion guides attention through the primary product and message.",
                        "onScreenText": "Innovation Meets Design.",
                    },
                    {
                        "id": "scene-3",
                        "name": "Call To Action",
                        "objective": "Close with a clear campaign endpoint.",
                        "durationSeconds": 3,
                        "narration": "The campaign closes with a polished call to action.",
                        "onScreenText": "Discover more",
                    },
                ],
            }
        )

