"""Cruza las miradas de una corrida (v3, histéresis) y arma los archivos descargables:

- cliente: el nivel que respondió cada petición del k6;
- servidor: el nivel con que el router atendió cada petición (eventos `PETICION` de CloudWatch);
- regla: el nivel que predice src/histeresis.py simulando la corrida con los errores (status ≥ 500)
  que vio el propio k6. Se reutilizan `entrar`/`registrar`: el panel no tiene una copia de la regla.

Todo se agrupa por «minuto del k6» (bloques de 20 peticiones), que es la unidad de la v3, no por
minuto de reloj. Que las tres coincidan petición por petición es la prueba de que el panel no
inventa nada; la regla se puede verificar aun sin leer el servidor, solo con la salida del k6.

Supuestos: la corrida del k6 empieza fresca (el router emite `CORRIDA_NUEVA` o el estado ya estaba
vacío tras 15 s sin tráfico), así que la iteración i del k6 es la petición i del router; y no hubo
peticiones manuales mientras corría el k6.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from typing import Any, Iterable

import histeresis
from histeresis import ParamsHisteresis
from panel.k6 import TOTAL_ITERACIONES, Iteracion, error_del_script, secuencia

COLUMNAS = ("minuto_k6", "peticiones", "errores_cliente", "errores_servidor", "niveles_cliente",
            "niveles_servidor", "niveles_regla", "coincide", "coincide_regla")


def simular(errores: Iterable[bool], p: ParamsHisteresis = ParamsHisteresis()) -> list[int]:
    """Nivel con que la regla atiende cada petición, dada la secuencia de errores. Una petición cada
    3 s, como el k6, así que la inactividad nunca abre una corrida nueva."""
    estado, out = histeresis.EstadoHisteresis(), []
    for i, es_error in enumerate(errores):
        estado, _ = histeresis.entrar(estado, i * 3.0, p)
        out.append(estado.nivel)
        estado = histeresis.registrar(estado, es_error)
    return out


def guion(p: ParamsHisteresis, iteraciones: list[Iteracion]) -> list[dict[str, Any]]:
    """El plan del k6 oficial por minuto del k6: errores que pide, niveles que predice la regla y los
    que respondió el sistema. El minuto 7 tiene tres niveles (N3 → N2 → N1): las rachas se cumplen
    dentro del bloque, en las peticiones 126 y 136."""
    errores = [error_del_script(i) for i in range(TOTAL_ITERACIONES)]
    esperado = simular(errores, p)
    vistos: dict[int, list[int | None]] = {}
    for it in iteraciones:
        vistos.setdefault((it.iteracion - 1) // p.tamano + 1, []).append(it.nivel)
    out = []
    for m in range(1, TOTAL_ITERACIONES // p.tamano + 1):
        bloque = slice((m - 1) * p.tamano, m * p.tamano)
        niveles = vistos.get(m, [])
        out.append({"minuto": m, "errores": sum(errores[bloque]), "niveles_esperados": secuencia(esperado[bloque]),
                    "niveles_vistos": secuencia(niveles), "iteraciones": len(niveles)})
    return out


def corrida_servidor(eventos: list[dict[str, Any]], desde_ms: int | None = None) -> dict[int, dict[str, Any]]:
    """Eventos `PETICION` de UNA corrida del router, por número de petición.

    Una corrida nueva empieza cuando la numeración vuelve atrás. Con `desde_ms` (el arranque del k6)
    se toma la primera corrida que empieza después; si no, la última. Se respeta el orden recibido
    (CloudWatch ya los da por tiempo), así que no hace falta el campo `ts`.
    """
    corridas: list[list[dict[str, Any]]] = []
    for e in eventos:
        if e.get("evento") != "PETICION":
            continue
        if not corridas or e["peticion"] <= corridas[-1][-1]["peticion"]:
            corridas.append([])
        corridas[-1].append(e)
    if not corridas:
        return {}
    elegida = corridas[-1]
    if desde_ms is not None:
        elegida = next((c for c in corridas if c[0].get("ts", desde_ms) >= desde_ms), corridas[-1])
    return {e["peticion"]: e for e in elegida}


def coherencia(iteraciones: Iterable[Iteracion], peticiones: dict[int, dict[str, Any]],
               p: ParamsHisteresis = ParamsHisteresis()) -> list[dict[str, Any]]:
    cliente = {it.iteracion: it for it in iteraciones}
    orden = sorted(cliente)
    regla = dict(zip(orden, simular((cliente[i].status >= 500 for i in orden), p))) if orden == list(
        range(1, len(orden) + 1)) else {}  # con huecos en la numeración no se puede simular
    filas = []
    for m in sorted({(n - 1) // p.tamano + 1 for n in set(cliente) | set(peticiones)}):
        nums = range((m - 1) * p.tamano + 1, m * p.tamano + 1)
        detalle = []
        for n in nums:
            c, s = cliente.get(n), peticiones.get(n)
            if c is None and s is None:
                continue
            detalle.append({"peticion": n, "cliente": c.nivel if c else None, "servidor": s["nivel"] if s else None,
                            "regla": regla.get(n), "error_cliente": bool(c and c.status >= 500),
                            "error_servidor": bool(s and s["status"] >= 500)})
        con_ambos = [d for d in detalle if d["cliente"] is not None and d["servidor"] is not None]
        con_regla = [d for d in detalle if d["cliente"] is not None and d["regla"] is not None]
        filas.append({
            "minuto": m, "peticiones": f"{detalle[0]['peticion']}-{detalle[-1]['peticion']}",
            "peticiones_cliente": sum(1 for d in detalle if d["peticion"] in cliente),
            "peticiones_servidor": sum(1 for d in detalle if d["servidor"] is not None),
            "errores_cliente": sum(d["error_cliente"] for d in detalle),
            "errores_servidor": sum(d["error_servidor"] for d in detalle),
            "niveles_cliente": secuencia([d["cliente"] for d in detalle]),
            "niveles_servidor": secuencia([d["servidor"] for d in detalle]),
            "niveles_regla": secuencia([d["regla"] for d in detalle]),
            "coincide": all(d["cliente"] == d["servidor"] for d in con_ambos) if con_ambos else None,
            "coincide_regla": all(d["cliente"] == d["regla"] for d in con_regla) if con_regla else None,
            "detalle": detalle,
        })
    return filas


def resumen_coherencia(filas: list[dict[str, Any]]) -> dict[str, Any]:
    evaluables = [f for f in filas if f["coincide"] is not None]
    con_regla = [f for f in filas if f.get("coincide_regla") is not None]
    return {"minutos": len(evaluables), "coinciden": sum(1 for f in evaluables if f["coincide"]),
            "todo_coincide": bool(evaluables) and all(f["coincide"] for f in evaluables),
            "minutos_regla": len(con_regla), "coinciden_regla": sum(1 for f in con_regla if f["coincide_regla"]),
            "regla_se_cumple": bool(con_regla) and all(f["coincide_regla"] for f in con_regla)}


def _si_no(v: bool | None) -> str:
    return "" if v is None else ("si" if v else "NO")


def como_csv(filas: list[dict[str, Any]]) -> str:
    salida = io.StringIO()
    w = csv.writer(salida, lineterminator="\n")
    w.writerow(COLUMNAS)
    for f in filas:
        w.writerow((f["minuto"], f["peticiones"], f["errores_cliente"], f["errores_servidor"],
                    "-".join(map(str, f["niveles_cliente"])), "-".join(map(str, f["niveles_servidor"])),
                    "-".join(map(str, f["niveles_regla"])), _si_no(f["coincide"]), _si_no(f["coincide_regla"])))
    return salida.getvalue()


def como_jsonl(registros: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros)


def zip_evidencia(archivos: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in archivos.items():
            z.writestr(nombre, contenido)
    return buf.getvalue()
