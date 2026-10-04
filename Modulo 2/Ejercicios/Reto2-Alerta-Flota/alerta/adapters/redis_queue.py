"""Adaptador Redis Streams para la cola de emergencias.

Un mensaje leído queda «pendiente» hasta XACK (equivale a la visibilidad de SQS):
si el notifier cae a mitad del envío, otro consumidor lo reclama con XAUTOCLAIM.
"""
from __future__ import annotations

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from alerta.domain import EmergencyAlert
from alerta.ports import Delivery


class RedisAlertQueue:
    def __init__(self, client: Redis, *, stream: str, group: str, consumer: str, dlq_stream: str) -> None:
        self._redis = client
        self._stream = stream
        self._group = group
        self._consumer = consumer
        self._dlq_stream = dlq_stream

    async def ensure_group(self) -> None:
        try:
            # id="0": el grupo también ve lo publicado antes de que el notifier arrancara.
            await self._redis.xgroup_create(self._stream, self._group, id="0", mkstream=True)
        except ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    async def publish(self, alert: EmergencyAlert) -> None:
        await self._redis.xadd(self._stream, alert.to_fields())

    async def fetch(self, count: int, block_ms: int) -> list[Delivery]:
        response = await self._redis.xreadgroup(
            self._group, self._consumer, {self._stream: ">"}, count=count, block=block_ms
        )
        return [_delivery(mid, fields) for _, messages in (response or []) for mid, fields in messages]

    async def claim_stale(self, min_idle_ms: int, count: int) -> list[Delivery]:
        response = await self._redis.xautoclaim(
            self._stream, self._group, self._consumer,
            min_idle_time=min_idle_ms, start_id="0-0", count=count,
        )
        messages = response[1]
        return [_delivery(mid, fields) for mid, fields in messages if fields]

    async def ack(self, message_id: str) -> None:
        await self._redis.xack(self._stream, self._group, message_id)

    async def dead_letter(self, delivery: Delivery, error: str) -> None:
        await self._redis.xadd(self._dlq_stream, {**delivery.alert.to_fields(), "error": error})
        await self.ack(delivery.message_id)


def _delivery(message_id: str, fields: dict[str, str]) -> Delivery:
    return Delivery(message_id=message_id, alert=EmergencyAlert.from_fields(fields))
