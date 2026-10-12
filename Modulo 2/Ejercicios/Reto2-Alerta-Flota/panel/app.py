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
from typing import Any, Awaitable, Callable, Literal

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from panel.agregador import Agregador, LectorIncremental
from panel.corridas import Historial
from panel.exportar import COLOMBIA, como_csv, como_log, registros_de_carga
from panel.limpieza import vaciar_logs
from panel.infra import MODO_PROFESOR

ESTATICOS = Path(__file__).parent / "static"


class PedidoCarga(BaseModel):
    modo: str
    emergencias: int | None = 1  # se ignora en modo «profesor»: ese script decide


def create_app(*, agregador: Agregador, lector_servicio: LectorIncremental, lector_nginx: LectorIncremental,
               redis_info: Callable[[], Awaitable[dict]], docker: Any, k6: Any,
               gateway: httpx.AsyncClient, gateway_url: str, smtp_host: str = "mailpit",
               log_dir: Path = Path("logs"), historial: Historial | None = None,
               redis_vaciar: Callable[[], Awaitable[None]] | None = None) -> FastAPI:
    app = FastAPI(title="Reto 2 — panel de control")
    historial = historial or Historial(log_dir / "panel-corridas.json")
    # Corrida que el agregador está observando. Tras reiniciar el panel no hay ninguna: las del
    # historial quedan como se guardaron.
    actual: dict[str, Any] = {"n": None}

    def cerrar_si_termino() -> None:
        ventana = k6.ventana()
        if actual["n"] is None or ventana is None or agregador.hasta is not None:
            return
        agregador.cerrar(ventana[1])
        historial.actualizar(actual["n"], fin=ventana[1].isoformat())

    def guardar_resumen(resumen: dict[str, Any]) -> None:
        # Solo con la corrida cerrada: mientras k6 envía, la medida todavía no es válida.
        if actual["n"] is None or agregador.hasta is None:
            return
        historial.actualizar(
            actual["n"], medida=resumen["medida_rubrica"], total=resumen["http"]["total"],
            aceptadas=resumen["http"]["aceptadas"], rechazadas_429=resumen["http"]["rechazadas_429"],
            emergencias=resumen["eventos"]["emergencias"], enviadas=resumen["eventos"]["enviadas"],
            dlq=resumen["eventos"]["dlq"], procesados=resumen["eventos"]["procesados"],
            emergencia_a_correo=resumen["emergencia_a_correo"]["segundos"],
        )

    @app.get("/api/estado")
    async def estado() -> dict[str, Any]:
        cerrar_si_termino()  # antes de leer: lo que entre después del cierre ya no es de la corrida
        # El orden importa: el ingest escribe antes que el notifier, así que se lee primero.
        agregador.ingerir_servicio(lector_servicio.leer())
        agregador.ingerir_nginx([registro for _, registro in lector_nginx.leer()])
        resultado = agregador.resumen(datetime.now(timezone.utc))
        guardar_resumen(resultado)
        resultado["corrida"] = historial.buscar(actual["n"]) if actual["n"] else None
        resultado["historial"] = historial.listar()
        resultado["redis"] = await redis_info()
        resultado["k6"] = k6.resumen()
        # Solo Mailpit corre dentro de Docker; Gmail es externo y el panel no puede apagarlo.
        resultado["smtp"] = {"host": smtp_host, "local": smtp_host == "mailpit"}
        try:
            resultado["contenedores"], resultado["docker_error"] = await docker.contenedores(), None
        except Exception as exc:  # sin socket de Docker el panel sigue sirviendo los datos
            resultado["contenedores"], resultado["docker_error"] = {}, f"{type(exc).__name__}: {exc}"
        return resultado

    @app.get("/api/k6/salida")
    def salida_k6() -> dict[str, Any]:
        return {"lineas": k6.salida_completa()}

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
        actual["n"] = historial.abrir(inicio, pedido.modo, smtp_host)["n"]
        emergencias = None if pedido.modo == MODO_PROFESOR else pedido.emergencias
        return {"modo": pedido.modo, "emergencias": emergencias, "corrida": actual["n"]}

    @app.get("/api/corridas/{n}/logs")
    def logs_de_una_corrida(n: int, formato: Literal["log", "csv"] = "log"):
        # Síncrona a propósito: FastAPI la corre en un hilo y leer los logs no frena /api/estado.
        corrida = historial.buscar(n)
        if corrida is None:
            return JSONResponse({"error": f"no existe la corrida {n}"}, status_code=404)
        if corrida["fin"] is None:
            return JSONResponse({"error": "la corrida no ha terminado"}, status_code=409)
        inicio, fin = datetime.fromisoformat(corrida["inicio"]), datetime.fromisoformat(corrida["fin"])
        return _descarga(log_dir, inicio, fin, formato, f"corrida-{n}-{corrida['modo']}")

    @app.post("/api/datos/limpiar")
    async def limpiar() -> Any:
        """Borra lo ejecutado hasta ahora (historial, logs, colas) para correr con data limpia."""
        if k6.resumen()["estado"] == "corriendo":
            return JSONResponse({"error": "hay una carga en curso: espere a que termine"}, status_code=409)
        try:
            if redis_vaciar:
                await redis_vaciar()
        except Exception as exc:  # sin Redis no se borra nada: mejor un error que un borrado a medias
            return JSONResponse({"error": f"Redis no respondió: {exc}"}, status_code=502)
        logs = vaciar_logs(log_dir)
        historial.vaciar()
        k6.olvidar()
        agregador.reiniciar(None)
        actual["n"] = None
        return {"logs_vaciados": logs}

    @app.post("/api/servicios/{servicio}/{accion}")
    async def servicio(servicio: str, accion: str):
        try:
            await docker.cambiar(servicio, accion)
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        except Exception as exc:
            return JSONResponse({"error": f"Docker: {exc}"}, status_code=502)
        return {"servicio": servicio, "accion": accion}

    app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="pagina")
    return app


def _descarga(log_dir: Path, inicio: datetime, fin: datetime, formato: str, prefijo: str) -> Response:
    registros = registros_de_carga(log_dir, inicio, fin)
    cuerpo, tipo = (como_csv(registros), "text/csv") if formato == "csv" else (como_log(registros), "text/plain")
    nombre = f"{prefijo}-{inicio.astimezone(COLOMBIA):%Y%m%d-%H%M%S}.{formato}"
    return Response(cuerpo, media_type=f"{tipo}; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{nombre}"'})


def build_app() -> FastAPI:
    import redis.asyncio as redis

    from panel.infra import Docker, EjecutorK6, estado_redis
    from panel.limpieza import vaciar_redis

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
        redis_vaciar=lambda: vaciar_redis(client, stream, dlq_stream),
        docker=Docker(os.environ.get("COMPOSE_PROJECT", "reto2-alerta-flota")),
        k6=EjecutorK6(os.environ.get("K6_SCRIPT", "/app/k6/carga.js"), gateway_url,
                      logs / "k6-summary.json",
                      script_profesor=os.environ.get("K6_SCRIPT_PROFESOR", "/app/k6/profesor.js")),
        gateway=httpx.AsyncClient(),
        gateway_url=gateway_url,
        smtp_host=os.environ.get("SMTP_HOST", "mailpit"),
        log_dir=logs,
    )
