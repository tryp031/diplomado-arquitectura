#!/usr/bin/env python3
"""Genera el HTML de lectura de una nota consolidada a partir de su Markdown.

El .md es la ÚNICA fuente de verdad. Este script solo lo presenta. Nunca se edita
el .html a mano: se regenera.

Sin dependencias externas — solo biblioteca estándar, igual que graficas.py.
El estilo vive en _Base-Conocimiento/estilo.py, compartido con generar-indice.py.

Uso:
    ./consolidar_html.py "Modulo 1/Consolidado/m1-consolidado.md"
    ./consolidar_html.py <ruta.md> --out <ruta.html>     # destino explícito

Subconjunto de Markdown soportado (documentado a propósito: si el consolidado usa
algo fuera de esta lista, saldrá como texto plano y hay que ampliar el script):

    # ## ### ####      encabezados
    | a | b |          tablas con fila de separación |---|
    - / * / 1.         listas, un nivel de anidación
    > cita             blockquote, varias líneas
    ```lang           bloque de código
    ---                separador
    **negrita** *cursiva* `código` [texto](url)
    [Curso] [Complementario] [Recomendación] [Hipótesis]   → se marcan como etiqueta
"""
import argparse
import html
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "_Base-Conocimiento"))
try:
    from estilo import pagina
except ImportError:
    sys.exit("No se encuentra _Base-Conocimiento/estilo.py — ¿se movió de sitio?")

BADGES = {
    "Curso": "b-curso",
    "Complementario": "b-compl",
    "Recomendación": "b-recom",
    "Recomendacion": "b-recom",
    "Hipótesis": "b-hipo",
    "Hipotesis": "b-hipo",
}


def slug(texto):
    t = re.sub(r"[^\w\s-]", "", texto.lower(), flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", t).strip("-") or "s"


def limpio(texto):
    """Texto sin marcado, para el índice lateral."""
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", texto)
    t = t.replace("**", "").replace("`", "")
    return re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", t).strip()


def inline(texto):
    """Convierte el marcado de línea. Escapa HTML primero: el .md es dato, no código."""
    t = html.escape(texto, quote=False)
    # las etiquetas van primero: en el .md se escriben `[Curso]`, entre backticks,
    # y si no se tratan aquí acabarían como código en línea en vez de etiqueta
    for nombre, clase in BADGES.items():
        etiqueta = f'<span class="pill {clase}">{nombre}</span>'
        t = t.replace(f"`[{nombre}]`", etiqueta).replace(f"[{nombre}]", etiqueta)
    # código en línea: se aparta para que no se le aplique negrita ni cursiva dentro
    trozos = []

    def guarda(m):
        trozos.append(m.group(1))
        return f"\x00{len(trozos) - 1}\x00"

    t = re.sub(r"`([^`]+)`", guarda, t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\x00(\d+)\x00",
               lambda m: f"<code>{trozos[int(m.group(1))]}</code>", t)
    return t


def fila_tabla(linea):
    celdas = linea.strip().strip("|").split("|")
    return [c.strip() for c in celdas]


def render(md):
    lineas = md.split("\n")
    out, toc = [], []
    visto_h1 = False
    i, n = 0, len(lineas)

    while i < n:
        ln = lineas[i]
        cruda = ln.rstrip()
        vacia = not cruda.strip()

        if vacia:
            i += 1
            continue

        # bloque de código
        if cruda.lstrip().startswith("```"):
            lang = cruda.strip().strip("`").strip()
            i += 1
            cuerpo = []
            while i < n and not lineas[i].strip().startswith("```"):
                cuerpo.append(lineas[i])
                i += 1
            i += 1
            clase = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre{clase}><code>{html.escape(chr(10).join(cuerpo))}</code></pre>")
            continue

        # separador
        if re.fullmatch(r"-{3,}", cruda.strip()):
            out.append("<hr>")
            i += 1
            continue

        # encabezado
        m = re.match(r"^(#{1,6})\s+(.*)$", cruda)
        if m:
            nivel, texto = len(m.group(1)), m.group(2).strip()
            sid = slug(texto)
            i += 1
            # el primer h1 ya se muestra en la cabecera: no se repite en el cuerpo
            if nivel == 1 and not visto_h1:
                visto_h1 = True
                continue
            if nivel == 2:
                toc.append((sid, limpio(texto)))
            out.append(f'<h{nivel} id="{sid}">{inline(texto)}</h{nivel}>')
            continue

        # tabla: fila de cabecera + fila de separación
        if cruda.lstrip().startswith("|") and i + 1 < n and \
           re.match(r"^\s*\|[\s:|-]+\|\s*$", lineas[i + 1]):
            cab = fila_tabla(cruda)
            i += 2
            filas = []
            while i < n and lineas[i].strip().startswith("|"):
                filas.append(fila_tabla(lineas[i]))
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in cab)
            cuerpo = []
            for f in filas:
                f = (f + [""] * len(cab))[:len(cab)]
                cuerpo.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in f) + "</tr>")
            out.append('<div class="tw"><table><thead><tr>' + th +
                       "</tr></thead><tbody>" + "".join(cuerpo) + "</tbody></table></div>")
            continue

        # cita
        if cruda.lstrip().startswith(">"):
            cuerpo = []
            while i < n and lineas[i].lstrip().startswith(">"):
                cuerpo.append(re.sub(r"^\s*>\s?", "", lineas[i]))
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(x.strip() for x in cuerpo))}</p></blockquote>")
            continue

        # listas
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", cruda)
        if m:
            ordenada = bool(re.match(r"\d+\.", m.group(2)))
            tag = "ol" if ordenada else "ul"
            items, nivel_base = [], len(m.group(1))
            while i < n:
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lineas[i].rstrip())
                if not mm:
                    # continuación de un ítem en la línea siguiente
                    if items and lineas[i].strip() and lineas[i].startswith(("  ", "\t")):
                        items[-1] = (items[-1][0], items[-1][1] + " " + lineas[i].strip())
                        i += 1
                        continue
                    break
                items.append((len(mm.group(1)) - nivel_base, mm.group(3)))
                i += 1
            html_items, anidada = [], False
            for sangria, txt in items:
                if sangria >= 2 and not anidada:
                    html_items.append(f"<ul><li>{inline(txt)}</li>")
                    anidada = True
                elif sangria >= 2:
                    html_items.append(f"<li>{inline(txt)}</li>")
                else:
                    if anidada:
                        html_items.append("</ul>")
                        anidada = False
                    html_items.append(f"<li>{inline(txt)}</li>")
            if anidada:
                html_items.append("</ul>")
            out.append(f"<{tag}>" + "".join(html_items) + f"</{tag}>")
            continue

        # párrafo: líneas consecutivas hasta una vacía o el inicio de otro bloque
        cuerpo = []
        while i < n and lineas[i].strip() and not re.match(
                r"^\s*(#{1,6}\s|\||>|```|-{3,}$|([-*]|\d+\.)\s)", lineas[i].rstrip()):
            cuerpo.append(lineas[i].strip())
            i += 1
        if cuerpo:
            out.append(f"<p>{inline(' '.join(cuerpo))}</p>")
        else:
            i += 1

    return "\n".join(out), toc


def main():
    ap = argparse.ArgumentParser(description="Genera el HTML de una nota consolidada.")
    ap.add_argument("md", help="ruta del .md consolidado")
    ap.add_argument("--out", help="ruta del .html (por defecto, el mismo nombre con .html)")
    a = ap.parse_args()

    src = pathlib.Path(a.md)
    if not src.is_file():
        sys.exit(f"No existe: {src}")
    dst = pathlib.Path(a.out) if a.out else src.with_suffix(".html")

    texto = src.read_text(encoding="utf-8")
    cuerpo, toc = render(texto)

    m = re.search(r"^#\s+(.+)$", texto, flags=re.M)
    titulo = m.group(1).strip() if m else src.stem

    toc_html = "".join(f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t in toc)
    dst.write_text(pagina(
        titulo=html.escape(titulo),
        kicker="Diplomado en Arquitectura de Software y Cloud Computing · Group 2",
        meta=html.escape(src.name),
        toc=toc_html,
        cuerpo=cuerpo,
        pie=f"<p>Generado desde <code>{html.escape(src.name)}</code> con "
            "<code>consolidar_html.py</code>. No editar este HTML: se regenera. "
            "La fuente de verdad es el Markdown.</p>"), encoding="utf-8")
    print(f"{dst}  ({dst.stat().st_size // 1024} KB · {len(toc)} secciones)")


if __name__ == "__main__":
    main()
