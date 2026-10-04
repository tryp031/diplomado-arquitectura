import pytest

from alerta.domain import UNKNOWN_PLATE, EmergencyAlert, InvalidEvent, VehicleEvent


def test_payload_del_enunciado_es_valido():
    event = VehicleEvent.from_payload({
        "type": "Position",
        "vehicle_plate": "ABC-123",
        "coordinates": {"latitude": 12.345, "longitude": 67.890},
        "status": "OK",
    })
    assert event == VehicleEvent(type="Position", vehicle_plate="ABC-123", status="OK")
    assert not event.is_emergency()


def test_emergency_se_detecta():
    assert VehicleEvent.from_payload({"type": "Emergency", "vehicle_plate": "VFH-600"}).is_emergency()


@pytest.mark.parametrize("tipo", ["emergency", "EMERGENCY", " Emergency "])
def test_emergency_no_distingue_mayusculas_ni_espacios(tipo):
    assert VehicleEvent.from_payload({"type": tipo, "vehicle_plate": "VFH-600"}).is_emergency()


def test_campos_extra_se_ignoran():
    event = VehicleEvent.from_payload(
        {"type": "Emergency", "vehicle_plate": "X-1", "speed": 80, "driver": {"id": 1}}
    )
    assert event.vehicle_plate == "X-1"


def test_type_desconocido_es_valido_pero_no_es_emergencia():
    assert not VehicleEvent.from_payload({"type": "Maintenance", "vehicle_plate": "X-1"}).is_emergency()


def test_status_que_no_es_texto_se_descarta():
    assert VehicleEvent.from_payload({"type": "Position", "vehicle_plate": "X-1", "status": 3}).status is None


@pytest.mark.parametrize("payload", [
    None,
    [],
    "texto",
    {"vehicle_plate": "X-1"},
    {"type": "", "vehicle_plate": "X-1"},
    {"type": 7, "vehicle_plate": "X-1"},
])
def test_payload_invalido(payload):
    with pytest.raises(InvalidEvent):
        VehicleEvent.from_payload(payload)


def test_alerta_ida_y_vuelta_por_campos_de_texto():
    alert = EmergencyAlert(
        event_id="ev-1", vehicle_plate="VFH-600", status="OK",
        received_at="2026-10-12T23:04:11.482-05:00",
    )
    fields = alert.to_fields()
    assert all(isinstance(v, str) for v in fields.values())
    assert EmergencyAlert.from_fields(fields) == alert


@pytest.mark.parametrize("placa", [None, "", "  "])
def test_emergency_sin_placa_se_acepta_como_desconocida(placa):
    # Perder una emergencia por un dato faltante es peor que alertar sin placa.
    payload = {"type": "Emergency"} if placa is None else {"type": "Emergency", "vehicle_plate": placa}
    event = VehicleEvent.from_payload(payload)
    assert event.is_emergency()
    assert event.vehicle_plate == UNKNOWN_PLATE == "DESCONOCIDA"


def test_placa_numerica_se_convierte_a_texto():
    assert VehicleEvent.from_payload({"type": "Position", "vehicle_plate": 123}).vehicle_plate == "123"
