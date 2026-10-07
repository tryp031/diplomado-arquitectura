"""Configuración por variables de entorno (12-factor). Los valores por defecto apuntan a Mailpit."""
from __future__ import annotations

import os
import socket
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    redis_url: str
    stream: str
    dlq_stream: str
    group: str
    consumer: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_starttls: bool
    mail_from: str
    mail_to: str
    notifier_concurrency: int
    max_attempts: int
    smtp_timeout_s: float
    log_dir: str | None


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "si", "sí"}


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env
    concurrency = int(env.get("NOTIFIER_CONCURRENCY", "5"))
    if concurrency < 1:
        raise ValueError("NOTIFIER_CONCURRENCY debe ser >= 1")
    max_attempts = int(env.get("MAX_ATTEMPTS", "4"))
    if max_attempts < 1:
        raise ValueError("MAX_ATTEMPTS debe ser >= 1")
    # Por operación de red (conectar, TLS, AUTH, DATA). Corto a propósito: una conexión colgada
    # debe cortarla aiosmtplib y reintentarse, no consumir los 15 s que da la rúbrica.
    smtp_timeout_s = float(env.get("SMTP_TIMEOUT_S", "4"))
    if smtp_timeout_s <= 0:
        raise ValueError("SMTP_TIMEOUT_S debe ser > 0")
    return Settings(
        redis_url=env.get("REDIS_URL", "redis://localhost:6379/0"),
        stream=env.get("STREAM", "emergencies"),
        dlq_stream=env.get("DLQ_STREAM", "emergencies-dlq"),
        group=env.get("CONSUMER_GROUP", "notifiers"),
        consumer=env.get("CONSUMER_NAME", socket.gethostname()),
        smtp_host=env.get("SMTP_HOST", "mailpit"),
        smtp_port=int(env.get("SMTP_PORT", "1025")),
        smtp_user=env.get("SMTP_USER", ""),
        smtp_password=env.get("SMTP_PASSWORD", ""),
        smtp_starttls=_as_bool(env.get("SMTP_STARTTLS", "false")),
        mail_from=env.get("MAIL_FROM", "alertas@reto2.local"),
        mail_to=env.get("MAIL_TO", "danny@reto2.local"),
        notifier_concurrency=concurrency,
        max_attempts=max_attempts,
        smtp_timeout_s=smtp_timeout_s,
        log_dir=env.get("LOG_DIR") or None,
    )
