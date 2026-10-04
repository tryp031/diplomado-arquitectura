"""Puertos: lo que el núcleo necesita del mundo exterior. Redis/SMTP hoy, SQS/SES mañana."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from alerta.domain import EmergencyAlert


@dataclass(frozen=True)
class Delivery:
    """Una alerta entregada por la cola, con el id que hay que confirmar."""

    message_id: str
    alert: EmergencyAlert


class AlertPublisher(Protocol):
    async def publish(self, alert: EmergencyAlert) -> None: ...


class AlertConsumer(Protocol):
    async def fetch(self, count: int, block_ms: int) -> list[Delivery]: ...

    async def claim_stale(self, min_idle_ms: int, count: int) -> list[Delivery]: ...

    async def ack(self, message_id: str) -> None: ...

    async def dead_letter(self, delivery: Delivery, error: str) -> None: ...


class Notifier(Protocol):
    async def send(self, alert: EmergencyAlert) -> None: ...
