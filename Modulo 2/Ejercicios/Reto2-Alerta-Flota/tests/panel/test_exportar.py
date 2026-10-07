import csv
import io
import json
from datetime import datetime, timedelta, timezone

import pytest

from panel.exportar import GRACIA, como_csv, como_log, registros_de_carga

COL = timezone(timedelta(hours=-5))
INICIO = datetime(2026, 10, 12, 23, 0, 0, tzinfo=COL)
FIN = datetime(2026, 10, 12, 23, 0, 30, tzinfo=COL)


def _linea(ts, **campos):
    return json.dumps({"ts": ts, **campos}) + "\n"


@pytest.fixture
def logs(tmp_path):
    (tmp_path / "nginx").mkdir()
    (tmp_path / "ingest-aaa.log").write_text(
        _linea("2026-10-12T22:59:59.999-05:00", service="ingest", event="EVENT_RECEIVED", event_id="antes")
        + _linea("2026-10-12T23:00:01.000-05:00", service="ingest", event="EMERGENCY_RECEIVED",
                 event_id="e1", plate="VFH-600")
        + "{no es json\n",
        encoding="utf-8")
    (tmp_path / "notifier-bbb.log").write_text(
        _linea("2026-10-12T23:00:02.500-05:00", service="notifier", event="EMAIL_SENT", event_id="e1",
               plate="VFH-600", attempt=1, ms_since_received=1500)
        # dentro de la gracia: un correo reintentado que sale después de que k6 terminó
        + _linea("2026-10-12T23:01:20.000-05:00", service="notifier", event="EMAIL_SENT", event_id="tarde")
        # fuera de la gracia: un Emergency manual enviado mucho después
        + _linea("2026-10-12T23:05:00.000-05:00", service="notifier", event="EMAIL_SENT", event_id="manual"),
        encoding="utf-8")
    # 23:00:00.500 -05:00 = 04:00:00.500 UTC
    msec = datetime(2026, 10, 13, 4, 0, 0, 500_000, tzinfo=timezone.utc).timestamp()
    (tmp_path / "nginx" / "gateway-access.log").write_text(
        json.dumps({"msec": msec, "status": 200, "request_time": 0.004, "method": "POST", "uri": "/events"})
        + "\n", encoding="utf-8")
    return tmp_path


def test_reune_servicios_y_gateway_de_la_ventana_ordenados_por_hora(logs):
    registros = registros_de_carga(logs, INICIO, FIN)
    assert [(r["service"], r["event"], r.get("event_id")) for r in registros] == [
        ("gateway", "HTTP_REQUEST", None),
        ("ingest", "EMERGENCY_RECEIVED", "e1"),
        ("notifier", "EMAIL_SENT", "e1"),
        ("notifier", "EMAIL_SENT", "tarde"),
    ]


def test_la_ventana_excluye_lo_anterior_a_k6_y_lo_posterior_a_la_gracia(logs):
    ids = {r.get("event_id") for r in registros_de_carga(logs, INICIO, FIN)}
    assert "antes" not in ids and "manual" not in ids
    assert GRACIA == timedelta(seconds=60)


def test_el_log_de_nginx_se_normaliza_a_hora_colombia_y_conserva_la_replica(logs):
    gateway, ingest, *_ = registros_de_carga(logs, INICIO, FIN)
    assert gateway["ts"] == "2026-10-12T23:00:00.500-05:00"
    assert (gateway["status"], gateway["request_time"], gateway["replica"]) == (200, 0.004, "gateway-access")
    assert ingest["replica"] == "ingest-aaa"


def test_sin_logs_devuelve_lista_vacia(tmp_path):
    assert registros_de_carga(tmp_path, INICIO, FIN) == []


def test_como_log_es_una_linea_json_por_registro(logs):
    texto = como_log(registros_de_carga(logs, INICIO, FIN))
    lineas = texto.splitlines()
    assert len(lineas) == 4
    assert json.loads(lineas[2])["ms_since_received"] == 1500


def test_como_csv_tiene_columnas_fijas_y_el_resto_en_detalle(logs):
    filas = list(csv.DictReader(io.StringIO(como_csv(registros_de_carga(logs, INICIO, FIN)))))
    assert list(filas[0]) == ["ts", "service", "replica", "event", "event_id", "plate", "detalle"]
    correo = filas[2]
    assert (correo["event"], correo["event_id"], correo["plate"]) == ("EMAIL_SENT", "e1", "VFH-600")
    assert json.loads(correo["detalle"]) == {"attempt": 1, "ms_since_received": 1500}
    assert json.loads(filas[0]["detalle"])["status"] == 200
