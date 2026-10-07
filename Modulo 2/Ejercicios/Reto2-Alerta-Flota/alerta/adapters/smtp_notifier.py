"""Adaptador SMTP: Mailpit en desarrollo, Gmail (587 + STARTTLS + App Password) en la demo."""
from __future__ import annotations

from email.message import EmailMessage
from html import escape

import aiosmtplib

from alerta.domain import EmergencyAlert

SUBJECT = "🚨 Alerta de Emergencia 🚨"


def build_message(alert: EmergencyAlert, mail_from: str, mail_to: str) -> EmailMessage:
    estado = alert.status or "—"
    lineas = [
        ("Placa", alert.vehicle_plate),
        ("Estado", estado),
        ("Evento", "Emergency"),
        ("Recibido", alert.received_at),
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
            build_message(alert, self._mail_from, self._mail_to),
            hostname=self._host,
            port=self._port,
            username=self._username or None,
            password=self._password or None,
            start_tls=self._starttls,
            timeout=self._timeout_s,
        )
