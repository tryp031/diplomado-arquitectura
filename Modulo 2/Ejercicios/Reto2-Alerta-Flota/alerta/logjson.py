"""Logs estructurados: una línea JSON por evento, hora Colombia (-05:00) con milisegundos.

La hora local evita que quien evalúa convierta desde UTC al compararla con Gmail.
"""
from __future__ import annotations

import json
import socket
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, TextIO

COLOMBIA = timezone(timedelta(hours=-5))  # Colombia no tiene horario de verano


def now_local() -> datetime:
    return datetime.now(COLOMBIA)


def format_ts(moment: datetime) -> str:
    return moment.astimezone(COLOMBIA).isoformat(timespec="milliseconds")


class JsonLogger:
    def __init__(self, service: str, log_dir: str | None = None, stream: TextIO = sys.stdout) -> None:
        self._service = service
        self._stream = stream
        self._file: TextIO | None = None
        if log_dir:
            directory = Path(log_dir)
            directory.mkdir(parents=True, exist_ok=True)
            # Un archivo por réplica: dos contenedores nunca escriben el mismo archivo.
            path = directory / f"{service}-{socket.gethostname()}.log"
            self._file = path.open("a", encoding="utf-8", buffering=1)

    def log(self, event: str, **fields: Any) -> dict[str, Any]:
        record = {"ts": format_ts(now_local()), "service": self._service, "event": event, **fields}
        line = json.dumps(record, ensure_ascii=False)
        print(line, file=self._stream, flush=True)
        if self._file is not None:
            self._file.write(line + "\n")
        return record
