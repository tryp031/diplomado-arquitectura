#!/usr/bin/env python3
"""
graficas.py — genera las figuras del informe en SVG, sin dependencias externas.

Por qué SVG a mano y no matplotlib: el harness es compartido por cuatro personas.
Una dependencia obliga a los cuatro a instalarla y a que coincidan las versiones, o las
figuras dejan de ser reproducibles. Con la librería estándar, cualquiera regenera las
figuras con `python3 graficas.py` y salen idénticas. SVG además es vectorial: se incrusta
en el PDF sin pixelarse.

Uso:
    ./graficas.py                      # agrega rondas 1-3 de cada variante en resultados/
    ./graficas.py --out ../docs/graficas/
"""
import argparse
import csv
import glob
import math
import os
import re
from collections import defaultdict

UMBRAL_NS = 1_000_000  # el objetivo del enunciado: 1 ms

ESTILO = {
    "tcp-python":           ("#2563eb", "TCP Python"),
    "C":  ("#16a34a", "C · Unix socket / UDP"),
    "A":  ("#a16207", "A · HTTP/REST"),
    "memoria-compartida-c": ("#7c3aed", "Memoria compartida C"),
}
ORDEN = ["tcp-python", "memoria-compartida-c"]
PERCENTILES = [0, 50, 90, 99, 99.9, 99.99, 99.999]


# Las rondas que sustentan el informe son 1, 2 y 3: 1 000 000 de iteraciones cada una,
# 3 000 000 por variante. Cualquier otra numeracion es exploratoria — la 0 son corridas
# de validacion y la 9 pruebas rapidas de 20 000 iteraciones— y NO entra en las figuras.
# Hasta el 17/09 este filtro solo excluia la ronda 0: la 9 se colaba y las figuras decian
# n=3 020 000 mientras la tabla del informe decia 3 000 000. No fallaba: mentia en silencio.
RONDAS_DEL_INFORME = (1, 2, 3)


def cargar(dir_res, rondas=RONDAS_DEL_INFORME):
    """Agrega las rondas del informe de cada variante. resultados-<VAR>-<RONDA>.csv"""
    series = defaultdict(list)
    for ruta in sorted(glob.glob(os.path.join(dir_res, "resultados-*.csv"))):
        m = re.match(r"resultados-([A-Za-z][A-Za-z0-9-]*)-(\d)\.csv$", os.path.basename(ruta))
        if not m:
            continue
        var, ronda = m.group(1), int(m.group(2))
        if ronda not in rondas:
            continue
        with open(ruta) as fh:
            lector = csv.DictReader(fh)
            # Por NOMBRE, nunca por posicion: el 15/09 se anadio la columna `hilo` al final
            # y analyze.py, que leia la ultima, empezo a reportar ceros sin dar error.
            if not lector.fieldnames or "latencia_ns" not in lector.fieldnames:
                raise SystemExit(
                    f"{ruta}: no tiene columna 'latencia_ns' (cabecera: {lector.fieldnames}).\n"
                    "El formato del CSV cambio: revisa el cliente antes de generar figuras."
                )
            series[var] += [int(fila["latencia_ns"]) for fila in lector]
    return {v: sorted(d) for v, d in series.items() if d}


def pct(d, q):
    return d[min(len(d) - 1, int(round(q / 100 * (len(d) - 1))))]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_ns(v):
    if v >= 1_000_000: return f"{v/1_000_000:g} ms"
    if v >= 1_000:     return f"{v/1_000:g} µs"
    return f"{v:g} ns"


class Lienzo:
    """SVG mínimo con ejes logarítmicos en Y."""

    def __init__(self, an, al, m, titulo, sub, ymin, ymax):
        self.an, self.al, self.m = an, al, m
        self.ymin, self.ymax = ymin, ymax
        self.p = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{an}" height="{al}" '
            f'viewBox="0 0 {an} {al}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
            f'<rect width="{an}" height="{al}" fill="#ffffff"/>',
            f'<text x="{m["l"]}" y="30" font-size="17" font-weight="600" fill="#111827">{esc(titulo)}</text>',
            f'<text x="{m["l"]}" y="50" font-size="12" fill="#6b7280">{esc(sub)}</text>',
        ]

    def y(self, v):
        v = max(v, self.ymin)
        t = (math.log10(v) - math.log10(self.ymin)) / (math.log10(self.ymax) - math.log10(self.ymin))
        return self.al - self.m["b"] - t * (self.al - self.m["t"] - self.m["b"])

    def eje_y(self, etiqueta):
        d = math.floor(math.log10(self.ymin))
        while 10 ** d <= self.ymax:
            v = 10 ** d
            if v >= self.ymin:
                yy = self.y(v)
                self.p.append(f'<line x1="{self.m["l"]}" y1="{yy:.1f}" x2="{self.an-self.m["r"]}" '
                              f'y2="{yy:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
                self.p.append(f'<text x="{self.m["l"]-8}" y="{yy+4:.1f}" font-size="11" '
                              f'fill="#6b7280" text-anchor="end">{fmt_ns(v)}</text>')
            d += 1
        self.p.append(f'<text x="16" y="{self.al/2:.0f}" font-size="12" fill="#374151" '
                      f'text-anchor="middle" transform="rotate(-90 16 {self.al/2:.0f})">{esc(etiqueta)}</text>')

    def umbral(self):
        if not (self.ymin <= UMBRAL_NS <= self.ymax):
            return
        yy = self.y(UMBRAL_NS)
        self.p.append(f'<line x1="{self.m["l"]}" y1="{yy:.1f}" x2="{self.an-self.m["r"]}" y2="{yy:.1f}" '
                      f'stroke="#dc2626" stroke-width="2" stroke-dasharray="7,4"/>')
        self.p.append(f'<text x="{self.m["l"]+8}" y="{yy-7:.1f}" font-size="12" font-weight="600" '
                      f'fill="#dc2626">objetivo del enunciado: 1 ms</text>')

    def leyenda(self, items, x, y):
        for i, (color, txt) in enumerate(items):
            yy = y + i * 19
            self.p.append(f'<rect x="{x}" y="{yy-9}" width="13" height="13" rx="2" fill="{color}"/>')
            self.p.append(f'<text x="{x+20}" y="{yy+2}" font-size="12" fill="#374151">{esc(txt)}</text>')

    def nota(self, txt, y):
        self.p.append(f'<text x="{self.m["l"]}" y="{y}" font-size="11" fill="#6b7280">{esc(txt)}</text>')

    def guardar(self, ruta):
        self.p.append("</svg>")
        with open(ruta, "w") as fh:
            fh.write("\n".join(self.p))
        print(f"  -> {ruta}")


def grafica_percentiles(series, salida):
    """Curva de percentiles. Es LA figura del informe: muestra la cola, que es donde
    se decide el cumplimiento. Eje X estirado hacia la cola (escala -log10(1-p))."""
    an, al, m = 940, 520, {"l": 90, "r": 75, "t": 70, "b": 70}
    vals = [pct(d, q) for d in series.values() for q in PERCENTILES] + \
           [max(d) for d in series.values()]
    ymin = max(10, min(v for v in vals if v > 0) / 2)
    ymax = max(vals) * 2

    c = Lienzo(an, al, m, "Latencia por percentil — dónde se decide el cumplimiento",
               "3 rondas × 1 000 000 por variante · RTT de aplicación (frontera F1, ADR-001) · escala logarítmica",
               ymin, ymax)
    c.eje_y("latencia (escala log)")

    # eje X: posiciones equiespaciadas por percentil + "máx" al final
    etiquetas = ["mín", "p50", "p90", "p99", "p99.9", "p99.99", "p99.999", "máx"]
    n = len(etiquetas)
    ancho = an - m["l"] - m["r"]
    xs = [m["l"] + ancho * i / (n - 1) for i in range(n)]
    for x, et in zip(xs, etiquetas):
        c.p.append(f'<line x1="{x:.1f}" y1="{m["t"]}" x2="{x:.1f}" y2="{al-m["b"]}" '
                   f'stroke="#f3f4f6" stroke-width="1"/>')
        c.p.append(f'<text x="{x:.1f}" y="{al-m["b"]+20}" font-size="11" fill="#6b7280" '
                   f'text-anchor="middle">{et}</text>')

    c.umbral()

    leyenda = []
    for var in ORDEN:
        if var not in series:
            continue
        d = series[var]
        color, nombre = ESTILO[var]
        ys = [pct(d, q) for q in PERCENTILES] + [d[-1]]
        pts = " ".join(f"{x:.1f},{c.y(v):.1f}" for x, v in zip(xs, ys))
        c.p.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" '
                   f'stroke-linejoin="round"/>')
        for x, v in zip(xs, ys):
            c.p.append(f'<circle cx="{x:.1f}" cy="{c.y(v):.1f}" r="3.5" fill="{color}"/>')
        sobre = sum(1 for v in d if v > UMBRAL_NS)
        leyenda.append((color, f"{nombre} — {sobre} muestras > 1 ms" if sobre
                        else f"{nombre} — ninguna > 1 ms"))
    c.leyenda(leyenda, m["l"] + 12, m["t"] + 12)
    c.nota("Las curvas son planas hasta el p99 y se disparan después: por la mediana todas cumplen; "
           "la diferencia está en la cola.", al - 18)
    c.guardar(salida)


def grafica_histograma(series, salida):
    """Distribución por décadas logarítmicas. Hace visible la cuantización de la variante D."""
    an, al, m = 940, 470, {"l": 90, "r": 75, "t": 70, "b": 70}
    todos = [v for d in series.values() for v in d if v > 0]
    lo, hi = math.log10(min(todos)), math.log10(max(todos))
    n_cubos = int((hi - lo) * 8) + 1
    bordes = [10 ** (lo + i * (hi - lo) / n_cubos) for i in range(n_cubos + 1)]

    conteos = {}
    for var, d in series.items():
        h = [0] * n_cubos
        for v in d:
            if v <= 0:
                continue
            i = min(n_cubos - 1, int((math.log10(v) - lo) / (hi - lo) * n_cubos))
            h[i] += 1
        conteos[var] = [100.0 * x / len(d) for x in h]

    ymax = max(max(h) for h in conteos.values()) * 1.15
    c = Lienzo(an, al, m, "Distribución de la latencia — dónde cae cada arquitectura",
               "porcentaje de muestras por cubo logarítmico · 3 000 000 de muestras por variante",
               0.001, 100)
    # eje Y lineal en porcentaje (sobrescribe el log del lienzo)
    c.y = lambda v, _al=al, _m=m, _ymax=ymax: _al - _m["b"] - (min(v, _ymax) / _ymax) * (_al - _m["t"] - _m["b"])
    for frac in range(0, 6):
        v = ymax * frac / 5
        yy = c.y(v)
        c.p.append(f'<line x1="{m["l"]}" y1="{yy:.1f}" x2="{an-m["r"]}" y2="{yy:.1f}" stroke="#e5e7eb"/>')
        c.p.append(f'<text x="{m["l"]-8}" y="{yy+4:.1f}" font-size="11" fill="#6b7280" '
                   f'text-anchor="end">{v:.0f}%</text>')

    ancho = an - m["l"] - m["r"]
    def x_de(v):
        return m["l"] + (math.log10(v) - lo) / (hi - lo) * ancho

    for d in range(int(math.floor(lo)), int(math.ceil(hi)) + 1):
        v = 10 ** d
        if not (10 ** lo <= v <= 10 ** hi):
            continue
        x = x_de(v)
        c.p.append(f'<line x1="{x:.1f}" y1="{m["t"]}" x2="{x:.1f}" y2="{al-m["b"]}" stroke="#f3f4f6"/>')
        c.p.append(f'<text x="{x:.1f}" y="{al-m["b"]+20}" font-size="11" fill="#6b7280" '
                   f'text-anchor="middle">{fmt_ns(v)}</text>')

    if 10 ** lo <= UMBRAL_NS <= 10 ** hi:
        x = x_de(UMBRAL_NS)
        c.p.append(f'<line x1="{x:.1f}" y1="{m["t"]}" x2="{x:.1f}" y2="{al-m["b"]}" stroke="#dc2626" '
                   f'stroke-width="2" stroke-dasharray="7,4"/>')
        c.p.append(f'<text x="{x-6:.1f}" y="{m["t"]+14}" font-size="12" font-weight="600" '
                   f'fill="#dc2626" text-anchor="end">1 ms</text>')

    leyenda = []
    for var in ORDEN:
        if var not in conteos:
            continue
        color, nombre = ESTILO[var]
        pts = []
        for i, p in enumerate(conteos[var]):
            x0, x1 = x_de(bordes[i]), x_de(bordes[i + 1])
            pts += [f"{x0:.1f},{c.y(p):.1f}", f"{x1:.1f},{c.y(p):.1f}"]
        c.p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2"/>')
        leyenda.append((color, nombre))
    c.leyenda(leyenda, m["l"] + 185, m["t"] + 12)  # zona vacía entre los dos picos
    c.nota("La variante D no forma una campana sino dos picos: son los tics del reloj "
           "(41,67 ns). El instrumento es visible en el resultado.", al - 18)
    c.guardar(salida)


def main():
    aqui = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--resultados", default=os.path.join(aqui, "resultados"))
    # Las figuras son PRODUCTO del analisis, no parte del sistema: viven en docs/ y
    # por eso no viajan en el ZIP del codigo fuente (nota 7 del 21/09, ADR-010).
    ap.add_argument("--out", default=os.path.join(os.path.dirname(aqui), "docs", "graficas"))
    a = ap.parse_args()

    series = cargar(a.resultados)
    if not series:
        raise SystemExit(f"no hay CSV en {a.resultados}")
    os.makedirs(a.out, exist_ok=True)
    print("series:", ", ".join(f"{v} (n={len(d):,})" for v, d in series.items()))
    grafica_percentiles(series, os.path.join(a.out, "percentiles.svg"))
    grafica_histograma(series, os.path.join(a.out, "histograma.svg"))


if __name__ == "__main__":
    main()
