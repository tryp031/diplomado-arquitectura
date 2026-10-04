import fakeredis
import pytest

from alerta.adapters.redis_queue import RedisAlertQueue
from alerta.domain import EmergencyAlert

ALERT = EmergencyAlert("ev-1", "VFH-600", "OK", "2026-10-12T23:04:11.482-05:00")


@pytest.fixture
def client():
    return fakeredis.FakeAsyncRedis(decode_responses=True)


def queue(client, consumer="c1"):
    return RedisAlertQueue(client, stream="em", group="g", consumer=consumer, dlq_stream="em-dlq")


async def test_ensure_group_es_idempotente(client):
    q = queue(client)
    await q.ensure_group()
    await q.ensure_group()


async def test_publica_y_consume_la_misma_alerta(client):
    q = queue(client)
    await q.ensure_group()
    await q.publish(ALERT)
    [delivery] = await q.fetch(count=10, block_ms=10)
    assert delivery.alert == ALERT


async def test_fetch_sin_mensajes_devuelve_lista_vacia(client):
    q = queue(client)
    await q.ensure_group()
    assert await q.fetch(count=10, block_ms=10) == []


async def test_ack_saca_el_mensaje_de_pendientes(client):
    q = queue(client)
    await q.ensure_group()
    await q.publish(ALERT)
    [delivery] = await q.fetch(count=1, block_ms=10)
    await q.ack(delivery.message_id)
    assert (await client.xpending("em", "g"))["pending"] == 0


async def test_dead_letter_copia_a_dlq_con_error_y_confirma(client):
    q = queue(client)
    await q.ensure_group()
    await q.publish(ALERT)
    [delivery] = await q.fetch(count=1, block_ms=10)
    await q.dead_letter(delivery, "SMTPException: caído")
    [(_, fields)] = await client.xrange("em-dlq")
    assert fields["event_id"] == "ev-1"
    assert fields["error"] == "SMTPException: caído"
    assert (await client.xpending("em", "g"))["pending"] == 0


async def test_otro_consumidor_reclama_pendientes_sin_confirmar(client):
    caido, nuevo = queue(client, "caido"), queue(client, "nuevo")
    await caido.ensure_group()
    await caido.publish(ALERT)
    await caido.fetch(count=1, block_ms=10)  # lo toma y "se cae" sin ack
    [delivery] = await nuevo.claim_stale(min_idle_ms=0, count=10)
    assert delivery.alert == ALERT


async def test_si_redis_se_reinicio_fetch_recrea_el_grupo(client):
    q = queue(client)
    await q.ensure_group()
    await client.flushall()  # Redis efímero reiniciado: ya no existen ni el stream ni el grupo
    assert await q.fetch(count=1, block_ms=10) == []
    await q.publish(ALERT)
    [delivery] = await q.fetch(count=1, block_ms=10)
    assert delivery.alert == ALERT


async def test_si_redis_se_reinicio_claim_stale_recrea_el_grupo(client):
    q = queue(client)
    await q.ensure_group()
    await client.flushall()
    assert await q.claim_stale(min_idle_ms=0, count=10) == []


async def test_claim_stale_recorre_el_cursor_hasta_count(client):
    caido, nuevo = queue(client, "caido"), queue(client, "nuevo")
    await caido.ensure_group()
    for i in range(5):
        await caido.publish(EmergencyAlert(f"ev-{i}", "VFH-600", "OK", ALERT.received_at))
    await caido.fetch(count=5, block_ms=10)
    claimed = await nuevo.claim_stale(min_idle_ms=0, count=5)
    assert sorted(d.alert.event_id for d in claimed) == [f"ev-{i}" for i in range(5)]
