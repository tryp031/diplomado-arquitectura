"""API y página del panel de control del Reto 2 (`uvicorn --factory panel.app:build_app`).

Lee los logs en cada consulta de la página (cada ~1 s): no hay hilos de fondo y el panel no
escribe nada en el plano de datos. Las acciones entran al sistema por la MISMA puerta que
cualquier vehículo (el gateway), o apagan/encienden contenedores de una lista blanca.
"""
from __future__ import annotations

import os
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from panel.agregador import Agregador, LectorIncremental

ESTATICOS = Path(__file__).parent / "static"


class PedidoCarga(BaseModel):
    modo: str
    emergencias: int = 5


def create_app(*, agregador: Agregador, lector_servicio: LectorIncremental, lector_nginx: LectorIncremental,
               redis_info: Callable[[], Awaitable[dict]], docker: Any, k6: Any,
               gateway: httpx.AsyncClient, gateway_url: str) -> FastAPI:
    app = FastAPI(title="Reto 2 — panel de control")

    @app.get("/api/estado")
    async def estado() -> dict[str, Any]:
        # El orden importa: el ingest escribe antes que el notifier, así que se lee primero.
        agregador.ingerir_servicio(lector_servicio.leer())
        agregador.ingerir_nginx([registro for _, registro in lector_nginx.leer()])
        resultado = agregador.resumen(datetime.now(timezone.utc))
        resultado["redis"] = await redis_info()
        resultado["k6"] = k6.resumen()
        try:
            resultado["contenedores"], resultado["docker_error"] = await docker.contenedores(), None
        except Exception as exc:  # sin socket de Docker el panel sigue sirviendo los datos
            resultado["contenedores"], resultado["docker_error"] = {}, f"{type(exc).__name__}: {exc}"
        return resultado

    @app.post("/api/emergencia")
    async def emergencia() -> dict[str, Any]:
        placa = "PNL-" + "".join(random.choices(string.digits, k=3))
        try:
            respuesta = await gateway.post(gateway_url, json={
                "type": "Emergency", "vehicle_plate": placa, "status": "OK",
                "coordinates": {"latitude": 3.4516, "longitude": -76.532},
            }, timeout=5)
        except httpx.HTTPError as exc:
            return JSONResponse({"error": f"gateway no responde: {exc}"}, status_code=502)
        try:
            cuerpo = respuesta.json()
        except ValueError:  # nginx responde 429/502 con HTML
            cuerpo = respuesta.text[:200]
        return {"placa": placa, "status_gateway": respuesta.status_code, "respuesta": cuerpo}

    @app.post("/api/carga", status_code=202)
    async def carga(pedido: PedidoCarga):
        inicio = datetime.now(timezone.utc)
        try:
            await k6.iniciar(pedido.modo, emergencias=pedido.emergencias)  # valida, luego ocupa
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        except RuntimeError as exc:
            return JSONResponse({"error": str(exc)}, status_code=409)
        agregador.reiniciar(inicio)  # cada carga se observa en su propia ventana
        return {"modo": pedido.modo, "emergencias": pedido.emergencias}

    @app.post("/api/servicios/{servicio}/{accion}")
    async def servicio(servicio: str, accion: str):
        try:
            await docker.cambiar(servicio, accion)
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        except Exception as exc:
            return JSONResponse({"error": f"Docker: {exc}"}, status_code=502)
        return {"servicio": servicio, "accion": accion}

    @app.post("/api/ventana/reiniciar")
    async def reiniciar_ventana() -> dict[str, str]:
        desde = datetime.now(timezone.utc)
        agregador.reiniciar(desde)
        return {"desde": desde.isoformat()}

    app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="pagina")
    return app


def build_app() -> FastAPI:
    import redis.asyncio as redis

    from panel.infra import Docker, EjecutorK6, estado_redis

    logs = Path(os.environ.get("LOG_DIR", "logs"))
    stream = os.environ.get("STREAM", "emergencies")
    dlq_stream = os.environ.get("DLQ_STREAM", "emergencies-dlq")
    group = os.environ.get("CONSUMER_GROUP", "notifiers")
    client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
                            decode_responses=True, socket_timeout=2, socket_connect_timeout=2)
    gateway_url = os.environ.get("GATEWAY_URL", "http://gateway/events")
    return create_app(
        agregador=Agregador(),
        lector_servicio=LectorIncremental(logs, ("ingest-*.log", "notifier-*.log")),
        lector_nginx=LectorIncremental(logs / "nginx", ("gateway-access.log",)),
        redis_info=lambda: estado_redis(client, stream, dlq_stream, group),
        docker=Docker(os.environ.get("COMPOSE_PROJECT", "reto2-alerta-flota")),
        k6=EjecutorK6(os.environ.get("K6_SCRIPT", "/app/k6/carga.js"), gateway_url,
                      logs / "k6-summary.json"),
        gateway=httpx.AsyncClient(),
        gateway_url=gateway_url,
    )
