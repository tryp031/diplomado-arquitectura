#!/usr/bin/env python3
"""
informe-a-pdf.py — genera el PDF del entregable a partir de INFORME.md.

Sin dependencias externas, por la misma razón que graficas.py: el harness lo comparten
cuatro personas y una dependencia obliga a los cuatro a instalarla. Lleva un conversor
Markdown mínimo (solo lo que el informe usa) y renderiza con Chrome en modo headless,
que ya está en la máquina y respeta el SVG como vectorial.

Uso:  python3 informe-a-pdf.py [--md INFORME.md] [--pdf INFORME.pdf]
"""
import argparse
import html
import os
import re
import subprocess
import sys
import tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 17mm 15mm 16mm 15mm; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       font-size: 10pt; line-height: 1.5; color: #111827; margin: 0; }
h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 4pt; color: #0f172a; }
h2 { font-size: 13.5pt; margin: 20pt 0 7pt; padding-bottom: 3pt;
     border-bottom: 1.5px solid #cbd5e1; color: #0f172a; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 14pt 0 5pt; color: #1e293b; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 11pt 0 4pt; color: #334155; break-after: avoid; }
p  { margin: 0 0 7pt; }
ul, ol { margin: 0 0 8pt; padding-left: 17pt; }
li { margin-bottom: 2.5pt; }
strong { font-weight: 650; color: #0f172a; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8.8pt;
       background: #f1f5f9; padding: 1px 4px; border-radius: 3px; color: #0f172a; }
pre { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #94a3b8;
      border-radius: 4px; padding: 8pt 10pt; overflow-x: auto; break-inside: avoid;
      margin: 0 0 9pt; }
pre code { background: none; padding: 0; font-size: 8.2pt; line-height: 1.42; }
blockquote { margin: 0 0 9pt; padding: 7pt 11pt; background: #f8fafc;
             border-left: 3px solid #64748b; border-radius: 0 4px 4px 0;
             color: #334155; break-inside: avoid; }
blockquote p:last-child { margin-bottom: 0; }
table { border-collapse: collapse; width: 100%; margin: 0 0 10pt;
        font-size: 8.8pt; break-inside: avoid; }
th { background: #f1f5f9; text-align: left; font-weight: 650; color: #0f172a; }
th, td { border: 1px solid #dbe1e8; padding: 4pt 6pt; vertical-align: top; }
tbody tr:nth-child(even) { background: #fafbfc; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 16pt 0; }
a { color: #1d4ed8; text-decoration: none; }
figure { margin: 10pt 0 14pt; break-inside: avoid; }
figure svg { width: 100%; height: auto; display: block;
             border: 1px solid #e2e8f0; border-radius: 5px; }
figcaption { font-size: 8.5pt; color: #64748b; margin-top: 4pt; text-align: center; }
.ok   { color: #15803d; font-weight: 700; }
.no   { color: #b91c1c; font-weight: 700; }
.av   { color: #b45309; font-weight: 700; }
.pend { color: #64748b; font-style: italic; font-size: 8.2pt;
        border: 1px solid #cbd5e1; border-radius: 3px; padding: 0 4px; }
body > p:first-of-type { color: #475569; font-size: 9.5pt; line-height: 1.55; }
"""


# ---------------------------------------------------------------- inline
# Los emoji de estado dependen de que la fuente de emoji esté disponible al renderizar.
# En un PDF formal, además, la tipografía normal se lee mejor que un pictograma de color.
# Se sustituyen en la CAPA DE PRESENTACIÓN: el .md conserva los emoji, que ahí sí se leen bien.
GLIFOS = {
    "✅": '<span class="ok">&#10003;</span>',
    "❌": '<span class="no">&#10007;</span>',
    "⚠️": '<span class="av">&#9888;</span>',
    "⚠": '<span class="av">&#9888;</span>',
    "⬜": '<span class="pend">pendiente</span>',
    "🟡": '<span class="av">parcial</span>',
    "👇": "", "👋": "", "📌": "", "1️⃣": "1.", "2️⃣": "2.", "3️⃣": "3.",
}


def inline(t):
    for k, v in GLIFOS.items():
        t = t.replace(k, "\x01" + str(list(GLIFOS).index(k)) + "\x01")
    t = html.escape(t, quote=False)
    t = re.sub(r"\x01(\d+)\x01", lambda m: list(GLIFOS.values())[int(m.group(1))], t)
    trozos = []

    def guardar(m):                       # el código va literal, sin más formato encima
        trozos.append(m.group(1))
        return f"\x00{len(trozos)-1}\x00"

    t = re.sub(r"`([^`]+)`", guardar, t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{trozos[int(m.group(1))]}</code>", t)
    return t


def es_sep_tabla(l):
    return bool(re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", l)) and "-" in l


def celdas(l):
    l = l.strip()
    if l.startswith("|"): l = l[1:]
    if l.endswith("|"):   l = l[:-1]
    return [c.strip() for c in l.split("|")]


# ---------------------------------------------------------------- bloques
def convertir(md):
    lineas = md.split("\n")
    out, i, n = [], 0, len(lineas)

    while i < n:
        l = lineas[i]

        # bloque de código
        if l.lstrip().startswith("```"):
            i += 1
            buf = []
            while i < n and not lineas[i].lstrip().startswith("```"):
                buf.append(lineas[i]); i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue

        # tabla
        if "|" in l and i + 1 < n and es_sep_tabla(lineas[i + 1]):
            cab = celdas(l); i += 2
            filas = []
            while i < n and "|" in lineas[i] and lineas[i].strip():
                filas.append(celdas(lineas[i])); i += 1
            t = ["<table><thead><tr>"] + [f"<th>{inline(c)}</th>" for c in cab] + ["</tr></thead><tbody>"]
            for f in filas:
                f = (f + [""] * len(cab))[:len(cab)]
                t += ["<tr>"] + [f"<td>{inline(c)}</td>" for c in f] + ["</tr>"]
            out.append("".join(t + ["</tbody></table>"]))
            continue

        # cita (puede contener tablas y listas dentro)
        if l.startswith(">"):
            buf = []
            while i < n and (lineas[i].startswith(">") or
                             (lineas[i].strip() and buf and not lineas[i].startswith(("#", "|", "-", "*")))):
                if not lineas[i].startswith(">"):
                    break
                buf.append(re.sub(r"^>\s?", "", lineas[i])); i += 1
            out.append("<blockquote>" + convertir("\n".join(buf)) + "</blockquote>")
            continue

        # regla horizontal
        if re.match(r"^-{3,}\s*$", l):
            out.append("<hr>"); i += 1; continue

        # encabezado
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m:
            niv = len(m.group(1))
            out.append(f"<h{niv}>{inline(m.group(2))}</h{niv}>"); i += 1; continue

        # listas
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", l)
        if m:
            orden = bool(re.match(r"\d+\.", m.group(2)))
            tag = "ol" if orden else "ul"
            items = []
            while i < n:
                mm = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lineas[i])
                if not mm:
                    # continuación indentada del ítem anterior
                    if items and lineas[i].startswith(("  ", "\t")) and lineas[i].strip():
                        items[-1] += " " + lineas[i].strip(); i += 1; continue
                    break
                items.append(mm.group(3)); i += 1
            cuerpo = "".join(f"<li>{inline(x)}</li>" for x in items)
            out.append(f"<{tag}>{cuerpo}</{tag}>")
            continue

        # párrafo
        if l.strip():
            buf = []
            while i < n and lineas[i].strip() and not lineas[i].startswith(("#", ">", "|", "```")) \
                    and not re.match(r"^(\s*)([-*+]|\d+\.)\s+", lineas[i]) \
                    and not re.match(r"^-{3,}\s*$", lineas[i]):
                # dos espacios al final = salto de línea explícito (Markdown estándar)
                buf.append(lineas[i].rstrip() + ("\x02" if lineas[i].endswith("  ") else ""))
                i += 1
            txt = inline(" ".join(x.strip() for x in buf)).replace("\x02", "<br>")
            out.append(f"<p>{txt}</p>")
            continue

        i += 1

    return "\n".join(out)


def incrustar_figuras(cuerpo, dir_graficas):
    """Inserta los SVG como vectoriales donde el informe los menciona."""
    figs = [("percentiles.svg",
             "Figura 1 — Latencia por percentil. Por la mediana las tres cumplen; "
             "la diferencia está en la cola."),
            ("histograma.svg",
             "Figura 2 — Distribución. La variante D no forma una campana sino dos picos: "
             "son los tics del reloj.")]
    bloque = []
    for nombre, pie in figs:
        ruta = os.path.join(dir_graficas, nombre)
        if not os.path.exists(ruta):
            continue
        with open(ruta) as fh:
            svg = fh.read()
        svg = re.sub(r'<\?xml[^>]*\?>', '', svg).strip()
        bloque.append(f"<figure>{svg}<figcaption>{html.escape(pie)}</figcaption></figure>")
    if not bloque:
        print("  aviso: no se encontraron los SVG; ejecuta antes harness/graficas.py")
        return cuerpo

    ancla = re.search(r"<p><strong>Figuras:</strong>.*?</p>", cuerpo, re.S)
    if ancla:
        return cuerpo[:ancla.end()] + "\n" + "\n".join(bloque) + cuerpo[ancla.end():]
    return cuerpo + "\n" + "\n".join(bloque)


def main():
    aqui = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=os.path.join(aqui, "INFORME.md"))
    ap.add_argument("--pdf", default=os.path.join(aqui, "INFORME.pdf"))
    ap.add_argument("--graficas", default=os.path.join(aqui, "harness", "graficas"))
    ap.add_argument("--html", default=None, help="conservar el HTML intermedio")
    a = ap.parse_args()

    with open(a.md) as fh:
        md = fh.read()

    cuerpo = incrustar_figuras(convertir(md), a.graficas)
    doc = (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
           f'<title>Reto de Latencia Mínima — Informe</title><style>{CSS}</style>'
           f'</head><body>{cuerpo}</body></html>')

    ruta_html = a.html or os.path.join(tempfile.gettempdir(), "informe-latencia.html")
    with open(ruta_html, "w") as fh:
        fh.write(doc)

    if not os.path.exists(CHROME):
        print(f"error: no se encontró Chrome en {CHROME}", file=sys.stderr)
        print(f"el HTML quedó en {ruta_html}: ábrelo e imprime a PDF a mano", file=sys.stderr)
        return 1

    r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", "--virtual-time-budget=4000",
                        f"--print-to-pdf={a.pdf}", f"file://{ruta_html}"],
                       capture_output=True, text=True)
    if not os.path.exists(a.pdf):
        print("error al renderizar:", r.stderr[-700:], file=sys.stderr)
        return 1
    print(f"  html -> {ruta_html}")
    print(f"  pdf  -> {a.pdf}  ({os.path.getsize(a.pdf)/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
