"""Arranque de la ingesta: `uvicorn --factory alerta.main_ingest:build_app`."""
from __future__ import annotations

from fastapi import FastAPI

from alerta.adapters.redis_queue import RedisAlertQueue, conectar
from alerta.config import load_settings
from alerta.ingest_app import create_app
from alerta.logjson import JsonLogger


def build_app() -> FastAPI:
    settings = load_settings()
    client = conectar(settings.redis_url)
    queue = RedisAlertQueue(client, stream=settings.stream, group=settings.group,
                            consumer=settings.consumer, dlq_stream=settings.dlq_stream)
    return create_app(queue, JsonLogger("ingest", settings.log_dir))
