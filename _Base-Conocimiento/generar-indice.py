#!/usr/bin/env python3
"""Genera INDICE.html: la portada navegable de todos los documentos del proyecto.

Escanea el proyecto y clasifica lo que encuentra por módulo y por tipo. Se ejecuta
de nuevo cada vez que alguien añade un documento — así el índice no envejece.

    _Base-Conocimiento/generar-indice.py

El título y la descripción de cada HTML se extraen del propio archivo (<title>,
meta description o primer párrafo). No hay lista de archivos escrita a mano: si
Freddy sube un aporte mañana, aparece solo.

Sin dependencias externas. El estilo vive en _Base-Conocimiento/estilo.py.
"""
import html
import pathlib
import re
import sys
import urllib.parse
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "_Base-Conocimiento"))
try:
    from estilo import CSS_INDICE, pagina
except ImportError:
    sys.exit("No se encuentra _Base-Conocimiento/estilo.py — ¿se movió de sitio?")

EXCLUIR = {".playwright-mcp", "node_modules", "__pycache__", ".git", ".claude"}
# títulos que pone la plantilla de Brightspace y no describen nada
TITULOS_INUTILES = {"tabs", "module introduction", "meet your facilitator",
                    "elements page", "document", "untitled", ""}

TIPOS = {
    "consolidado": ("CONSOLIDADO", "t-consolidado"),
    "oficial": ("MATERIAL OFICIAL", "t-oficial"),
    "aporte": ("APORTE", "t-aporte"),
    "herramienta": ("HERRAMIENTA", "t-herramienta"),
    "md": ("MARKDOWN", "t-md"),
    "pdf": ("PDF", "t-md"),
}


def limpia(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def lee_cabecera(ruta):
    """Título y descripción, sacados del propio documento."""
    try:
        h = ruta.read_text(encoding="utf-8", errors="replace")[:60000]
    except OSError:
        return None, None
    m = re.search(r"<title[^>]*>(.*?)</title>", h, re.S | re.I)
    titulo = limpia(m.group(1)) if m else ""
    if titulo.lower() in TITULOS_INUTILES:
        titulo = ""
    desc = ""
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', h, re.I)
    if m:
        desc = limpia(m.group(1))
    if not desc:
        for clase in ("lede", "standfirst", "lead"):
            m = re.search(rf'<p[^>]*class=["\'][^"\']*{clase}[^"\']*["\'][^>]*>(.*?)</p>', h, re.S | re.I)
            if m:
                desc = limpia(m.group(1))
                break
    if not desc:
        for m in re.finditer(r"<p[^>]*>(.*?)</p>", h, re.S | re.I):
            t = limpia(m.group(1))
            if len(t) > 40:
                desc = t
                break
    return titulo, (desc[:190] + "…" if len(desc) > 190 else desc)


def nombre_legible(ruta):
    n = ruta.stem
    if n.lower() == "index":
        n = ruta.parent.name
    n = n.replace("-", " ").replace("_", " ")
    n = re.sub(r"^m\d+\s+", "", n)
    n = re.sub(r"\s+(danny|camilo|freddy)$", "", n, flags=re.I)
    return n[:1].upper() + n[1:]


def clasifica(rel):
    p = str(rel)
    if "/Consolidado/" in p:
        return "consolidado", None
    if "/Material-Clase/" in p or re.match(r"^Modulo \d+/[^/]+\.html/", p):
        return "oficial", None
    m = re.search(r"/Aportes/([^/]+)/", p)
    if m:
        return "aporte", m.group(1)
    if "/Ejercicios/" in p or "/Laboratorios/" in p:
        return "herramienta", None
    return "otro", None


def modulo_de(rel):
    m = re.match(r"^(Modulo \d+)/", str(rel))
    return m.group(1) if m else "Transversal"


def tarjeta(rel, titulo, desc, tipo, extra="", destacado=False):
    etiqueta, clase = TIPOS.get(tipo, ("DOCUMENTO", "t-md"))
    href = urllib.parse.quote(str(rel))
    ruta = RAIZ / rel
    try:
        kb = max(1, ruta.stat().st_size // 1024)
        peso = f"{kb} KB"
    except OSError:
        peso = ""
    apagado = " apagado" if "superada" in str(rel) else ""
    clases = f"doc{' destacado' if destacado else ''}{apagado}"
    pie = f'<span class="tipo {clase}">{etiqueta}</span>'
    if extra:
        pie += f"<span>{html.escape(extra)}</span>"
    pie += f'<span>{peso}</span><span>{html.escape(str(rel.parent))}/</span>'
    d = f'<span class="d">{html.escape(desc)}</span>' if desc else ""
    return (f'<a class="{clases}" href="{href}">'
            f'<span class="t">{html.escape(titulo)}</span>{d}'
            f'<span class="f">{pie}</span></a>')


def main():
    docs = []
    for ruta in sorted(RAIZ.rglob("*.html")):
        if not ruta.is_file() or any(p in EXCLUIR for p in ruta.parts):
            continue
        rel = ruta.relative_to(RAIZ)
        if rel.name == "INDICE.html":
            continue
        tipo, autor = clasifica(rel)
        titulo, desc = lee_cabecera(ruta)
        docs.append({"rel": rel, "titulo": titulo or nombre_legible(rel), "desc": desc or "",
                     "tipo": tipo, "autor": autor, "mod": modulo_de(rel)})

    secciones, toc = [], []

    def sec(sid, título, html_cuerpo):
        toc.append((sid, título))
        secciones.append(f'<h2 id="{sid}">{html.escape(título)}</h2>{html_cuerpo}')

    # --- Empieza aquí ---
    destacados = []
    # (ruta, descripción, título propio). El título propio es para cuando el <title> del
    # documento no dice qué es desde el índice: "Reto de Latencia Minima - Group 2" no
    # distingue la presentacion del informe. None = se usa el <title> del documento.
    for patron, desc, titulo_propio in [
        ("Consolidado/m1-consolidado.html", "Las notas de estudio del Módulo 1: las 5 fuentes fusionadas, con las contradicciones registradas.", None),
        ("Aportes/danny/m1-clasificador-hosts-danny.html", "Qué construimos en el reto, cómo funciona y dónde encaja cada pieza. El documento de la reunión.", None),
        ("Aportes/danny/m1-presentacion-reto-latencia-danny.html", "Las láminas de la sustentación, con las cifras de la corrida del 17/09. Borrador: sin revisar por Freddy ni Camilo.", "Presentación del reto — Módulo 1"),
    ]:
        for d in docs:
            if str(d["rel"]).endswith(patron):
                destacados.append(tarjeta(d["rel"], titulo_propio or d["titulo"], desc, d["tipo"], destacado=True))
    destacados.append(tarjeta(pathlib.Path("README.md"), "README — puerta de entrada",
                              "Qué es este repositorio, cómo está organizado y cuál es el flujo de trabajo.", "md", destacado=True))
    destacados.append(tarjeta(pathlib.Path("CONTRIBUIR.md"), "CONTRIBUIR — cómo aportar",
                              "Dónde va cada cosa, nombres de archivo, ficha de autoría y lo que no se hace.", "md", destacado=True))
    sec("empieza-aqui", "Empieza aquí", '<div class="docs">' + "".join(destacados) + "</div>")

    # --- por módulo ---
    orden_tipo = ["consolidado", "oficial", "aporte", "herramienta", "otro"]
    titulo_grupo = {"consolidado": "Conocimiento consolidado", "oficial": "Material oficial",
                    "aporte": "Aportes individuales", "herramienta": "Herramientas del reto",
                    "otro": "Otros"}
    for mod in sorted({d["mod"] for d in docs if d["mod"] != "Transversal"}):
        cuerpo = []
        for tipo in orden_tipo:
            grupo = [d for d in docs if d["mod"] == mod and d["tipo"] == tipo]
            if not grupo:
                continue
            cuerpo.append(f"<h3>{titulo_grupo[tipo]}</h3>")
            cuerpo.append('<div class="docs">' + "".join(
                tarjeta(d["rel"], d["titulo"], d["desc"], d["tipo"],
                        extra=d["autor"] or "") for d in grupo) + "</div>")
        # quién no ha aportado todavía
        if mod == "Modulo 1":
            con_aporte = {d["autor"] for d in docs if d["mod"] == mod and d["autor"]}
            faltan = [a for a in ("danny", "camilo", "freddy") if a not in con_aporte]
            if faltan:
                cuerpo.append(f'<div class="vacio">Sin aportes todavía: <strong>'
                              f'{", ".join(faltan)}</strong>.</div>')
        sec(mod.lower().replace(" ", "-"), mod, "".join(cuerpo))

    # --- transversales en Markdown ---
    trans = [
        ("_Base-Conocimiento/INDICE.md", "Índice maestro y estado", "Estado por módulo, entregas pendientes y preguntas abiertas del diplomado."),
        ("_Base-Conocimiento/CRONOGRAMA.md", "Cronograma", "Fechas, sesiones y análisis de riesgos del calendario."),
        ("_Base-Conocimiento/EQUIPO.md", "Equipo — Group 2", "Quién es quién, reparto del reto y ambigüedades pendientes de confirmar."),
        ("_Base-Conocimiento/GLOSARIO.md", "Glosario", "Términos con definición contextual."),
        ("_Base-Conocimiento/MAPA-CONCEPTUAL.md", "Mapa conceptual", "Grafo acumulativo de conceptos entre módulos."),
        ("_Base-Conocimiento/Aprendizajes/LEEME.md", "Aprendizajes reutilizables", "Lo que sale de un módulo cerrado y sirve para los siguientes."),
        ("CLAUDE.md", "CLAUDE.md — contrato para IA", "Resumen ejecutable del contrato de trabajo."),
        ("PROMPT-MAESTRO.md", "PROMPT-MAESTRO.md", "El contrato completo, fuente de verdad."),
    ]
    tarjetas = [tarjeta(pathlib.Path(r), t, d, "md") for r, t, d in trans if (RAIZ / r).is_file()]
    # Los ADR de un ejercicio viven CON el ejercicio (ver _Base-Conocimiento/ADR/LEEME.md),
    # asi que el indice los recoge de los dos sitios en vez de exigir que se dupliquen.
    adr = sorted((RAIZ / "_Base-Conocimiento/ADR").glob("ADR-*.md"))
    adr += sorted(RAIZ.glob("Modulo */Ejercicios/*/*/docs/ADR/ADR-*.md"))
    # ADR-000 es la PLANTILLA, no una decision: no va en el listado de decisiones.
    # Ademas existe en los dos sitios, asi que filtrarla evita listarla por duplicado.
    adr = [a for a in adr if not a.stem.startswith("ADR-000")]
    for a in adr:
        rel = a.relative_to(RAIZ)
        titulo = a.stem.replace("-", " ")
        primera = ""
        for ln in a.read_text(encoding="utf-8", errors="replace").split("\n"):
            if ln.startswith("# "):
                titulo = ln[2:].strip()
            elif ln.strip() and not ln.startswith(("#", ">", "|", "-")):
                primera = ln.strip()
                break
        tarjetas.append(tarjeta(rel, titulo, primera[:150], "md"))
    sec("transversal", "Base de conocimiento y decisiones", '<div class="docs">' + "".join(tarjetas) + "</div>")

    # --- documentos del reto ---
    reto = RAIZ / "Modulo 1/Ejercicios/Reto-Latencia-Minima"
    if reto.is_dir():
        claves = ["PLAN-DE-TRABAJO.md", "ENUNCIADO.md", "DISENO-ARQUITECTURA.md",
                  "ESPEC-MEDICION.md", "INFORME.md", "INFORME.pdf", "GUION-VIDEO.md",
                  "PLAN-EQUIPO.md", "OPCIONES-SISTEMA.md"]
        t2 = []
        for c in claves:
            f = reto / c
            if f.is_file():
                rel = f.relative_to(RAIZ)
                t2.append(tarjeta(rel, c, "", "pdf" if c.endswith(".pdf") else "md"))
        if t2:
            sec("reto-m1", "Reto de Latencia Mínima — documentos",
                '<div class="docs">' + "".join(t2) + "</div>")

    toc_html = "".join(f'<li><a href="#{s}">{html.escape(t)}</a></li>' for s, t in toc)
    n_html = len([d for d in docs])
    dst = RAIZ / "INDICE.html"
    dst.write_text(pagina(
        titulo="Índice del proyecto",
        kicker="Diplomado en Arquitectura de Software y Cloud Computing · Group 2",
        meta=f"{n_html} documentos HTML · generado el {datetime.now():%d/%m/%Y %H:%M}",
        toc=toc_html,
        cuerpo="".join(secciones),
        pie="<p>Generado con <code>_Base-Conocimiento/generar-indice.py</code>. "
            "No editar a mano: se regenera. Vuelve a ejecutarlo cada vez que añadas un documento.</p>",
        css_extra=CSS_INDICE), encoding="utf-8")
    print(f"{dst}  ({dst.stat().st_size // 1024} KB · {n_html} documentos · {len(toc)} secciones)")


if __name__ == "__main__":
    main()
