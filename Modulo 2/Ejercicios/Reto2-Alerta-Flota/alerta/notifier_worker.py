"""Worker del notifier: consume alertas, envía con concurrencia acotada, reintenta y manda a DLQ.

Tácticas: concurrencia acotada (desempeño), reintento con backoff y cola de mensajes
fallidos (disponibilidad). Entrega al-menos-una-vez: un correo duplicado es posible.
"""
from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime
from typing import Awaitable, Callable, Sequence

from alerta.logjson import JsonLogger, now_local
from alerta.ports import AlertConsumer, Delivery, Notifier


class NotifierWorker:
    def __init__(
        self,
        consumer: AlertConsumer,
        notifier: Notifier,
        log: JsonLogger,
        *,
        concurrency: int,
        max_attempts: int = 4,
        backoff_s: Sequence[float] = (1, 2, 4),
        block_ms: int = 1000,
        claim_idle_ms: int = 30_000,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if concurrency < 1:
            raise ValueError("concurrency debe ser >= 1")
        if len(backoff_s) < max_attempts - 1:
            raise ValueError("faltan esperas de backoff para los reintentos")
        self._consumer = consumer
        self._notifier = notifier
        self._log = log
        self._concurrency = concurrency
        self._max_attempts = max_attempts
        self._backoff_s = backoff_s
        self._block_ms = block_ms
        self._claim_idle_ms = claim_idle_ms
        self._sleep = sleep
        self._inflight: set[asyncio.Task[None]] = set()

    async def handle(self, delivery: Delivery) -> None:
        alert = delivery.alert
        ids = {"event_id": alert.event_id, "plate": alert.vehicle_plate}
        for attempt in range(1, self._max_attempts + 1):
            try:
                await self._notifier.send(alert)
            except Exception as exc:  # no sabemos qué fallo es transitorio: se reintenta todo
                error = f"{type(exc).__name__}: {exc}"
                if attempt == self._max_attempts:
                    await self._consumer.dead_letter(delivery, error)
                    self._log.log("EMAIL_DLQ", **ids, attempts=attempt, error=error)
                    return
                delay = self._backoff_s[attempt - 1]
                self._log.log("EMAIL_RETRY", **ids, attempt=attempt, error=error, retry_in_s=delay)
                await self._sleep(delay)
            else:
                self._log.log("EMAIL_SENT", **ids, attempt=attempt,
                              ms_since_received=_ms_since(alert.received_at))
                await self._consumer.ack(delivery.message_id)
                return

    async def run(self, stop: asyncio.Event) -> None:
        backlog = deque(await self._consumer.claim_stale(self._claim_idle_ms, count=100))
        if backlog:
            self._log.log("PENDING_CLAIMED", count=len(backlog))
        while not stop.is_set():
            free = self._concurrency - len(self._inflight)
            if free == 0:
                await asyncio.wait(self._inflight, return_when=asyncio.FIRST_COMPLETED)
                continue
            if backlog:
                batch = [backlog.popleft() for _ in range(min(free, len(backlog)))]
            else:
                batch = await self._consumer.fetch(count=free, block_ms=self._block_ms)
            for item in batch:
                self._spawn(item)
        if self._inflight:
            await asyncio.wait(self._inflight)

    def _spawn(self, delivery: Delivery) -> None:
        task = asyncio.create_task(self.handle(delivery))
        self._inflight.add(task)
        task.add_done_callback(self._on_done)

    def _on_done(self, task: asyncio.Task[None]) -> None:
        self._inflight.discard(task)
        if not task.cancelled() and task.exception() is not None:
            # p. ej. Redis caído al hacer XACK: el mensaje sigue pendiente y se reclama al reiniciar.
            self._log.log("WORKER_ERROR", error=repr(task.exception()))


def _ms_since(received_at: str) -> int:
    return round((now_local() - datetime.fromisoformat(received_at)).total_seconds() * 1000)
