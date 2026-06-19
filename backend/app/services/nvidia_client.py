import json
import re
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


def extract_json(content: str) -> dict[str, Any]:
    fenced = re.search(r"\x60\x60\x60(?:json)?\s*([\s\S]*?)\x60\x60\x60", content, re.IGNORECASE)
    raw = fenced.group(1) if fenced else content
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("NVIDIA response did not contain JSON.")
    return json.loads(raw[start : end + 1])


async def nvidia_chat_json(
    *,
    model: str,
    messages: list[dict[str, Any]],
    schema: type[T],
    temperature: float = 0.2,
    max_tokens: int = 1800,
) -> T:
    last_error: Exception | None = None
    url = f"{settings.nvidia_base_url.rstrip('/')}/chat/completions"
    attempts = max(1, settings.nvidia_max_attempts)
    async with httpx.AsyncClient(timeout=settings.nvidia_request_timeout) as client:
        for attempt in range(1, attempts + 1):
            try:
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {settings.nvidia_api_key}", "Content-Type": "application/json"},
                    json={"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
                )
                response.raise_for_status()
                content = response.json().get("choices", [{}])[0].get("message", {}).get("content")
                if not content:
                    raise ValueError("NVIDIA API returned an empty completion.")
                return schema.model_validate(extract_json(content))
            except (httpx.HTTPError, ValueError, ValidationError, json.JSONDecodeError) as error:
                last_error = error
                logger.warning("NVIDIA JSON completion attempt failed", extra={"model": model, "attempt": attempt, "error": str(error)})
    raise last_error or RuntimeError("NVIDIA JSON completion failed.")
