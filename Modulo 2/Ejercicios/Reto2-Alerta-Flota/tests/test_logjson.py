import io
import json
from datetime import datetime, timezone

from alerta.logjson import JsonLogger, format_ts


def test_format_ts_usa_hora_colombia_con_milisegundos():
    moment = datetime(2026, 10, 13, 4, 4, 11, 482000, tzinfo=timezone.utc)
    assert format_ts(moment) == "2026-10-12T23:04:11.482-05:00"


def test_logger_escribe_una_linea_json_en_stream_y_archivo(tmp_path):
    stream = io.StringIO()
    logger = JsonLogger("ingest", log_dir=str(tmp_path), stream=stream)

    logger.log("EMERGENCY_RECEIVED", event_id="ev-1", plate="VFH-600")

    record = json.loads(stream.getvalue())
    assert record["service"] == "ingest"
    assert record["event"] == "EMERGENCY_RECEIVED"
    assert record["event_id"] == "ev-1"
    assert record["ts"].endswith("-05:00")
    files = list(tmp_path.glob("ingest-*.log"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8")) == record


def test_logger_sin_directorio_solo_escribe_en_stream():
    stream = io.StringIO()
    JsonLogger("notifier", stream=stream).log("EMAIL_SENT", event_id="ev-1")
    assert json.loads(stream.getvalue())["event"] == "EMAIL_SENT"
