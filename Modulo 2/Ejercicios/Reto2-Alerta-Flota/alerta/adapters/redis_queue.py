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
        try:
            response = await self._redis.xreadgroup(
                self._group, self._consumer, {self._stream: ">"}, count=count, block=block_ms
            )
        except ResponseError as exc:
            await self._recreate_group_if_missing(exc)
            return []
        return [_delivery(mid, fields) for _, messages in (response or []) for mid, fields in messages]

    async def claim_stale(self, min_idle_ms: int, count: int) -> list[Delivery]:
        deliveries: list[Delivery] = []
        start = "0-0"
        while len(deliveries) < count:
            try:
                next_start, messages, *_ = await self._redis.xautoclaim(
                    self._stream, self._group, self._consumer,
                    min_idle_time=min_idle_ms, start_id=start, count=count - len(deliveries),
                )
            except ResponseError as exc:
                await self._recreate_group_if_missing(exc)
                return deliveries
            deliveries += [_delivery(mid, fields) for mid, fields in messages if fields]
            if next_start == "0-0":  # el cursor dio la vuelta: no quedan pendientes
                break
            start = next_start
        return deliveries

    async def _recreate_group_if_missing(self, exc: ResponseError) -> None:
        # Redis es efímero: si se reinició, el stream y el grupo ya no existen.
        # Se consulta el estado real en vez de leer el texto del error (varía entre versiones).
        if await self._group_exists():
            raise exc
        await self.ensure_group()

    async def _group_exists(self) -> bool:
        try:
            groups = await self._redis.xinfo_groups(self._stream)
        except ResponseError:  # el stream no existe
            return False
        return any(group["name"] == self._group for group in groups)

    async def ack(self, message_id: str) -> None:
        await self._redis.xack(self._stream, self._group, message_id)

    async def dead_letter(self, delivery: Delivery, error: str) -> None:
        await self._redis.xadd(self._dlq_stream, {**delivery.alert.to_fields(), "error": error})
        await self.ack(delivery.message_id)


def _delivery(message_id: str, fields: dict[str, str]) -> Delivery:
    return Delivery(message_id=message_id, alert=EmergencyAlert.from_fields(fields))
