#!/usr/bin/env python3
"""
Análisis compartido de latencias — Reto de Latencia Mínima.

Único script que calcula métricas: todas las variantes producen CSV crudo y este
script los interpreta, así los resultados son comparables por construcción.

Uso:
    ./analyze.py resultados/*.csv
    ./analyze.py --histograma resultados/resultados-tcp-python-1.csv
    ./analyze.py --md resultados/*.csv

Percentiles por rango más cercano (nearest-rank), sin interpolación: devuelve
siempre una muestra observada, nunca un valor inventado.
"""

import argparse
import csv
import math
import statistics
import sys
from pathlib import Path

# Percentiles que se reportan en todas las variantes.
PERCENTILES = [50.0, 90.0, 99.0, 99.9, 99.99]


def leer_csv(ruta: Path) -> list[int]:
    """Lee un CSV de muestras y devuelve las latencias en ns.

    La columna se localiza POR NOMBRE, no por posición: leer la última columna daría
    el número de hilo (0) y un análisis de puros ceros sin ningún error. Un CSV cuyo
    formato no se reconoce detiene el análisis en vez de producir un número falso.
    """
    muestras: list[int] = []
    with ruta.open(newline="") as fh:
        lector = csv.reader(fh)
        cabecera = next(lector, None)
        if cabecera is None:
            raise SystemExit(f"error: {ruta} esta vacio")

        hay_cabecera = not cabecera[0].strip().lstrip("-").isdigit()
        if hay_cabecera:
            nombres = [c.strip().lower() for c in cabecera]
            if "latencia_ns" not in nombres:
                raise SystemExit(
                    f"error: {ruta} tiene cabecera pero no una columna 'latencia_ns'.\n"
                    f"       columnas encontradas: {', '.join(nombres)}")
            col = nombres.index("latencia_ns")
        else:
            # Sin cabecera: el formato historico es `iteracion,latencia_ns`.
            col = 1 if len(cabecera) >= 2 else 0
            muestras.append(int(cabecera[col]))

        for n, fila in enumerate(lector, start=2):
            if not fila:
                continue
            if len(fila) <= col:
                raise SystemExit(f"error: {ruta}:{n} tiene {len(fila)} columnas, "
                                 f"se esperaba la latencia en la {col + 1}")
            muestras.append(int(fila[col]))

    if not muestras:
        raise SystemExit(f"error: {ruta} no contiene muestras")
    return muestras


def percentil(ordenadas: list[int], p: float) -> int:
    """Percentil por rango más cercano. ordenadas debe venir ya ordenada."""
    n = len(ordenadas)
    rango = math.ceil(p / 100.0 * n)
    return ordenadas[max(0, min(n - 1, rango - 1))]


def resumir(ruta: Path) -> dict:
    muestras = leer_csv(ruta)
    ordenadas = sorted(muestras)
    r = {
        "nombre": ruta.stem,
        "n": len(ordenadas),
        "min": ordenadas[0],
        "max": ordenadas[-1],
        "media": statistics.fmean(ordenadas),
        "desv": statistics.pstdev(ordenadas) if len(ordenadas) > 1 else 0.0,
        "muestras": ordenadas,
    }
    for p in PERCENTILES:
        r[f"p{p}"] = percentil(ordenadas, p)
    return r


def us(ns: float) -> str:
    """Formatea ns como microsegundos con 2 decimales."""
    return f"{ns / 1000.0:,.2f}"


def cumple_1ms(r: dict) -> str:
    """El umbral del enunciado es < 1 ms. Se evalúa contra p99.9, no contra la media."""
    return "SÍ" if r["p99.9"] < 1_000_000 else "NO"


def imprimir_detalle(r: dict) -> None:
    print(f"\n=== {r['nombre']} ===")
    print(f"  n              {r['n']:,}")
    print(f"  mín            {us(r['min']):>12} µs")
    print(f"  p50            {us(r['p50.0']):>12} µs")
    print(f"  p90            {us(r['p90.0']):>12} µs")
    print(f"  p99            {us(r['p99.0']):>12} µs")
    print(f"  p99.9          {us(r['p99.9']):>12} µs")
    print(f"  p99.99         {us(r['p99.99']):>12} µs")
    print(f"  máx            {us(r['max']):>12} µs")
    print(f"  desv. est.     {us(r['desv']):>12} µs")
    print(f"  media          {us(r['media']):>12} µs   <- NO usar como métrica principal")
    print(f"  ¿p99.9 < 1 ms? {cumple_1ms(r):>12}")


def imprimir_histograma(r: dict, ancho: int = 56) -> None:
    """
    Histograma con cubos logarítmicos (10 por década, razón ~1.26x).
    Escala log porque las latencias abarcan varios órdenes de magnitud;
    un histograma lineal aplastaría toda la distribución en el primer cubo.
    """
    cubos: dict[int, int] = {}
    for v in r["muestras"]:
        if v <= 0:
            v = 1
        idx = int(math.floor(math.log10(v) * 10))
        cubos[idx] = cubos.get(idx, 0) + 1
    if not cubos:
        return
    pico = max(cubos.values())
    print(f"\n  histograma (log, 10 cubos/década) — {r['nombre']}")
    for idx in range(min(cubos), max(cubos) + 1):
        cuenta = cubos.get(idx, 0)
        lo = 10 ** (idx / 10.0)
        barra = "#" * int(round(cuenta / pico * ancho)) if cuenta else ""
        pct = cuenta / r["n"] * 100
        print(f"    {lo / 1000.0:9.3f} µs | {barra:<{ancho}} {cuenta:>9,} ({pct:5.2f}%)")


def imprimir_tabla_md(resumenes: list[dict]) -> None:
    print("\n| Variante | n | mín | p50 | p90 | p99 | p99.9 | p99.99 | máx | p99.9 < 1 ms |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|")
    for r in resumenes:
        print(
            f"| {r['nombre']} | {r['n']:,} | {us(r['min'])} | {us(r['p50.0'])} | "
            f"{us(r['p90.0'])} | {us(r['p99.0'])} | {us(r['p99.9'])} | "
            f"{us(r['p99.99'])} | {us(r['max'])} | {cumple_1ms(r)} |"
        )
    print("\nTodos los valores en microsegundos (µs). 1 ms = 1.000 µs.")
    print("El umbral del enunciado se evalúa contra **p99.9**, no contra la media.")


# Guarda de comparabilidad: corridas de máquinas distintas no se mezclan en una
# tabla, porque la diferencia incluiría la diferencia entre computadoras y se leería
# como diferencia entre arquitecturas. La plataforma se lee del .log hermano que
# escribe run.sh, sin cambiar el formato del CSV.
def plataforma_de(ruta: Path) -> str:
    """Identidad de la maquina donde se tomo esta corrida, o 'desconocida'."""
    log = ruta.parent / ruta.name.replace("resultados-", "ejecucion-").replace(".csv", ".log")
    if not log.exists():
        return "desconocida"
    sistema = cpu = ""
    for linea in log.read_text(errors="ignore").splitlines()[:12]:
        if linea.startswith("host:"):
            partes = linea.split()
            if len(partes) >= 2:
                sistema = partes[1]                       # Darwin | Linux
            if partes and partes[-1] in ("arm64", "x86_64", "aarch64"):
                sistema += "/" + partes[-1]
        elif linea.startswith("cpu:"):
            cpu = linea.split(":", 1)[1].strip()[:40]
    return f"{sistema} · {cpu}".strip(" ·") or "desconocida"


def main() -> None:
    ap = argparse.ArgumentParser(description="Análisis de latencias del reto M1")
    ap.add_argument("csv", nargs="+", type=Path, help="uno o más CSV de muestras crudas")
    ap.add_argument("--histograma", action="store_true", help="imprime histograma logarítmico")
    ap.add_argument("--md", action="store_true", help="solo la tabla comparativa en Markdown")
    ap.add_argument("--mezclar-plataformas", action="store_true",
                    help="comparar corridas de maquinas distintas (normalmente NO se debe)")
    args = ap.parse_args()

    # Guarda de comparabilidad.
    plataformas: dict[str, list[str]] = {}
    for ruta in args.csv:
        plataformas.setdefault(plataforma_de(ruta), []).append(ruta.name)
    if len(plataformas) > 1 and not args.mezclar_plataformas:
        print("\nERROR: estas comparando corridas tomadas en maquinas distintas.\n", file=sys.stderr)
        for plat, archivos in plataformas.items():
            print(f"  {plat}", file=sys.stderr)
            for a in sorted(archivos):
                print(f"      {a}", file=sys.stderr)
        print("\n  La diferencia entre estos numeros incluye la diferencia entre las dos\n"
              "  maquinas, no solo entre las dos arquitecturas. Una tabla asi dice algo\n"
              "  distinto de lo que parece decir.\n\n"
              "  Lo correcto: una tabla por plataforma, cada una con su equipo declarado.\n"
              "  Si aun asi necesitas la mezcla, pedila explicitamente con\n"
              "  --mezclar-plataformas y declara junto a la tabla que las mezcla.\n",
              file=sys.stderr)
        raise SystemExit(2)
    if len(plataformas) == 1 and "desconocida" not in plataformas:
        print(f"plataforma: {next(iter(plataformas))}")

    resumenes = [resumir(p) for p in args.csv]
    resumenes.sort(key=lambda r: r["p50.0"])

    if not args.md:
        for r in resumenes:
            imprimir_detalle(r)
            if args.histograma:
                imprimir_histograma(r)

    if len(resumenes) > 1 or args.md:
        imprimir_tabla_md(resumenes)


if __name__ == "__main__":
    sys.exit(main())
