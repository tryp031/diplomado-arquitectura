"""Lambda notifier: toma un Emergency de SQS y lo envía por correo con SES.

SQS (Simple Queue Service): cola de mensajes. SES (Simple Email Service): envío
de correo de AWS. DLQ (Dead Letter Queue): cola aparte donde se guardan los
mensajes que no se pudieron enviar, para revisarlos en vez de perderlos.

Entrada: evento de SQS (un mensaje por invocación) con event_id, vehicle_plate,
         status y received_at.
Salida:  siempre `batchItemFailures` vacío; los fallos se resuelven aquí, no por
         visibilidad de SQS.
Variables de entorno: MAIL_FROM, MAIL_TO, DLQ_URL.

Presupuesto de tiempo: 2 intentos de ~5 segundos cada uno y 1 segundo de espera entre ellos,
máximo ~12 segundos, para que el correo salga dentro de los 15 segundos.
Si ambos intentos fallan, el mensaje va a la DLQ de inmediato: dejar que SQS lo
reintente por visibilidad lo entregaría después de esos 15 segundos.
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from html import escape

import boto3
from botocore.config import Config

COLOMBIA = timezone(timedelta(hours=-5))
MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_TO = os.environ["MAIL_TO"]
DLQ_URL = os.environ["DLQ_URL"]
SUBJECT = "🚨 Alerta de Emergencia 🚨"

# max_attempts=1: el presupuesto de reintentos lo controla este código, no botocore.
# connect (2 s) + read (3 s) dan los ~5 s por intento.
ses = boto3.client("ses", config=Config(connect_timeout=2, read_timeout=3, retries={"max_attempts": 1}))
sqs = boto3.client("sqs")


def _ahora() -> datetime:
    return datetime.now(COLOMBIA)


def _log(evento: str, **campos) -> None:
    registro = {"ts": _ahora().isoformat(timespec="milliseconds"), "service": "notifier", "event": evento, **campos}
    print(json.dumps(registro, ensure_ascii=False))


def _build_message(alerta: dict) -> EmailMessage:
    estado = alerta.get("status") or "—"
    lineas = [
        ("Placa", alerta["vehicle_plate"]),
        ("Estado", estado),
        ("Evento", "Emergency"),
        ("Recibido", alerta["received_at"]),
        ("ID del evento", alerta["event_id"]),
    ]
    message = EmailMessage()
    message["Subject"] = SUBJECT
    message["From"] = MAIL_FROM
    message["To"] = MAIL_TO
    message.set_content("Alerta de Emergencia\n\n" + "\n".join(f"{k}: {v}" for k, v in lineas) + "\n")
    filas = "".join(f"<p><strong>{escape(k)}:</strong> {escape(str(v))}</p>" for k, v in lineas)
    message.add_alternative(f"<h2>Alerta de Emergencia</h2>{filas}", subtype="html")
    return message


def _enviar(alerta: dict) -> None:
    message = _build_message(alerta)
    ses.send_raw_email(Source=MAIL_FROM, Destinations=[MAIL_TO], RawMessage={"Data": message.as_bytes()})


def _ms_desde(received_at_iso: str) -> int:
    return round((_ahora() - datetime.fromisoformat(received_at_iso)).total_seconds() * 1000)


def lambda_handler(event, context):
    for record in event.get("Records", []):
        alerta = json.loads(record["body"])
        ids = {"event_id": alerta["event_id"], "plate": alerta["vehicle_plate"]}

        enviado = False
        intento = 0
        ultimo_error = None
        for intento in (1, 2):
            try:
                _enviar(alerta)
                enviado = True
                break
            except Exception as exc:
                # No se distingue el tipo de fallo: se reintenta todo una vez.
                ultimo_error = f"{type(exc).__name__}: {exc}"
                if intento == 1:
                    _log("EMAIL_RETRY", **ids, attempt=intento, error=ultimo_error, retry_in_s=1)
                    time.sleep(1)

        if enviado:
            _log("EMAIL_SENT", **ids, attempt=intento, ms_since_received=_ms_desde(alerta["received_at"]))
        else:
            sqs.send_message(
                QueueUrl=DLQ_URL,
                MessageBody=json.dumps({**alerta, "error": ultimo_error}, ensure_ascii=False),
            )
            _log("EMAIL_DLQ", **ids, attempts=2, error=ultimo_error)

    return {"batchItemFailures": []}
