"""Cruza las miradas de una corrida y arma los archivos descargables:

- cliente: el nivel que respondieron las peticiones del k6 en cada minuto de reloj;
- servidor: el nivel que el router fijó en DynamoDB (si hay permiso de lectura);
- regla: el nivel que predice src/reglas.py con los errores (status ≥ 500) que vio el propio k6.

Que las tres coincidan es la prueba de que el panel no inventa nada. La regla se puede verificar
aun sin leer el servidor, solo con la salida del k6. Supuesto: el minuto anterior a la corrida no
tuvo errores (el sistema arranca en N1) y los relojes de cliente y servidor están sincronizados.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any, Iterable

from estado import RegistroMinuto
from panel.k6 import Iteracion
from reglas import Umbrales, decision_para

COLUMNAS = ("minuto_utc", "nivel_servidor", "errores", "peticiones", "niveles_cliente", "iteraciones", "coincide",
            "errores_cliente", "nivel_regla", "coincide_regla")


def _minuto(ts: str) -> int:
    return int(datetime.fromisoformat(ts).timestamp() // 60)


def prediccion(por_minuto: dict[int, list[Iteracion]], u: Umbrales) -> dict[int, int]:
    """Nivel que la regla le asigna a cada minuto con tráfico del cliente, desde los errores que vio el k6."""
    registros: dict[int, RegistroMinuto] = {}
    out = {}
    for m in sorted(por_minuto):
        d = decision_para(m, registros, u)
        errores = sum(1 for i in por_minuto[m] if i.status >= 500)
        registros[m] = RegistroMinuto(nivel=d.nivel, errores=errores, degradado_en=d.degradado_en)
        out[m] = d.nivel
    return out


def coherencia(iteraciones: Iterable[Iteracion], minutos: list[dict[str, Any]],
               u: Umbrales = Umbrales()) -> list[dict[str, Any]]:
    por_minuto: dict[int, list[Iteracion]] = {}
    for it in iteraciones:
        por_minuto.setdefault(_minuto(it.ts), []).append(it)
    servidor = {m["minuto"]: m for m in minutos}
    regla = prediccion(por_minuto, u)
    filas = []
    for m in sorted(set(por_minuto) | set(servidor)):
        cliente = por_minuto.get(m, [])
        s = servidor.get(m, {})
        niveles = sorted({i.nivel for i in cliente if i.nivel is not None})
        nivel_srv = s.get("nivel")
        coincide = None if not cliente or nivel_srv is None else niveles == [nivel_srv]
        esperado = regla.get(m)
        filas.append({
            "minuto": m, "minuto_utc": datetime.fromtimestamp(m * 60, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "nivel_servidor": nivel_srv, "errores": s.get("errores", 0), "peticiones": s.get("peticiones", 0),
            "niveles_cliente": niveles,
            "iteraciones": f"{cliente[0].iteracion}-{cliente[-1].iteracion}" if cliente else "",
            "coincide": coincide,
            "errores_cliente": sum(1 for i in cliente if i.status >= 500),
            "nivel_regla": esperado,
            "coincide_regla": None if not niveles or esperado is None else niveles == [esperado],
        })
    return filas


def resumen_coherencia(filas: list[dict[str, Any]]) -> dict[str, Any]:
    evaluables = [f for f in filas if f["coincide"] is not None]
    con_regla = [f for f in filas if f.get("coincide_regla") is not None]
    return {"minutos": len(evaluables), "coinciden": sum(1 for f in evaluables if f["coincide"]),
            "todo_coincide": bool(evaluables) and all(f["coincide"] for f in evaluables),
            "minutos_regla": len(con_regla), "coinciden_regla": sum(1 for f in con_regla if f["coincide_regla"]),
            "regla_se_cumple": bool(con_regla) and all(f["coincide_regla"] for f in con_regla)}


def como_csv(filas: list[dict[str, Any]]) -> str:
    salida = io.StringIO()
    w = csv.writer(salida, lineterminator="\n")
    w.writerow(COLUMNAS)
    for f in filas:
        w.writerow((f["minuto_utc"], f["nivel_servidor"] or "", f["errores"], f["peticiones"],
                    " ".join(map(str, f["niveles_cliente"])), f["iteraciones"],
                    "" if f["coincide"] is None else ("si" if f["coincide"] else "NO"),
                    f.get("errores_cliente", ""), f.get("nivel_regla") or "",
                    "" if f.get("coincide_regla") is None else ("si" if f["coincide_regla"] else "NO")))
    return salida.getvalue()


def como_jsonl(registros: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros)


def zip_evidencia(archivos: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in archivos.items():
            z.writestr(nombre, contenido)
    return buf.getvalue()
