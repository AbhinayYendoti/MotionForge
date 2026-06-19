"""Structured production logging for MotionForge backend.

In production, every log line is valid JSON (one object per line) so that
log aggregators (Render, Datadog, etc.) can parse fields like level, message,
and extra context without a regex.

Usage:
    from app.core.logging import logger
    logger.info("Pipeline started", extra={"project_id": "abc", "user_id": "xyz"})
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object."""

    # Fields from LogRecord that are noise in structured output
    _SKIP = frozenset(
        {
            "args", "created", "exc_info", "exc_text", "filename", "funcName",
            "levelno", "lineno", "module", "msecs", "msg", "pathname",
            "process", "processName", "relativeCreated", "stack_info",
            "thread", "threadName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        # Merge any `extra` fields into the top-level payload.
        extra = {k: v for k, v in record.__dict__.items() if k not in self._SKIP and not k.startswith("_")}
        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            **extra,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _build_logger() -> logging.Logger:
    log = logging.getLogger("motionforge")
    if log.handlers:
        return log  # Already configured (e.g. during testing)

    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JSONFormatter())
    log.addHandler(handler)
    log.propagate = False
    return log


logger = _build_logger()
