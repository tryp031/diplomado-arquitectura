"""Los dos sistemas que el panel puede observar: el local (Docker) y la opción B en AWS.

El panel (agregador, historial, medida de la rúbrica, página) es el mismo para ambos. Lo único
que cambia es DE DÓNDE lee y CONTRA QUÉ dispara, y eso vive aquí detrás de una interfaz común:

    leer()                 → (registros de servicio, peticiones en formato nginx)
    cola()                 → estado de la cola (Redis o SQS) con el mismo formato
    contenedores()         → estado de Docker; en AWS no aplica
    registros_de_carga()   → logs de una ventana, para descargar la evidencia de una corrida
    vaciar()               → «Borrar datos» de ese entorno
    k6, gateway_url        → contra qué URL se lanzan la carga y el Emergency manual

Cambiar de entorno no reinicia nada del plano de datos: solo cambia lo que se mira.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable

from panel.agregador import LectorIncremental
from panel.aws import LectorCloudWatch, estado_sqs, leer_ventana, peticiones_desde_ingesta
from panel.exportar import GRACIA, registros_de_carga
from panel.limpieza import vaciar_logs

Lectura = tuple[list[tuple[str, dict]], list[dict]]


class EntornoLocal:
    nombre = "local"
    gestionado = False  # Docker: se puede apagar/encender

    def __init__(self, *, lector_servicio: LectorIncremental, lector_nginx: LectorIncremental,
                 redis_info: Callable[[], Awaitable[dict]], redis_vaciar: Callable[[], Awaitable[None]] | None,
                 docker: Any, k6: Any, gateway_url: str, smtp_host: str, log_dir: Path) -> None:
        self._lector_servicio, self._lector_nginx = lector_servicio, lector_nginx
        self._redis_info, self._redis_vaciar = redis_info, redis_vaciar
        self.docker, self.k6, self.gateway_url = docker, k6, gateway_url
        self.smtp_host, self.log_dir = smtp_host, log_dir

    @property
    def smtp(self) -> dict[str, Any]:
        # Solo Mailpit corre dentro de Docker; Gmail es externo y el panel no puede apagarlo.
        return {"host": self.smtp_host, "local": self.smtp_host == "mailpit"}

    @property
    def error(self) -> str | None:
        return None

    def leer(self) -> Lectura:
        # El orden importa: el ingest escribe antes que el notifier, así que se lee primero.
        return self._lector_servicio.leer(), [r for _, r in self._lector_nginx.leer()]

    def reiniciar_lectura(self) -> None:
        self._lector_servicio.reiniciar()
        self._lector_nginx.reiniciar()

    async def cola(self) -> dict[str, Any]:
        return await self._redis_info()

    async def contenedores(self) -> tuple[dict, str | None]:
        try:
            return await self.docker.contenedores(), None
        except Exception as exc:  # sin socket de Docker el panel sigue sirviendo los datos
            return {}, f"{type(exc).__name__}: {exc}"

    def registros_de_carga(self, inicio: datetime, fin: datetime) -> list[dict]:
        return registros_de_carga(self.log_dir, inicio, fin)

    async def vaciar(self) -> dict[str, Any]:
        if self._redis_vaciar:  # sin Redis no se borra nada: mejor un error que un borrado a medias
            await self._redis_vaciar()
        return {"logs_vaciados": vaciar_logs(self.log_dir)}


class EntornoAws:
    nombre = "aws"
    gestionado = True  # servicios administrados: el panel no los apaga

    def __init__(self, *, logs: Any, sqs: Any, grupos: dict[str, str], cola_url: str | None,
                 dlq_url: str | None, k6: Any, gateway_url: str, lector: LectorCloudWatch | None = None) -> None:
        self._logs, self._sqs, self._grupos = logs, sqs, grupos
        self._cola_url, self._dlq_url = cola_url, dlq_url
        self._lector = lector or LectorCloudWatch(logs, grupos)
        self.k6, self.gateway_url = k6, gateway_url
        self.smtp = {"host": "Amazon SES", "local": False}
        self.docker = None

    @property
    def error(self) -> str | None:
        return self._lector.error

    def leer(self) -> Lectura:
        registros = self._lector.leer()
        return registros, peticiones_desde_ingesta(registros)

    def reiniciar_lectura(self) -> None:
        self._lector.reiniciar()

    async def cola(self) -> dict[str, Any]:
        return await asyncio.to_thread(estado_sqs, self._sqs, self._cola_url, self._dlq_url)

    async def contenedores(self) -> tuple[dict, str | None]:
        return {}, None

    def registros_de_carga(self, inicio: datetime, fin: datetime) -> list[dict]:
        pares = leer_ventana(self._logs, self._grupos, inicio, fin + GRACIA)
        return [{**registro, "replica": replica} for replica, registro in pares]

    async def vaciar(self) -> dict[str, Any]:
        # El usuario IAM del panel es de solo lectura: CloudWatch y SQS se conservan. Se borra lo
        # del panel (historial y estado de k6 de este entorno), que lo hace quien llama.
        return {"logs_vaciados": 0}
