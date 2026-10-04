#!/usr/bin/env python3
"""Genera las gráficas SVG del cuaderno de estudio del Módulo 2.

Las gráficas son MODELOS de cálculo, no mediciones: ilustran dos cuentas que el
reto exige saber hacer (token bucket del API Gateway y ley de Little). Cuando
haya mediciones reales del Reto 2, van en otra gráfica, marcada como dato medido.

Sin dependencias externas — solo biblioteca estándar.

Uso:
    python3 "Modulo 2/Aportes/danny/graficas/generar_graficas.py"

Escribe token-bucket.svg y ley-little.svg junto a este script. Los SVG llevan su
propio <style> con modo claro y oscuro, así se ven bien en GitHub (como imagen) y
dentro del HTML generado (consolidar_html.py los inserta en línea).
"""
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent

# --- Datos del enunciado (Actividad-Reto2.md) -------------------------------------
PETICIONES = 1000          # iteraciones del k6
LLEGADAS = 35.69           # req/s de la salida de k6 de referencia
RATE = 15                  # req/s del stage prod del API Gateway
LIMITE_INSTANCIAS = 10
DURACION_K6_REF = 0.176    # s, promedio de la salida de k6 de referencia

W, H = 640, 340
M_IZQ, M_DER, M_SUP, M_INF = 64, 150, 40, 52   # margen derecho: etiquetas directas
AW, AH = W - M_IZQ - M_DER, H - M_SUP - M_INF

# Paleta validada con dataviz/validate_palette.js (claro y oscuro: ALL PASS).
ESTILO = """
.v{--sf:#FFFFFF;--t1:#0E2226;--t2:#3F5A61;--t3:#6E868C;--grid:#E1E9EA;--ax:#CDDADC;
  --s1:#2a78d6;--s2:#eb6834;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
@media (prefers-color-scheme:dark){.v{--sf:#101F22;--t1:#E3EBEC;--t2:#A5B9BE;--t3:#7C9399;
  --grid:#1A2E32;--ax:#233A3F;--s1:#3987e5;--s2:#d95926}}
.v .bg{fill:var(--sf)}
.v .grid{stroke:var(--grid);stroke-width:1}
.v .ax{stroke:var(--ax);stroke-width:1}
.v .tick{fill:var(--t3);font-size:11px}
.v .lab{fill:var(--t2);font-size:12px}
.v .ttl{fill:var(--t1);font-size:13px;font-weight:600}
.v .note{fill:var(--t2);font-size:11.5px}
.v .ref{stroke:var(--t3);stroke-width:1}
.v .l1{fill:none;stroke:var(--s1);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.v .l2{fill:none;stroke:var(--s2);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.v .d1{fill:var(--s1);stroke:var(--sf);stroke-width:2}
.v .d2{fill:var(--s2);stroke:var(--sf);stroke-width:2}
.v .hit{fill:transparent}
"""


def num(x, dec=0):
    """Número con coma decimal y punto de miles, como en el resto del cuaderno."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


class Lienzo:
    def __init__(self, uid, titulo, desc, xmax, ymax):
        # uid: los dos SVG van en línea en la misma página; sus id no pueden chocar.
        self.xmax, self.ymax = xmax, ymax
        self.partes = [
            f'<svg xmlns="http://www.w3.org/2000/svg" class="v" viewBox="0 0 {W} {H}" '
            f'role="img" aria-labelledby="{uid}-t {uid}-d" style="max-width:100%;height:auto">',
            f'<title id="{uid}-t">{titulo}</title><desc id="{uid}-d">{desc}</desc>',
            f"<style>{ESTILO}</style>",
            f'<rect class="bg" width="{W}" height="{H}" rx="3"/>',
        ]

    def x(self, v):
        return M_IZQ + v / self.xmax * AW

    def y(self, v):
        return M_SUP + AH - v / self.ymax * AH

    def ejes(self, xticks, yticks, xfmt, yfmt, xlab, ylab):
        p = self.partes
        for t in yticks:
            p.append(f'<line class="grid" x1="{M_IZQ}" x2="{M_IZQ + AW}" y1="{self.y(t):.1f}" y2="{self.y(t):.1f}"/>')
            p.append(f'<text class="tick" x="{M_IZQ - 8}" y="{self.y(t) + 4:.1f}" text-anchor="end">{yfmt(t)}</text>')
        for t in xticks:
            p.append(f'<text class="tick" x="{self.x(t):.1f}" y="{M_SUP + AH + 18}" text-anchor="middle">{xfmt(t)}</text>')
        p.append(f'<line class="ax" x1="{M_IZQ}" x2="{M_IZQ + AW}" y1="{M_SUP + AH}" y2="{M_SUP + AH}"/>')
        p.append(f'<text class="lab" x="{M_IZQ + AW / 2}" y="{H - 10}" text-anchor="middle">{xlab}</text>')
        p.append(f'<text class="lab" x="8" y="{M_SUP - 14}">{ylab}</text>')

    def linea(self, pts, clase):
        d = " ".join(f"{'M' if i == 0 else 'L'}{self.x(a):.1f},{self.y(b):.1f}" for i, (a, b) in enumerate(pts))
        self.partes.append(f'<path class="{clase}" d="{d}"/>')

    def punto(self, a, b, clase, tooltip):
        # El <title> da el tooltip nativo; el círculo transparente agranda el blanco del hover.
        cx, cy = self.x(a), self.y(b)
        self.partes.append(
            f'<g><title>{tooltip}</title><circle class="hit" cx="{cx:.1f}" cy="{cy:.1f}" r="12"/>'
            f'<circle class="{clase}" cx="{cx:.1f}" cy="{cy:.1f}" r="5"/></g>')

    def texto(self, a, b, txt, clase="note", ancla="start", dx=0, dy=0):
        self.partes.append(f'<text class="{clase}" x="{self.x(a) + dx:.1f}" y="{self.y(b) + dy:.1f}" '
                           f'text-anchor="{ancla}">{txt}</text>')

    def guardar(self, nombre):
        (AQUI / nombre).write_text("\n".join(self.partes + ["</svg>"]) + "\n", encoding="utf-8")


def fichas(burst, t):
    """Fichas que quedan en el cubo a los t segundos (modelo de flujo continuo)."""
    return max(0.0, burst - (LLEGADAS - RATE) * t)


def token_bucket():
    dur = PETICIONES / LLEGADAS
    burst_min = PETICIONES - RATE * dur
    c = Lienzo(
        "tb", "Token bucket del API Gateway durante la prueba k6",
        f"Fichas disponibles en el cubo con {num(LLEGADAS, 1)} req/s de llegada y rate {RATE}. "
        f"Con burst 2000 el cubo nunca se vacía. Con burst 500 se vacía a los "
        f"{num(500 / (LLEGADAS - RATE), 1)} s y desde ahí las peticiones sobrantes reciben 429. "
        f"El burst mínimo para 1000 peticiones es {num(burst_min)}.",
        xmax=30, ymax=2000)
    c.ejes(range(0, 31, 5), range(0, 2001, 500), lambda t: f"{t} s", lambda v: num(v),
           "segundos desde el inicio del k6", "fichas en el cubo")

    pasos = [i * dur / 100 for i in range(101)]
    c.linea([(t, fichas(2000, t)) for t in pasos], "l1")
    c.linea([(t, fichas(500, t)) for t in pasos], "l2")

    # Referencia: el burst mínimo que deja pasar las 1000 peticiones.
    yb = c.y(burst_min)
    c.partes.append(f'<line class="ref" x1="{M_IZQ}" x2="{M_IZQ + AW}" y1="{yb:.1f}" y2="{yb:.1f}"/>')
    c.texto(0.4, burst_min, f"burst mínimo ≈ {num(burst_min)}", dy=-6)

    vacio = 500 / (LLEGADAS - RATE)
    rechazos = (LLEGADAS - RATE) * (dur - vacio)
    c.punto(vacio, 0, "d2", f"Burst 500: cubo vacío a los {num(vacio, 1)} s; ≈ {num(rechazos)} peticiones con 429")
    c.texto(vacio, 0, f"vacío a los {num(vacio, 1)} s;", dx=4, dy=-30)
    c.texto(vacio, 0, f"después ≈ {num(rechazos)} respuestas 429", dx=4, dy=-14)

    fin2000 = fichas(2000, dur)
    c.punto(dur, fin2000, "d1", f"Burst 2000: quedan {num(fin2000)} fichas al terminar ({num(dur, 1)} s)")
    # Etiquetas directas al final de cada línea + leyenda (dos series).
    c.texto(dur, fin2000, "burst 2000", dx=12, dy=4, clase="lab")
    c.texto(dur, fin2000, f"quedan {num(fin2000)}", dx=12, dy=20)
    c.texto(dur, 0, "burst 500", dx=12, dy=4, clase="lab")
    ly = M_SUP + 4
    c.partes.append(
        f'<g transform="translate({M_IZQ + AW + 20},{ly + 120})">'
        f'<line class="l1" x1="0" x2="18" y1="0" y2="0"/><text class="tick" x="24" y="4">burst 2000</text>'
        f'<line class="l2" x1="0" x2="18" y1="18" y2="18"/><text class="tick" x="24" y="22">burst 500</text></g>')
    c.guardar("token-bucket.svg")
    return dur, burst_min, vacio, rechazos


def ley_little():
    c = Lienzo(
        "ll", "Ley de Little: instancias simultáneas según la duración de cada petición",
        f"Con {num(LLEGADAS, 1)} req/s, la concurrencia es llegadas por duración. El límite de "
        f"{LIMITE_INSTANCIAS} instancias se cruza a los {num(LIMITE_INSTANCIAS / LLEGADAS, 2)} s por petición.",
        xmax=0.8, ymax=30)
    c.ejes([0, 0.2, 0.4, 0.6, 0.8], range(0, 31, 10), lambda t: f"{num(t, 1)} s", lambda v: num(v),
           "duración de cada petición", "instancias simultáneas")
    c.linea([(0, 0), (0.8, LLEGADAS * 0.8)], "l1")

    yl = c.y(LIMITE_INSTANCIAS)
    c.partes.append(f'<line class="ref" x1="{M_IZQ}" x2="{M_IZQ + AW}" y1="{yl:.1f}" y2="{yl:.1f}"/>')
    c.texto(0.8, LIMITE_INSTANCIAS, f"límite: {LIMITE_INSTANCIAS} instancias", dx=8, dy=4, clase="lab")

    corte = LIMITE_INSTANCIAS / LLEGADAS
    casos = [
        (DURACION_K6_REF, "k6 de referencia", "d1"),
        (corte, "corte", "d1"),
        (0.5, "si el handler espera el correo", "d2"),
    ]
    for d, nombre, clase in casos:
        conc = LLEGADAS * d
        c.punto(d, conc, clase, f"{nombre}: {num(d, 3)} s × {num(LLEGADAS, 1)} req/s ≈ {num(conc, 1)} instancias")
    c.texto(DURACION_K6_REF, LLEGADAS * DURACION_K6_REF, f"0,176 s → {num(LLEGADAS * DURACION_K6_REF, 1)}",
            dx=10, dy=16)
    c.texto(corte, LIMITE_INSTANCIAS, f"{num(corte, 2)} s", dx=-10, dy=-10, ancla="end")
    c.texto(0.5, LLEGADAS * 0.5, f"0,5 s → {num(LLEGADAS * 0.5, 1)} (no alcanza)", dx=10, dy=16)
    c.texto(0.8, LLEGADAS * 0.8, f"{num(LLEGADAS, 1)} req/s", dx=8, dy=4, clase="lab")
    c.guardar("ley-little.svg")
    return corte


if __name__ == "__main__":
    dur, burst_min, vacio, rechazos = token_bucket()
    corte = ley_little()
    print(f"token-bucket.svg  duración {dur:.2f} s · burst mínimo {burst_min:.0f} · "
          f"burst 500 se vacía a {vacio:.2f} s · ≈{rechazos:.0f} rechazos")
    print(f"ley-little.svg    corte del límite a {corte:.3f} s por petición")
