import asyncio
from collections import deque

import pytest

from alerta.domain import EmergencyAlert
from alerta.logjson import format_ts, now_local
from alerta.notifier_worker import NotifierWorker
from alerta.ports import Delivery


def delivery(i: int) -> Delivery:
    return Delivery(f"{i}-0", EmergencyAlert(f"ev-{i}", "VFH-600", "OK", format_ts(now_local())))


class FakeConsumer:
    def __init__(self, deliveries=(), stale=()):
        self.queue = deque(deliveries)
        self.stale = list(stale)
        self.acked: list[str] = []
        self.dead: list[tuple[str, str]] = []

    async def fetch(self, count, block_ms):
        items = [self.queue.popleft() for _ in range(min(count, len(self.queue)))]
        if not items:
            await asyncio.sleep(0.001)  # imita el BLOCK de Redis
        return items

    async def claim_stale(self, min_idle_ms, count):
        stale, self.stale = self.stale, []
        return stale

    async def ack(self, message_id):
        self.acked.append(message_id)

    async def dead_letter(self, d, error):
        self.dead.append((d.message_id, error))


class FakeNotifier:
    def __init__(self, failures=0, always_fail=False, delay_s=0.0):
        self.failures, self.always_fail, self.delay_s = failures, always_fail, delay_s
        self.calls = 0
        self.sent: list[str] = []
        self.in_flight = 0
        self.max_in_flight = 0

    async def send(self, alert):
        self.calls += 1
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        try:
            await asyncio.sleep(self.delay_s)
            if self.always_fail or self.calls <= self.failures:
                raise ConnectionError("smtp caído")
            self.sent.append(alert.event_id)
        finally:
            self.in_flight -= 1


def worker(consumer, notifier, log, sleeps, concurrency=5):
    async def fake_sleep(seconds):
        sleeps.append(seconds)

    return NotifierWorker(consumer, notifier, log, concurrency=concurrency, sleep=fake_sleep, block_ms=1)


async def run_until(w, done, timeout=2.0):
    stop = asyncio.Event()
    task = asyncio.create_task(w.run(stop))

    async def esperar():
        while not done():
            await asyncio.sleep(0.005)

    await asyncio.wait_for(esperar(), timeout)
    stop.set()
    await asyncio.wait_for(task, timeout)


async def test_envio_exitoso_registra_y_confirma(captured_log):
    consumer, notifier, sleeps = FakeConsumer(), FakeNotifier(), []
    await worker(consumer, notifier, captured_log.logger, sleeps).handle(delivery(1))
    assert notifier.sent == ["ev-1"]
    assert consumer.acked == ["1-0"]
    [record] = captured_log.records()
    assert record["event"] == "EMAIL_SENT"
    assert record["event_id"] == "ev-1"
    assert record["ms_since_received"] >= 0


async def test_falla_transitoria_reintenta_con_backoff_y_envia(captured_log):
    consumer, notifier, sleeps = FakeConsumer(), FakeNotifier(failures=2), []
    await worker(consumer, notifier, captured_log.logger, sleeps).handle(delivery(1))
    assert sleeps == [1, 2]
    assert captured_log.names() == ["EMAIL_RETRY", "EMAIL_RETRY", "EMAIL_SENT"]
    assert consumer.acked == ["1-0"]


async def test_falla_persistente_va_a_dlq(captured_log):
    consumer, notifier, sleeps = FakeConsumer(), FakeNotifier(always_fail=True), []
    await worker(consumer, notifier, captured_log.logger, sleeps).handle(delivery(1))
    assert notifier.calls == 4
    assert sleeps == [1, 2, 4]
    assert consumer.dead == [("1-0", "ConnectionError: smtp caído")]
    assert consumer.acked == []
    assert captured_log.names()[-1] == "EMAIL_DLQ"


async def test_run_respeta_la_concurrencia_maxima(captured_log):
    consumer = FakeConsumer(deliveries=[delivery(i) for i in range(6)])
    notifier = FakeNotifier(delay_s=0.02)
    w = worker(consumer, notifier, captured_log.logger, [], concurrency=2)
    await run_until(w, lambda: len(notifier.sent) == 6)
    assert notifier.max_in_flight == 2


async def test_run_procesa_primero_los_pendientes_reclamados(captured_log):
    consumer = FakeConsumer(stale=[delivery(9)])
    notifier = FakeNotifier()
    await run_until(worker(consumer, notifier, captured_log.logger, []), lambda: notifier.sent == ["ev-9"])
    assert "PENDING_CLAIMED" in captured_log.names()


def test_concurrencia_invalida(captured_log):
    with pytest.raises(ValueError):
        NotifierWorker(FakeConsumer(), FakeNotifier(), captured_log.logger, concurrency=0)
