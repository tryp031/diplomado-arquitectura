"""Lo que el panel lee de AWS (opción B de Camilo): CloudWatch Logs y el estado de SQS.

Solo LECTURA: el usuario IAM del panel necesita `logs:FilterLogEvents` sobre los dos grupos de
logs y `sqs:GetQueueAttributes` sobre las dos colas (ver docs/2026-10-12-panel-switch-aws.md).
No hay equivalente a apagar contenedores: en AWS el panel observa, no inyecta fallas.

Las Lambdas de Camilo escriben las MISMAS líneas JSON que el sistema local (EVENT_RECEIVED,
EMERGENCY_RECEIVED, EMAIL_SENT…), así que el Agregador las procesa sin cambios. Lo que cambia
es cómo llegan:

- CloudWatch las publica con unos segundos de retraso y cada grupo de logs va a su ritmo. Si un
  EMAIL_SENT llegara antes que su EMERGENCY_RECEIVED, el Agregador lo descartaría. Por eso el
  lector RETIENE lo más reciente (`retencion_s`) y entrega todo ordenado por hora.
- FilterLogEvents tiene una cuota baja de llamadas por segundo: el lector consulta como mucho
  cada `intervalo_s` y, entre una consulta y otra, devuelve una lista vacía.
- No hay log del gateway: API Gateway no escribe nada en los logs de las Lambdas. Las peticiones
  se derivan de lo que registró la ingesta (`peticiones_desde_ingesta`), así que un 429 de API
  Gateway NO se ve aquí.
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any, Callable

# Cuántas páginas de FilterLogEvents se piden como máximo en una consulta. Una corrida de 1000
# eventos deja ~4000 líneas (con START/END/REPORT) y cada página trae hasta 10 000: sobra.
MAX_PAGINAS = 20


def _paginas(cliente: Any, grupo: str, desde_ms: int, hasta_ms: int | None) -> list[dict]:
    pedido: dict[str, Any] = {"logGroupName": grupo, "startTime": desde_ms}
    if hasta_ms is not None:
        pedido["endTime"] = hasta_ms
    eventos: list[dict] = []
    for _ in range(MAX_PAGINAS):
        respuesta = cliente.filter_log_events(**pedido)
        eventos += respuesta.get("events", [])
        token = respuesta.get("nextToken")
        if not token:
            break
        pedido["nextToken"] = token
    return eventos


def _registro(evento: dict, rol: str) -> tuple[str, dict] | None:
    """(réplica, registro) de una línea de CloudWatch, o None si no es una línea JSON del sistema."""
    try:
        registro = json.loads(evento.get("message", ""))
    except (TypeError, ValueError):
        return None  # START, END y REPORT de Lambda no son JSON
    if not isinstance(registro, dict) or "event" not in registro or "ts" not in registro:
        return None
    # Cada log stream es una instancia de la Lambda: se usa como «réplica».
    stream = str(evento.get("logStreamName", ""))
    replica = f"{rol}-{stream.rsplit(']', 1)[-1][:6] or '?'}"
    # Las Lambdas se nombran «ingesta»/«notifier»; el panel usa los roles de la versión local.
    return replica, {**registro, "service": rol}


class LectorCloudWatch:
    """Misma interfaz que LectorIncremental (`leer()` → [(réplica, registro)]), pero sobre CloudWatch.

    `grupos` va de rol del panel (`ingest`, `notifier`) a nombre del grupo de logs. Entrega cada
    línea UNA sola vez aunque las consultas se solapen (se deduplica por `eventId`).
    """

    def __init__(self, cliente: Any, grupos: dict[str, str], *, intervalo_s: float = 2.0,
                 retencion_s: float = 5.0, solape_s: float = 30.0, mirar_atras_s: float = 600.0,
                 reloj: Callable[[], float] = time.time) -> None:
        self._cliente = cliente
        self._grupos = grupos
        self._intervalo = intervalo_s
        self._retencion_ms = int(retencion_s * 1000)
        self._solape_ms = int(solape_s * 1000)
        self._mirar_atras_ms = int(mirar_atras_s * 1000)
        self._reloj = reloj
        self.error: str | None = None
        self.reiniciar()

    def reiniciar(self) -> None:
        """Vuelve a leer desde `mirar_atras_s` antes de ahora (al cambiar de entorno)."""
        self._ultima_consulta: float | None = None
        self._cursor_ms: int | None = None  # hora (ms) de la última línea entregada
        self._entregados: dict[str, int] = {}  # eventId → timestamp, para no repetir

    def leer(self) -> list[tuple[str, dict]]:
        ahora = self._reloj()
        if self._ultima_consulta is not None and ahora - self._ultima_consulta < self._intervalo:
            return []
        self._ultima_consulta = ahora
        ahora_ms = int(ahora * 1000)
        desde = (self._cursor_ms - self._solape_ms) if self._cursor_ms else ahora_ms - self._mirar_atras_ms
        limite = ahora_ms - self._retencion_ms  # lo más nuevo espera: puede faltar su pareja del otro grupo
        try:
            crudos = [(rol, e) for rol, grupo in self._grupos.items()
                      for e in _paginas(self._cliente, grupo, desde, None)]
        except Exception as exc:  # credenciales, red, cuota: el panel sigue y muestra el error
            self.error = f"{type(exc).__name__}: {exc}"
            return []
        self.error = None
        nuevos = []
        for rol, evento in crudos:
            marca, eid = int(evento.get("timestamp", 0)), evento.get("eventId")
            if marca > limite or not eid or eid in self._entregados:
                continue
            self._entregados[eid] = marca
            par = _registro(evento, rol)
            if par:
                nuevos.append((marca, par))
        if nuevos:
            self._cursor_ms = max(self._cursor_ms or 0, max(m for m, _ in nuevos))
        if self._cursor_ms:  # lo anterior al solape ya no puede volver a llegar en una consulta
            piso = self._cursor_ms - self._solape_ms
            self._entregados = {k: v for k, v in self._entregados.items() if v >= piso}
        nuevos.sort(key=lambda par: par[0])
        return [par for _, par in nuevos]


def leer_ventana(cliente: Any, grupos: dict[str, str], inicio: datetime, fin: datetime) -> list[tuple[str, dict]]:
    """Todas las líneas del sistema entre `inicio` y `fin` (para descargar los logs de una corrida)."""
    desde, hasta = int(inicio.timestamp() * 1000), int(fin.timestamp() * 1000)
    pares = [(int(e.get("timestamp", 0)), par) for rol, grupo in grupos.items()
             for e in _paginas(cliente, grupo, desde, hasta) if (par := _registro(e, rol))]
    pares.sort(key=lambda par: par[0])
    return [par for _, par in pares]


# Qué línea de la ingesta equivale a una respuesta HTTP y con qué código. Un Emergency deja dos
# líneas (RECEIVED y luego ENQUEUED o ENQUEUE_FAILED): se cuenta solo la segunda, que es la que
# decide la respuesta. Las peticiones inválidas (400) no se registran y no aparecen.
_RESPUESTA_DE = {"EVENT_RECEIVED": 200, "EMERGENCY_ENQUEUED": 200, "EMERGENCY_ENQUEUE_FAILED": 503}


def peticiones_desde_ingesta(registros: list[tuple[str, dict]]) -> list[dict]:
    """Peticiones en el formato del log de nginx (`msec`, `status`, `uri`) derivadas de la ingesta.

    Aproximación declarada: la hora es la de la Lambda al recibir (no la del envío de k6) y un
    429 de API Gateway no llega a la Lambda, así que no se cuenta.
    """
    peticiones = []
    for _, registro in registros:
        status = _RESPUESTA_DE.get(registro.get("event", ""))
        if status is None or registro.get("service") != "ingest":
            continue
        try:
            momento = datetime.fromisoformat(str(registro["ts"]).replace("Z", "+00:00"))
        except ValueError:
            continue
        peticiones.append({"msec": momento.timestamp(), "status": status, "uri": "/events"})
    return peticiones


def estado_sqs(cliente: Any, cola_url: str | None, dlq_url: str | None) -> dict[str, Any]:
    """Mismo formato que `estado_redis`: `stream` = mensajes visibles, `pendientes` = en vuelo."""
    if not cola_url or not dlq_url:
        return {"ok": False, "error": "faltan AWS_SQS_URL o AWS_SQS_DLQ_URL"}
    nombres = ["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"]
    try:
        cola = cliente.get_queue_attributes(QueueUrl=cola_url, AttributeNames=nombres)["Attributes"]
        dlq = cliente.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=nombres[:1])["Attributes"]
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"ok": True, "stream": int(cola["ApproximateNumberOfMessages"]),
            "pendientes": int(cola["ApproximateNumberOfMessagesNotVisible"]),
            "dlq": int(dlq["ApproximateNumberOfMessages"])}
