from app.core.config import settings
from app.core.logging import logger
from app.schemas.pipeline import LayerExtraction, MotionPlan, Storyboard
from app.services.nvidia_client import nvidia_chat_json


async def run_motion_director_agent(storyboard: Storyboard, layers: LayerExtraction) -> MotionPlan:
    try:
        return await nvidia_chat_json(
            model=settings.nvidia_text_model,
            schema=MotionPlan,
            messages=[
                {"role": "system", "content": "You are MotionForge's Motion Director Agent. Plan Remotion-friendly layer animations. Return only valid JSON."},
                {
                    "role": "user",
                    "content": f"Storyboard: {storyboard.model_dump_json()}. Layers: {layers.model_dump_json()}. Create motion JSON with fps 30 and animations keyed to sceneId and existing layerId values.",
                },
            ],
        )
    except Exception as error:
        logger.warning("Motion planning failed; using deterministic fallback motion plan", extra={"error": str(error)})
        animations = []
        for scene_index, scene in enumerate(storyboard.scenes):
            start = scene_index * 90
            for layer_index, layer in enumerate(layers.layers[:4]):
                translate_y_start = 24 if layer_index % 2 == 0 else -18
                animations.append(
                    {
                        "sceneId": scene.id,
                        "layerId": layer.id,
                        "fromFrame": start,
                        "toFrame": start + max(30, round(scene.durationSeconds * 30)),
                        "transform": {
                            "translateY": [translate_y_start, 0],
                            "scale": [0.98, 1.04],
                            "opacity": [0, 1],
                        },
                        "easing": "easeOut",
                    }
                )
        return MotionPlan.model_validate({"format": "reel", "fps": 30, "animations": animations})

