"""Adaptador SMTP: Mailpit en desarrollo, Gmail (587 + STARTTLS + App Password) en la demo."""
from __future__ import annotations

from datetime import datetime
from email.message import EmailMessage
from html import escape

import aiosmtplib

from alerta.domain import EmergencyAlert
from alerta.logjson import COLOMBIA, now_local

SUBJECT = "🚨 Alerta de Emergencia 🚨"


def _hora(moment: datetime) -> str:
    return moment.astimezone(COLOMBIA).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " (UTC-05:00)"


def build_message(alert: EmergencyAlert, mail_from: str, mail_to: str, *, sent_at: datetime) -> EmailMessage:
    # sent_at es cuando el sistema arma y entrega el correo al SMTP, no cuando llega al buzón:
    # esa hora la pone Gmail. Si hay reintento, cada intento lleva su propia hora.
    received_at = datetime.fromisoformat(alert.received_at)
    demora_ms = round((sent_at - received_at).total_seconds() * 1000)
    estado = alert.status or "—"
    lineas = [
        ("Placa", alert.vehicle_plate),
        ("Estado", estado),
        ("Evento", "Emergency"),
        ("Hora de recepción del evento", _hora(received_at)),
        ("Hora de envío de la notificación", _hora(sent_at)),
        ("Tiempo de procesamiento", f"{demora_ms} ms"),
        ("ID del evento", alert.event_id),
    ]
    message = EmailMessage()
    message["Subject"] = SUBJECT
    message["From"] = mail_from
    message["To"] = mail_to
    message.set_content("Alerta de Emergencia\n\n" + "\n".join(f"{k}: {v}" for k, v in lineas) + "\n")
    filas = "".join(f"<p><strong>{escape(k)}:</strong> {escape(v)}</p>" for k, v in lineas)
    message.add_alternative(f"<h2>Alerta de Emergencia</h2>{filas}", subtype="html")
    return message


class SmtpNotifier:
    def __init__(self, *, host: str, port: int, username: str, password: str, starttls: bool,
                 mail_from: str, mail_to: str, timeout_s: float = 4.0) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._starttls = starttls
        self._mail_from = mail_from
        self._mail_to = mail_to
        self._timeout_s = timeout_s

    async def send(self, alert: EmergencyAlert) -> None:
        # Una conexión por correo: simple y suficiente con concurrencia acotada.
        # Si al medir la latencia lo exige, se cambia por una conexión reutilizada.
        await aiosmtplib.send(
            build_message(alert, self._mail_from, self._mail_to, sent_at=now_local()),
            hostname=self._host,
            port=self._port,
            username=self._username or None,
            password=self._password or None,
            start_tls=self._starttls,
            timeout=self._timeout_s,
        )
