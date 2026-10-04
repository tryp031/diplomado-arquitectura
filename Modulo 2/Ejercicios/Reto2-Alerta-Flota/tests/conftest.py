import io
import json

import pytest

from alerta.logjson import JsonLogger


class CapturedLog:
    def __init__(self) -> None:
        self.stream = io.StringIO()
        self.logger = JsonLogger("test", stream=self.stream)

    def records(self) -> list[dict]:
        return [json.loads(line) for line in self.stream.getvalue().splitlines()]

    def names(self) -> list[str]:
        return [record["event"] for record in self.records()]


@pytest.fixture
def captured_log() -> CapturedLog:
    return CapturedLog()
