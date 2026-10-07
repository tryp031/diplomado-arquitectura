"""Lo que el panel consulta o acciona fuera de sí mismo: Redis, Docker y k6.

Docker se controla por su socket. Eso equivale a acceso root sobre Docker en la máquina:
aceptable para una demo local (puerto solo en 127.0.0.1), nunca en un ambiente compartido.
Por eso las acciones están limitadas a una lista blanca.
"""
from __future__ import annotations

import asyncio
import json
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

import httpx

SERVICIOS_CONTROLABLES = {"mailpit", "redis", "notifier"}
ACCIONES_DOCKER = {"apagar": "stop", "encender": "start"}
MODOS_K6 = {"rafaga": None, "ritmo": "0.28"}  # SLEEP_S: el ritmo imita la salida de referencia
# El k6 del profesor decide solo cuántos Emergency manda y a qué ritmo: no recibe parámetros.
MODO_PROFESOR = "profesor"
MAX_EMERGENCIAS = 100
_COLOR_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


async def estado_redis(client: Any, stream: str, dlq_stream: str, group: str) -> dict[str, Any]:
    try:
        await client.ping()
        pendientes = 0
        try:
            pendientes = (await client.xpending(stream, group))["pending"]
        except Exception:  # el grupo aún no existe (Redis recién reiniciado)
            pass
        return {"ok": True, "stream": await client.xlen(stream), "pendientes": pendientes,
                "dlq": await client.xlen(dlq_stream)}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


class Docker:
    def __init__(self, proyecto: str, *, socket: str = "/var/run/docker.sock",
                 transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._proyecto = proyecto
        self._client = httpx.AsyncClient(
            transport=transport or httpx.AsyncHTTPTransport(uds=socket),
            base_url="http://docker", timeout=20,
        )

    async def contenedores(self) -> dict[str, dict[str, str]]:
        filtros = json.dumps({"label": [f"com.docker.compose.project={self._proyecto}"]})
        respuesta = await self._client.get("/containers/json", params={"all": "true", "filters": filtros})
        respuesta.raise_for_status()
        resultado = {}
        for contenedor in respuesta.json():
            etiquetas = contenedor["Labels"]
            servicio = etiquetas.get("com.docker.compose.service", "?")
            numero = etiquetas.get("com.docker.compose.container-number", "1")
            resultado[f"{servicio}-{numero}"] = {
                "servicio": servicio, "estado": contenedor["State"], "detalle": contenedor["Status"],
            }
        return resultado

    async def cambiar(self, servicio: str, accion: str) -> None:
        if servicio not in SERVICIOS_CONTROLABLES or accion not in ACCIONES_DOCKER:
            raise ValueError(f"acción no permitida: {accion} {servicio}")
        nombre = f"{self._proyecto}-{servicio}-1"
        respuesta = await self._client.post(f"/containers/{nombre}/{ACCIONES_DOCKER[accion]}",
                                            params={"t": "5"} if accion == "apagar" else None)
        if respuesta.status_code not in (204, 304):  # 304: ya estaba en ese estado
            respuesta.raise_for_status()


Lanzador = Callable[..., Awaitable[Any]]


class EjecutorK6:
    """Corre una carga k6 a la vez y guarda las últimas líneas de su salida."""

    def __init__(self, script: str, url: str, resumen_path: Path, *, script_profesor: str | None = None,
                 binario: str = "k6", lanzar: Lanzador | None = asyncio.create_subprocess_exec) -> None:
        self._script = script
        self._script_profesor = script_profesor
        self._url = url
        self._resumen_path = Path(resumen_path)
        self._binario = binario
        self._lanzar = lanzar
        self._tarea: asyncio.Task[None] | None = None
        self.estado = "inactivo"
        self.modo: str | None = None
        self.inicio: datetime | None = None
        self.fin: datetime | None = None
        self.codigo: int | None = None
        self.salida: deque[str] = deque(maxlen=30)

    @property
    def ocupado(self) -> bool:
        return self.estado == "corriendo"

    async def iniciar(self, modo: str, *, emergencias: int | None = None) -> None:
        argumentos = [self._binario, "run", "--no-color",
                      "-e", f"TARGET_URL={self._url}",
                      "-e", f"SUMMARY_PATH={self._resumen_path}"]
        if modo == MODO_PROFESOR:
            if not self._script_profesor:
                raise ValueError("el k6 del profesor no está configurado")
            argumentos.append(self._script_profesor)
        elif modo in MODOS_K6:
            if emergencias is None or not 0 <= emergencias <= MAX_EMERGENCIAS:
                raise ValueError(f"emergencias debe estar entre 0 y {MAX_EMERGENCIAS}")
            argumentos += ["-e", f"EMERGENCIES={emergencias}"]
            if MODOS_K6[modo]:
                argumentos += ["-e", f"SLEEP_S={MODOS_K6[modo]}"]
            argumentos.append(self._script)
        else:
            raise ValueError(f"modo desconocido: {modo}")
        if self.ocupado:
            raise RuntimeError("ya hay una carga en curso")
        self.estado, self.modo, self.codigo = "corriendo", modo, None
        self.inicio, self.fin = datetime.now(timezone.utc), None
        self.salida.clear()
        try:
            proceso = await self._lanzar(*argumentos, stdout=asyncio.subprocess.PIPE,
                                         stderr=asyncio.subprocess.STDOUT)
        except Exception:
            self.estado, self.fin = "fallido", datetime.now(timezone.utc)
            raise
        self._tarea = asyncio.create_task(self._seguir(proceso))

    async def _seguir(self, proceso: Any) -> None:
        async for linea in proceso.stdout:
            texto = _COLOR_ANSI.sub("", linea.decode(errors="replace")).strip()
            if texto:
                self.salida.append(texto)
        self.codigo = await proceso.wait()
        self.fin = datetime.now(timezone.utc)
        self.estado = "terminado" if self.codigo == 0 else "fallido"

    def ventana(self) -> tuple[datetime, datetime] | None:
        """(inicio, fin) de la última carga, solo si ya terminó (bien o mal)."""
        if self.ocupado or self.inicio is None or self.fin is None:
            return None
        return self.inicio, self.fin

    async def esperar(self) -> None:
        if self._tarea:
            await self._tarea

    def resumen(self) -> dict[str, Any]:
        ultimo = None
        if self._resumen_path.exists():
            try:
                ultimo = json.loads(self._resumen_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                ultimo = None
        return {
            "estado": self.estado,
            "modo": self.modo,
            "inicio": self.inicio.isoformat() if self.inicio else None,
            "fin": self.fin.isoformat() if self.fin else None,
            "codigo": self.codigo,
            "salida": list(self.salida)[-12:],
            "ultimo_resumen": ultimo,
        }
