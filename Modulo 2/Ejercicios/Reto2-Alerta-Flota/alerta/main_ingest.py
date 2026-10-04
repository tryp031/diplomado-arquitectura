"""Arranque de la ingesta: `uvicorn --factory alerta.main_ingest:build_app`."""
from __future__ import annotations

import redis.asyncio as redis
from fastapi import FastAPI

from alerta.adapters.redis_queue import RedisAlertQueue
from alerta.config import load_settings
from alerta.ingest_app import create_app
from alerta.logjson import JsonLogger


def build_app() -> FastAPI:
    settings = load_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    queue = RedisAlertQueue(client, stream=settings.stream, group=settings.group,
                            consumer=settings.consumer, dlq_stream=settings.dlq_stream)
    return create_app(queue, JsonLogger("ingest", settings.log_dir))
