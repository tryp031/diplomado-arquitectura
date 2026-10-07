"""Exporta los logs de UNA carga (ingest, notifier y gateway) como evidencia descargable.

La ventana va del arranque de k6 a su fin más una gracia: un correo reintentado puede salir
después de que k6 terminó (la cadena de reintentos más larga dura ~39 s) y sigue siendo de
esa carga. Lo posterior a la gracia, p. ej. un Emergency manual, ya no lo es.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from panel.agregador import LectorIncremental

GRACIA = timedelta(seconds=60)
COLOMBIA = timezone(timedelta(hours=-5))
COLUMNAS = ("ts", "service", "replica", "event", "event_id", "plate")


def registros_de_carga(log_dir: Path, inicio: datetime, fin: datetime) -> list[dict[str, Any]]:
    hasta = fin + GRACIA
    # Un lector nuevo lee los archivos desde el principio: no comparte posición con el del panel.
    servicios = LectorIncremental(log_dir, ("ingest-*.log", "notifier-*.log")).leer()
    nginx = LectorIncremental(log_dir / "nginx", ("gateway-access.log",)).leer()
    candidatos = [(replica, r) for replica, r in servicios if "ts" in r]
    candidatos += [(replica, _desde_nginx(r)) for replica, r in nginx if "msec" in r]
    dentro = []
    for replica, registro in candidatos:
        try:
            momento = datetime.fromisoformat(registro["ts"])
        except (TypeError, ValueError):
            continue
        if inicio <= momento <= hasta:
            dentro.append((momento, {**registro, "replica": replica}))
    dentro.sort(key=lambda par: par[0])
    return [registro for _, registro in dentro]


def _desde_nginx(registro: dict[str, Any]) -> dict[str, Any]:
    momento = datetime.fromtimestamp(registro["msec"], COLOMBIA)
    resto = {k: v for k, v in registro.items() if k != "msec"}
    return {"ts": momento.isoformat(timespec="milliseconds"), "service": "gateway",
            "event": "HTTP_REQUEST", **resto}


def como_log(registros: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros)


def como_csv(registros: list[dict[str, Any]]) -> str:
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow((*COLUMNAS, "detalle"))
    for registro in registros:
        detalle = {k: v for k, v in registro.items() if k not in COLUMNAS}
        escritor.writerow((*(registro.get(c, "") for c in COLUMNAS),
                           json.dumps(detalle, ensure_ascii=False) if detalle else ""))
    return salida.getvalue()
