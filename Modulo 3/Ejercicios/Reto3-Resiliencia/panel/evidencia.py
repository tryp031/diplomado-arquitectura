"""Cruza las dos miradas de una corrida, la del cliente (k6) y la del servidor (DynamoDB), y
arma los archivos descargables.

La coherencia es la prueba de que el panel no inventa nada: en cada minuto de reloj, el nivel
que respondieron las peticiones del k6 tiene que ser el nivel que el router fijó en la tabla.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any, Iterable

from panel.k6 import Iteracion

COLUMNAS = ("minuto_utc", "nivel_servidor", "errores", "peticiones", "niveles_cliente", "iteraciones", "coincide")


def _minuto(ts: str) -> int:
    return int(datetime.fromisoformat(ts).timestamp() // 60)


def coherencia(iteraciones: Iterable[Iteracion], minutos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    por_minuto: dict[int, list[Iteracion]] = {}
    for it in iteraciones:
        por_minuto.setdefault(_minuto(it.ts), []).append(it)
    servidor = {m["minuto"]: m for m in minutos}
    filas = []
    for m in sorted(set(por_minuto) | set(servidor)):
        cliente = por_minuto.get(m, [])
        s = servidor.get(m, {})
        niveles = sorted({i.nivel for i in cliente if i.nivel is not None})
        nivel_srv = s.get("nivel")
        coincide = None if not cliente or nivel_srv is None else niveles == [nivel_srv]
        filas.append({
            "minuto": m, "minuto_utc": datetime.fromtimestamp(m * 60, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "nivel_servidor": nivel_srv, "errores": s.get("errores", 0), "peticiones": s.get("peticiones", 0),
            "niveles_cliente": niveles,
            "iteraciones": f"{cliente[0].iteracion}-{cliente[-1].iteracion}" if cliente else "",
            "coincide": coincide,
        })
    return filas


def resumen_coherencia(filas: list[dict[str, Any]]) -> dict[str, Any]:
    evaluables = [f for f in filas if f["coincide"] is not None]
    return {"minutos": len(evaluables), "coinciden": sum(1 for f in evaluables if f["coincide"]),
            "todo_coincide": bool(evaluables) and all(f["coincide"] for f in evaluables)}


def como_csv(filas: list[dict[str, Any]]) -> str:
    salida = io.StringIO()
    w = csv.writer(salida, lineterminator="\n")
    w.writerow(COLUMNAS)
    for f in filas:
        w.writerow((f["minuto_utc"], f["nivel_servidor"] or "", f["errores"], f["peticiones"],
                    " ".join(map(str, f["niveles_cliente"])), f["iteraciones"],
                    "" if f["coincide"] is None else ("si" if f["coincide"] else "NO")))
    return salida.getvalue()


def como_jsonl(registros: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros)


def zip_evidencia(archivos: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in archivos.items():
            z.writestr(nombre, contenido)
    return buf.getvalue()
