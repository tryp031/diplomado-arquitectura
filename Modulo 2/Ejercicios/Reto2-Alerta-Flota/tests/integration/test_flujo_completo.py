"""Flujo completo contra el sistema levantado con `docker compose --profile dev up`.

Correr con: .venv/bin/pytest -m integration
"""
import json
import os
import time
import urllib.request
from urllib.parse import quote

import pytest

pytestmark = pytest.mark.integration

GATEWAY = os.environ.get("GATEWAY_URL", "http://localhost:8080")
MAILPIT = os.environ.get("MAILPIT_URL", "http://localhost:8025")


def post_event(payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        f"{GATEWAY}/events", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status, json.load(response)


def mailpit_count(text: str) -> int:
    with urllib.request.urlopen(f"{MAILPIT}/api/v1/search?query={quote(text)}", timeout=5) as response:
        return json.load(response).get("messages_count", 0)


def test_position_responde_200():
    status, body = post_event({"type": "Position", "vehicle_plate": "ABC-123", "status": "OK"})
    assert status == 200 and body["status"] == "accepted"


def test_emergency_llega_como_correo_en_menos_de_15_s():
    status, body = post_event({"type": "Emergency", "vehicle_plate": "VFH-600", "status": "OK"})
    assert status == 200
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if mailpit_count(body["event_id"]) > 0:
            return
        time.sleep(0.5)
    pytest.fail(f"no llegó correo para {body['event_id']} en 15 s")
