"""API y página del panel de control del Reto 2 (`uvicorn --factory panel.app:build_app`).

Lee los logs en cada consulta de la página (cada ~1 s): no hay hilos de fondo y el panel no
escribe nada en el plano de datos. Las acciones entran al sistema por la MISMA puerta que
cualquier vehículo (el gateway), o apagan/encienden contenedores de una lista blanca.

Observa uno de dos entornos a la vez, local (Docker) o AWS (opción B), y se cambia con el switch
de la página (`POST /api/entorno`). Ver panel/entornos.py.
"""
from __future__ import annotations

import asyncio
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
from panel.entornos import EntornoAws, EntornoLocal
from panel.exportar import COLOMBIA, como_csv, como_log
from panel.infra import MODO_PROFESOR

ESTATICOS = Path(__file__).parent / "static"


class PedidoCarga(BaseModel):
    modo: str
    emergencias: int | None = 1  # se ignora en modo «profesor»: ese script decide


class PedidoEntorno(BaseModel):
    entorno: Literal["local", "aws"]


def create_app(*, agregador: Agregador, lector_servicio: LectorIncremental, lector_nginx: LectorIncremental,
               redis_info: Callable[[], Awaitable[dict]], docker: Any, k6: Any,
               gateway: httpx.AsyncClient, gateway_url: str, smtp_host: str = "mailpit",
               log_dir: Path = Path("logs"), historial: Historial | None = None,
               redis_vaciar: Callable[[], Awaitable[None]] | None = None,
               aws: EntornoAws | None = None, aws_motivo: str | None = None) -> FastAPI:
    """`aws` es opcional: sin él, el switch aparece deshabilitado con `aws_motivo` como explicación."""
    app = FastAPI(title="Reto 2 — panel de control")
    historial = historial or Historial(log_dir / "panel-corridas.json")
    local = EntornoLocal(lector_servicio=lector_servicio, lector_nginx=lector_nginx, redis_info=redis_info,
                         redis_vaciar=redis_vaciar, docker=docker, k6=k6, gateway_url=gateway_url,
                         smtp_host=smtp_host, log_dir=log_dir)
    entornos: dict[str, EntornoLocal | EntornoAws] = {"local": local, **({"aws": aws} if aws else {})}
    # Corrida que el agregador está observando y entorno activo. Tras reiniciar el panel no hay
    # corrida (las del historial quedan como se guardaron) y se vuelve al entorno local.
    actual: dict[str, Any] = {"n": None, "entorno": "local"}

    def activo() -> EntornoLocal | EntornoAws:
        return entornos[actual["entorno"]]

    def alguna_carga_corriendo() -> bool:
        return any(e.k6.resumen()["estado"] == "corriendo" for e in entornos.values())

    def cerrar_si_termino() -> None:
        ventana = activo().k6.ventana()
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
        entorno = activo()
        cerrar_si_termino()  # antes de leer: lo que entre después del cierre ya no es de la corrida
        # En un hilo: en AWS es una llamada de red (boto3 es síncrono) y no debe frenar el servidor.
        servicio, peticiones = await asyncio.to_thread(entorno.leer)
        agregador.ingerir_servicio(servicio)
        agregador.ingerir_nginx(peticiones)
        resultado = agregador.resumen(datetime.now(timezone.utc))
        guardar_resumen(resultado)
        resultado["corrida"] = historial.buscar(actual["n"]) if actual["n"] else None
        resultado["historial"] = historial.listar()
        resultado["redis"] = await entorno.cola()  # Redis o SQS, mismo formato
        resultado["k6"] = entorno.k6.resumen()
        resultado["smtp"] = entorno.smtp
        resultado["contenedores"], resultado["docker_error"] = await entorno.contenedores()
        resultado["entorno"] = {
            "activo": entorno.nombre, "gestionado": entorno.gestionado, "error": entorno.error,
            "aws_disponible": "aws" in entornos, "aws_motivo": None if "aws" in entornos else aws_motivo,
        }
        return resultado

    @app.post("/api/entorno")
    async def cambiar_entorno(pedido: PedidoEntorno):
        if pedido.entorno not in entornos:
            return JSONResponse({"error": aws_motivo or "AWS no está configurado"}, status_code=400)
        if pedido.entorno == actual["entorno"]:
            return {"entorno": pedido.entorno}
        if alguna_carga_corriendo():
            return JSONResponse({"error": "hay una carga en curso: espere a que termine"}, status_code=409)
        actual["entorno"], actual["n"] = pedido.entorno, None
        entornos[pedido.entorno].reiniciar_lectura()
        agregador.reiniciar(None)  # lo observado en el otro entorno no se mezcla con este
        return {"entorno": pedido.entorno}

    @app.get("/api/k6/salida")
    def salida_k6() -> dict[str, Any]:
        return {"lineas": activo().k6.salida_completa()}

    @app.post("/api/emergencia")
    async def emergencia() -> dict[str, Any]:
        placa = "PNL-" + "".join(random.choices(string.digits, k=3))
        try:
            respuesta = await gateway.post(activo().gateway_url, json={
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
        entorno = activo()
        inicio = datetime.now(timezone.utc)
        try:
            await entorno.k6.iniciar(pedido.modo, emergencias=pedido.emergencias)  # valida, luego ocupa
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        except RuntimeError as exc:
            return JSONResponse({"error": str(exc)}, status_code=409)
        agregador.reiniciar(inicio)  # cada carga se observa en su propia ventana
        actual["n"] = historial.abrir(inicio, pedido.modo, entorno.smtp["host"], entorno.nombre)["n"]
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
        # Los logs salen del entorno DONDE CORRIÓ, no del que se está mirando ahora.
        nombre = corrida.get("entorno", "local")
        if nombre not in entornos:
            return JSONResponse({"error": f"la corrida {n} es de {nombre}, que no está configurado"}, status_code=409)
        inicio, fin = datetime.fromisoformat(corrida["inicio"]), datetime.fromisoformat(corrida["fin"])
        try:
            registros = entornos[nombre].registros_de_carga(inicio, fin)
        except Exception as exc:  # CloudWatch sin credenciales o sin red
            return JSONResponse({"error": f"no se pudieron leer los logs: {exc}"}, status_code=502)
        sufijo = "-aws" if nombre == "aws" else ""
        return _descarga(registros, inicio, formato, f"corrida-{n}-{corrida['modo']}{sufijo}")

    @app.post("/api/datos/limpiar")
    async def limpiar() -> Any:
        """Borra lo ejecutado en el entorno activo (historial, logs, colas) para correr con data limpia.

        En AWS solo se borra lo del panel: el usuario IAM es de solo lectura y no toca CloudWatch ni SQS.
        """
        entorno = activo()
        if entorno.k6.resumen()["estado"] == "corriendo":
            return JSONResponse({"error": "hay una carga en curso: espere a que termine"}, status_code=409)
        try:
            resultado = await entorno.vaciar()
        except Exception as exc:  # sin Redis no se borra nada: mejor un error que un borrado a medias
            return JSONResponse({"error": f"Redis no respondió: {exc}"}, status_code=502)
        historial.vaciar(entorno.nombre)
        entorno.k6.olvidar()
        agregador.reiniciar(None)
        actual["n"] = None
        return resultado

    @app.post("/api/servicios/{servicio}/{accion}")
    async def servicio(servicio: str, accion: str):
        if activo().gestionado:
            return JSONResponse({"error": "en AWS el panel solo observa: no apaga servicios"}, status_code=400)
        try:
            await docker.cambiar(servicio, accion)
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
        except Exception as exc:
            return JSONResponse({"error": f"Docker: {exc}"}, status_code=502)
        return {"servicio": servicio, "accion": accion}

    @app.middleware("http")
    async def sin_cache(request, call_next):
        # El navegador revalida la página y su JS en cada carga: tras reconstruir el panel nadie
        # se queda viendo una versión vieja (pasó el 12/10 con la ayuda del modo AWS).
        respuesta = await call_next(request)
        respuesta.headers["Cache-Control"] = "no-cache"
        return respuesta

    app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="pagina")
    return app


def _descarga(registros: list[dict], inicio: datetime, formato: str, prefijo: str) -> Response:
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
    aws, motivo = _entorno_aws(logs)
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
        aws=aws, aws_motivo=motivo,
    )


def _entorno_aws(logs: Path) -> tuple[EntornoAws | None, str | None]:
    """El entorno AWS si hay configuración (`.env.aws`); si no, None y el motivo para la página."""
    from panel.infra import EjecutorK6

    url = os.environ.get("AWS_API_URL")
    if not url:
        return None, "Falta AWS_API_URL: copie .env.aws.example a .env.aws y reconstruya el panel"
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        return None, "Falta boto3 en la imagen del panel: reconstruya con --build"
    region = os.environ.get("AWS_REGION", "us-east-2")
    # Timeouts cortos y sin reintentos ocultos: un AWS lento no debe congelar el panel.
    config = Config(region_name=region, connect_timeout=3, read_timeout=5, retries={"max_attempts": 2})
    grupos = {"ingest": os.environ.get("AWS_LOG_GROUP_INGESTA", "/aws/lambda/reto2-ingesta"),
              "notifier": os.environ.get("AWS_LOG_GROUP_NOTIFIER", "/aws/lambda/reto2-notifier")}
    k6 = EjecutorK6(os.environ.get("K6_SCRIPT", "/app/k6/carga.js"), url, logs / "k6-summary-aws.json",
                    script_profesor=os.environ.get("K6_SCRIPT_PROFESOR", "/app/k6/profesor.js"))
    return EntornoAws(logs=boto3.client("logs", config=config), sqs=boto3.client("sqs", config=config),
                      grupos=grupos, cola_url=os.environ.get("AWS_SQS_URL"),
                      dlq_url=os.environ.get("AWS_SQS_DLQ_URL"), k6=k6, gateway_url=url), None
