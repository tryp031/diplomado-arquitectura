"""Lambda de ingesta (paso 2, camino B en AWS).

Misma lógica tolerante del sistema local (ver recepcion.py / ingest_app.py del Reto2-Alerta-Flota):
solo `type` es obligatorio, decide el flujo; placa faltante -> DESCONOCIDA; `Emergency` sin distinguir
mayúsculas. Responde en milisegundos, nunca espera al envío del correo.

Variable de entorno: QUEUE_URL (la URL de la cola SQS de emergencias). Mientras no exista (paso 2,
antes de crear SQS en el paso 3), cualquier Emergency responde 503 a propósito: nunca confirma una
alerta que no quedó guardada en ningún lado. Es el camino de error ya documentado en el diseño, no un
bug de esta prueba.
"""
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

COLOMBIA = timezone(timedelta(hours=-5))
sqs = boto3.client("sqs")


def _ahora() -> str:
    return datetime.now(COLOMBIA).isoformat(timespec="milliseconds")


def _log(evento: str, **campos) -> None:
    registro = {"ts": _ahora(), "service": "ingesta", "event": evento, **campos}
    print(json.dumps(registro, ensure_ascii=False))


def _respuesta(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def lambda_handler(event, context):
    try:
        payload = json.loads(event.get("body") or "{}")
    except (TypeError, ValueError):
        return _respuesta(400, {"error": "el cuerpo no es JSON válido"})

    if not isinstance(payload, dict):
        return _respuesta(400, {"error": "el payload debe ser un objeto JSON"})

    tipo = payload.get("type")
    if not isinstance(tipo, str) or not tipo.strip():
        return _respuesta(400, {"error": "falta 'type' o no es texto"})

    placa = payload.get("vehicle_plate")
    if not isinstance(placa, str) or not placa.strip():
        placa = "DESCONOCIDA"

    event_id = str(uuid.uuid4())
    ids = {"event_id": event_id, "plate": placa}

    if tipo.casefold() != "emergency":
        _log("EVENT_RECEIVED", **ids, type=tipo)
        return _respuesta(200, {"event_id": event_id, "status": "accepted"})

    received_at = _ahora()
    _log("EMERGENCY_RECEIVED", **ids)

    queue_url = os.environ.get("QUEUE_URL")
    try:
        if not queue_url:
            raise RuntimeError("QUEUE_URL no configurada todavía (paso 3 pendiente)")
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(
                {
                    "event_id": event_id,
                    "vehicle_plate": placa,
                    "status": payload.get("status") or "",
                    "received_at": received_at,
                },
                ensure_ascii=False,
            ),
        )
    except Exception as exc:  # preferimos un error visible a confirmar una alerta perdida
        _log("EMERGENCY_ENQUEUE_FAILED", **ids, error=f"{type(exc).__name__}: {exc}")
        return _respuesta(503, {"error": "no se pudo registrar la emergencia"})

    _log("EMERGENCY_ENQUEUED", **ids)
    return _respuesta(200, {"event_id": event_id, "status": "accepted"})
