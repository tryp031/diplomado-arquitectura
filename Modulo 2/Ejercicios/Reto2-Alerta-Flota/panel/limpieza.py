"""Borrar los datos de las pruebas para empezar una corrida con data limpia (botón del panel).

Los logs se VACÍAN, no se eliminan: cada servicio tiene su archivo abierto en modo append y, si se
borrara, seguiría escribiendo en un archivo que ya nadie ve. Al truncarlo, el servicio sigue
escribiendo desde cero en el mismo archivo y el lector del panel detecta el truncado.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

PATRONES_LOG = ("ingest-*.log", "notifier-*.log", "nginx/gateway-access.log")


def vaciar_logs(log_dir: Path) -> int:
    vaciados = 0
    for patron in PATRONES_LOG:
        for path in log_dir.glob(patron):
            with path.open("r+b") as archivo:
                archivo.truncate(0)
            vaciados += 1
    (log_dir / "k6-summary.json").unlink(missing_ok=True)
    return vaciados


async def vaciar_redis(client: Any, stream: str, dlq_stream: str) -> None:
    # XTRIM y no DEL: borrar el stream se llevaría el consumer group y el notifier quedaría sin él.
    await client.xtrim(stream, maxlen=0, approximate=False)
    await client.delete(dlq_stream)
