#!/usr/bin/env python3
"""
generar-datos.py — condensa los CSV crudos de resultados/ en un JSON para el visor.

No mide nada: lee lo que el harness ya midió. El visor es un instrumento de lectura;
un navegador añade milisegundos y sus números serían del navegador, no del sistema.

Uso:  python3 visor/generar-datos.py > visor/datos.js
"""
import csv
import json
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RES = AQUI.parent / "resultados"

# Binning logarítmico COMPARTIDO por todas las variantes: sin un eje común no hay
# comparación posible entre distribuciones.
DEC_INI, DEC_FIN, POR_DEC = 1, 8, 12          # de 10^1 ns (10 ns) a 10^8 ns (100 ms)
N_BINS = (DEC_FIN - DEC_INI) * POR_DEC

def bin_de(ns: int) -> int:
    if ns <= 0:
        return 0
    b = int((math.log10(ns) - DEC_INI) * POR_DEC)
    return max(0, min(N_BINS - 1, b))

def pct(ordenados, p):
    if not ordenados:
        return 0
    i = min(len(ordenados) - 1, int(len(ordenados) * p / 100.0))
    return ordenados[i]

VARIANTES = {
    "memoria-compartida-c":  {"nombre": "Memoria compartida C",  "detalle": "C11 · espera activa · cero llamadas al sistema", "lenguaje": "C"},
    "tcp-python":  {"nombre": "TCP Python", "detalle": "TCP_NODELAY · conexión persistente",             "lenguaje": "Python"},
}

def cargar(patron):
    muestras = []
    for f in sorted(RES.glob(patron)):
        with f.open() as fh:
            r = csv.reader(fh)
            next(r, None)
            for fila in r:
                if len(fila) >= 2:
                    try:
                        muestras.append(int(fila[1]))
                    except ValueError:
                        pass
    return muestras

salida = {"bins": {"decIni": DEC_INI, "porDec": POR_DEC, "n": N_BINS}, "variantes": []}

for clave, meta in VARIANTES.items():
    patron = f"resultados-{clave}-[123].csv"
    m = cargar(patron)
    if not m:
        print(f"  aviso: sin datos para {clave}", file=sys.stderr)
        continue
    m.sort()
    n = len(m)
    media = sum(m) / n
    var = sum((x - media) ** 2 for x in m) / n

    hist = [0] * N_BINS
    for x in m:
        hist[bin_de(x)] += 1

    salida["variantes"].append({
        "id": clave, **meta, "n": n,
        "min": m[0],
        "p50": pct(m, 50), "p75": pct(m, 75), "p90": pct(m, 90),
        "p99": pct(m, 99), "p999": pct(m, 99.9), "p9999": pct(m, 99.99),
        "max": m[-1],
        "media": round(media, 1),
        "desv": round(math.sqrt(var), 1),
        "sobre1ms": sum(1 for x in m if x > 1_000_000),
        "hist": hist,
    })
    print(f"  {clave}: {n:,} muestras · p50={pct(m,50):,} ns · max={m[-1]:,} ns", file=sys.stderr)

print("window.DATOS = " + json.dumps(salida, ensure_ascii=False, separators=(",", ":")) + ";")
