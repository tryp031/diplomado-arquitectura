import httpx
import pytest

from alerta.ingest_app import create_app


class FakePublisher:
    def __init__(self, fail=False):
        self.fail = fail
        self.published = []

    async def publish(self, alert):
        if self.fail:
            raise ConnectionError("redis caído")
        self.published.append(alert)


@pytest.fixture
def client_for(captured_log):
    def make(publisher):
        app = create_app(publisher, captured_log.logger)
        return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
    return make


POSITION = {"type": "Position", "vehicle_plate": "ABC-123", "status": "OK",
            "coordinates": {"latitude": 12.345, "longitude": 67.89}}
EMERGENCY = {**POSITION, "type": "Emergency", "vehicle_plate": "VFH-600"}


async def test_position_responde_200_sin_encolar(client_for, captured_log):
    publisher = FakePublisher()
    async with client_for(publisher) as client:
        response = await client.post("/events", json=POSITION)
    assert response.status_code == 200
    assert response.json()["event_id"]
    assert publisher.published == []
    assert captured_log.names() == ["EVENT_RECEIVED"]


async def test_emergency_se_encola_con_el_mismo_event_id(client_for, captured_log):
    publisher = FakePublisher()
    async with client_for(publisher) as client:
        response = await client.post("/events", json=EMERGENCY)
    assert response.status_code == 200
    [alert] = publisher.published
    assert alert.event_id == response.json()["event_id"]
    assert (alert.vehicle_plate, alert.status) == ("VFH-600", "OK")
    assert alert.received_at.endswith("-05:00")
    assert captured_log.names() == ["EMERGENCY_RECEIVED", "EMERGENCY_ENQUEUED"]


async def test_emergency_con_cola_caida_responde_503(client_for, captured_log):
    async with client_for(FakePublisher(fail=True)) as client:
        response = await client.post("/events", json=EMERGENCY)
    assert response.status_code == 503
    assert captured_log.names() == ["EMERGENCY_RECEIVED", "EMERGENCY_ENQUEUE_FAILED"]


async def test_position_no_depende_de_la_cola(client_for):
    async with client_for(FakePublisher(fail=True)) as client:
        response = await client.post("/events", json=POSITION)
    assert response.status_code == 200


@pytest.mark.parametrize("body", [b"{no es json", b'{"type": "Position"}', b"[]"])
async def test_payload_invalido_responde_400(client_for, body):
    async with client_for(FakePublisher()) as client:
        response = await client.post("/events", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    assert "error" in response.json()


async def test_health(client_for):
    async with client_for(FakePublisher()) as client:
        response = await client.get("/health")
    assert response.json() == {"status": "ok"}
