"""Logs estructurados en una línea JSON, con métricas en formato EMF.

CloudWatch Logs convierte el bloque _aws en métricas sin llamar a PutMetricData:
no agrega latencia ni permisos.
"""
import json
import time
from typing import Callable

NAMESPACE = "Reto3"
UNIDADES = {"LatenciaRouter": "Milliseconds"}


class Observabilidad:
    def __init__(self, servicio: str, escribir: Callable[[str], None] = print,
                 reloj: Callable[[], float] = time.time):
        self.servicio = servicio
        self._escribir = escribir
        self._reloj = reloj

    def emitir(self, evento: str, metricas: dict[str, float] | None = None, **campos) -> None:
        # Una línea JSON por evento, con el nombre del evento y el servicio que lo emite.
        registro = {"evento": evento, "servicio": self.servicio, **campos}
        # Bloque EMF: CloudWatch lo convierte en métricas del namespace Reto3, con la dimensión `servicio`.
        if metricas:
            registro["_aws"] = {
                "Timestamp": int(self._reloj() * 1000),
                "CloudWatchMetrics": [{
                    "Namespace": NAMESPACE,
                    "Dimensions": [["servicio"]],
                    "Metrics": [{"Name": n, "Unit": UNIDADES.get(n, "Count")} for n in metricas],
                }],
            }
            registro.update(metricas)
        self._escribir(json.dumps(registro, ensure_ascii=False))
