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
from datetime import date, datetime

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

# Calendario oficial (fuente: _Base-Conocimiento/CRONOGRAMA.md). El estado de cada módulo
# (Cerrado / En curso / Próximo) NO está escrito aquí: se calcula con la fecha de hoy.
# Encuentros sincrónicos: siempre a las 6:00 pm.
A = 2026
MODULOS = {
    "Modulo 0": ("Inducción y aula virtual", date(A, 9, 2), date(A, 9, 6), [date(A, 9, 8)]),
    "Modulo 1": ("Fundamentos de la arquitectura de software", date(A, 9, 7), date(A, 9, 29),
                 [date(A, 9, 15), date(A, 9, 29)]),
    "Modulo 2": ("Requerimientos y tácticas de arquitectura", date(A, 9, 30), date(A, 10, 20),
                 [date(A, 10, 6), date(A, 10, 13)]),
    "Modulo 3": ("Por publicar", date(A, 10, 21), date(A, 11, 3), [date(A, 10, 27), date(A, 11, 3)]),
    "Modulo 4": ("Por publicar", date(A, 11, 4), date(A, 11, 10), [date(A, 11, 10)]),
}
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# "Lo principal" de cada módulo: (final de la ruta, descripción, título propio o None).
# El título propio sirve cuando el <title> no dice qué es desde el índice.
DESTACADOS = {
    "Modulo 2": [
        ("Aportes/danny/m2-cuaderno-estudio-danny.html",
         "Notas de estudio del módulo con método, matriz de trade-offs, autoevaluación y glosario. Empieza por aquí.", "Cuaderno de estudio del Módulo 2"),
        ("Material-Clase/Actividad-Reto2.html",
         "Enunciado oficial del Reto 2 (alerta para flota vehicular): requisitos, restricciones y las dos rúbricas.", "Reto 2 — enunciado oficial"),
        ("Aportes/danny/m2-analisis-apertura-danny.html",
         "Errores del material y análisis del Reto 2: ASR, opciones de arquitectura, riesgos y calendario.", "Análisis del módulo y del Reto 2"),
        ("Material-Clase/Genially-Contenidos-Obligatorios.html",
         "Transcripción de los 4 Genially obligatorios: ASR, ADD, disponibilidad, desempeño e interoperabilidad.", "Los 4 Genially obligatorios"),
    ],
    "Modulo 1": [
        ("Consolidado/m1-consolidado.html", "Las notas de estudio del Módulo 1: las 5 fuentes fusionadas, con las contradicciones registradas.", None),
        ("Aportes/danny/m1-clasificador-hosts-danny.html", "Qué construimos en el reto, cómo funciona y dónde encaja cada pieza. El documento de la reunión.", None),
        ("Aportes/danny/m1-presentacion-reto-latencia-v2-danny.html", "La presentación oficial de la sustentación del 29/09: 9 láminas, con demo del sistema y la ejecución del 28/09.", "Presentación oficial del reto — Módulo 1"),
        ("Aportes/danny/m1-presentacion-reto-latencia-danny.html", "Primer draft de la sustentación, con las cifras del 24/09 y el apéndice técnico. Superado por la v2: se conserva, no se presenta.", "Presentación del reto — Módulo 1"),
    ],
}

# Descripciones para documentos generados desde Markdown, cuyo primer párrafo es una ficha
# de metadatos y no sirve de resumen. Clave: nombre de archivo sin extensión.
DESCRIPCIONES = {
    "Modulo2-Brightspace": "Páginas del módulo en Brightspace: bienvenida, contenidos, conclusiones y lecturas.",
    "Tacticas-Disponibilidad": "Deck oficial: defecto, error y falla; tácticas de detección, recuperación y prevención; hot/warm/cold spare, TMR, circuit breaker.",
    "Tacticas-Desempeno": "Deck oficial: tiempo y concurrencia; tácticas de control de demanda y gestión de recursos; service mesh, load balancer, map-reduce.",
    "Tacticas-Seguridad": "Deck oficial: confidencialidad, integridad y disponibilidad; tácticas de detectar, resistir, reaccionar y recuperarse; IPS.",
    "Tacticas-Desplegabilidad": "Deck oficial (complementario): pipeline y sistema desplegado; blue/green, rolling, canary, feature toggle.",
    "Tacticas-Usabilidad": "Deck oficial (complementario): iniciativa del usuario y del sistema; MVC, Observer, Memento.",
}

# Títulos para páginas cuyo <title> no dice qué son desde el índice.
TITULOS = {
    "Modulo2-Brightspace": "Módulo 2 en Brightspace — páginas y lecturas",
}

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


def tarjeta(rel, titulo, desc, tipo, extra="", destacado=False, autor=""):
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
        pie += f'<span class="autor">{html.escape(extra)}</span>'
    pie += f'<span>{peso}</span><span>{html.escape(str(rel.parent))}/</span>'
    d = f'<span class="d">{html.escape(desc)}</span>' if desc else ""
    buscable = html.escape(f"{titulo} {desc} {rel} {autor}".lower(), quote=True)
    return (f'<a class="{clases}" href="{href}" data-tipo="{tipo}" data-autor="{html.escape(autor)}" '
            f'data-q="{buscable}">'
            f'<span class="t">{html.escape(titulo)}</span>{d}'
            f'<span class="f">{pie}</span></a>')


def estado_modulo(mod, hoy):
    _, ini, cie, _ = MODULOS[mod]
    if hoy > cie:
        return "cerrado", "Cerrado"
    if hoy >= ini:
        return "curso", "En curso"
    return "proximo", "Próximo"


def fecha_corta(d):
    return f"{DIAS[d.weekday()]} {d:%d/%m}"


def panel_estado(hoy, conteo):
    """Tira con los 5 módulos del diplomado y su estado calculado por fecha."""
    celdas = []
    for mod, (titulo, ini, cie, enc) in MODULOS.items():
        clase, etiqueta = estado_modulo(mod, hoy)
        n = conteo.get(mod, 0)
        num = mod.split()[1]
        cuerpo = (f'<span class="mn">Módulo {num}</span><span class="mt">{html.escape(titulo)}</span>'
                  f'<span class="mf">{ini:%d/%m} → {cie:%d/%m}</span>'
                  f'<span class="me"><span class="est e-{clase}">{etiqueta}</span>'
                  f'{f"<span>{n} documentos</span>" if n else "<span>sin documentos</span>"}</span>')
        if n:
            celdas.append(f'<a class="mod m-{clase}" href="#{mod.lower().replace(" ", "-")}">{cuerpo}</a>')
        else:
            celdas.append(f'<div class="mod m-{clase}">{cuerpo}</div>')
    return '<div class="modulos">' + "".join(celdas) + "</div>"


def panel_ahora(hoy, docs_por_mod):
    """El módulo en curso: fechas clave y accesos directos. Se calcula, no se edita."""
    en_curso = [m for m in MODULOS if estado_modulo(m, hoy)[0] == "curso"]
    if not en_curso:
        return ""
    mod = en_curso[0]
    titulo, ini, cie, enc = MODULOS[mod]
    dias = (cie - hoy).days
    proximos = [e for e in enc if e >= hoy]
    hitos = []
    if proximos:
        hitos.append(("Próximo encuentro", f"{fecha_corta(proximos[0])} · 6:00 pm"))
    if len(proximos) > 1:
        hitos.append(("Siguiente", f"{fecha_corta(proximos[1])} · 6:00 pm"))
    hitos.append(("Cierre del módulo", f"{fecha_corta(cie)} · quedan {dias} días"))
    lis = "".join(f'<li><span>{html.escape(k)}</span><strong>{html.escape(v)}</strong></li>' for k, v in hitos)
    botones = ""
    for patron, _desc, titulo_propio in DESTACADOS.get(mod, []):
        for d in docs_por_mod.get(mod, []):
            if str(d["rel"]).endswith(patron):
                botones += (f'<a class="btn" href="{urllib.parse.quote(str(d["rel"]))}">'
                            f'{html.escape(titulo_propio or d["titulo"])}</a>')
    return (f'<div class="ahora"><div class="ah-l"><p class="ah-k">Ahora · {html.escape(mod.replace("Modulo", "Módulo"))}</p>'
            f'<h3>{html.escape(titulo)}</h3><ul class="hitos">{lis}</ul></div>'
            f'<div class="ah-r"><p class="ah-k">Acceso directo</p><div class="botones">{botones}</div></div></div>')


def main():
    hoy = date.today()
    docs = []
    for ruta in sorted(RAIZ.rglob("*.html")):
        if not ruta.is_file() or any(p in EXCLUIR for p in ruta.parts):
            continue
        rel = ruta.relative_to(RAIZ)
        if rel.name == "INDICE.html":
            continue
        tipo, autor = clasifica(rel)
        titulo, desc = lee_cabecera(ruta)
        desc = DESCRIPCIONES.get(ruta.stem, desc)
        titulo = TITULOS.get(ruta.stem, titulo)
        docs.append({"rel": rel, "titulo": titulo or nombre_legible(rel), "desc": desc or "",
                     "tipo": tipo, "autor": autor, "mod": modulo_de(rel)})
    # PDF oficiales que viven en Material-Clase (p. ej. el enunciado de un reto)
    for ruta in sorted(RAIZ.glob("Modulo */Material-Clase/*.pdf")):
        rel = ruta.relative_to(RAIZ)
        docs.append({"rel": rel, "titulo": nombre_legible(rel) + " (PDF original)", "desc": "",
                     "tipo": "oficial", "autor": None, "mod": modulo_de(rel)})

    por_mod = {}
    for d in docs:
        por_mod.setdefault(d["mod"], []).append(d)
    conteo = {m: len(v) for m, v in por_mod.items()}

    secciones, toc = [], []

    def sec(sid, titulo, cuerpo):
        toc.append((sid, titulo))
        secciones.append(f'<section class="bloque" id="{sid}"><h2>{html.escape(titulo)}</h2>{cuerpo}</section>')

    # --- Ahora: panel del módulo en curso ---
    sec("ahora", "Ahora", panel_ahora(hoy, por_mod) + panel_estado(hoy, conteo))

    # --- por módulo: el más reciente primero; los cerrados van plegados ---
    orden_tipo = ["consolidado", "oficial", "aporte", "herramienta", "otro"]
    titulo_grupo = {"consolidado": "Conocimiento consolidado", "oficial": "Material oficial",
                    "aporte": "Aportes individuales", "herramienta": "Herramientas del reto",
                    "otro": "Otros"}
    mods = sorted((m for m in por_mod if m != "Transversal"), key=lambda m: -int(m.split()[1]))
    for mod in mods:
        destacados = []
        usados = set()
        for patron, desc, titulo_propio in DESTACADOS.get(mod, []):
            for d in por_mod[mod]:
                if str(d["rel"]).endswith(patron):
                    usados.add(d["rel"])
                    destacados.append(tarjeta(d["rel"], titulo_propio or d["titulo"], desc, d["tipo"],
                                              extra=d["autor"] or "", destacado=True, autor=d["autor"] or ""))
        guias = []
        for f in [RAIZ / mod / "README.md", *sorted((RAIZ / mod / "Temario").glob("*.md"))]:
            if f.is_file():
                rel = f.relative_to(RAIZ)
                t = f.stem.replace("-", " ")
                for ln in f.read_text(encoding="utf-8", errors="replace").split("\n"):
                    if ln.startswith("# "):
                        t = ln[2:].strip()
                        break
                guias.append(tarjeta(rel, t, "Puerta de entrada del módulo." if f.name == "README.md" else "Temario y preguntas abiertas.", "md"))
        cuerpo = []
        if destacados:
            cuerpo.append('<div class="grupo"><h3>Lo principal</h3><div class="docs">'
                          + "".join(destacados) + "</div></div>")
        if guias:
            cuerpo.append('<div class="grupo"><h3>Guías del módulo</h3><div class="docs">'
                          + "".join(guias) + "</div></div>")
        for tipo in orden_tipo:
            grupo = [d for d in por_mod[mod] if d["tipo"] == tipo and d["rel"] not in usados]
            if not grupo:
                continue
            cuerpo.append(f'<div class="grupo"><h3>{titulo_grupo[tipo]}</h3><div class="docs">' + "".join(
                tarjeta(d["rel"], d["titulo"], d["desc"], d["tipo"], extra=d["autor"] or "",
                        autor=d["autor"] or "") for d in grupo) + "</div></div>")
        # consolidado pendiente / quién no ha aportado todavía (solo módulos con aportes)
        if (RAIZ / mod / "Aportes").is_dir():
            if not any(d["tipo"] == "consolidado" for d in por_mod[mod]):
                cuerpo.append('<div class="vacio">Consolidado: <strong>pendiente</strong>. '
                              'Se genera al fusionar los aportes (skill <code>consolidar-conocimiento</code>).</div>')
            con_aporte = {d["autor"] for d in por_mod[mod] if d["autor"]}
            faltan = [a for a in ("danny", "camilo", "freddy") if a not in con_aporte]
            if faltan:
                cuerpo.append(f'<div class="vacio">Sin aportes todavía: <strong>'
                              f'{", ".join(faltan)}</strong>.</div>')
        clase, etiqueta = estado_modulo(mod, hoy)
        titulo_mod, ini, cie, _ = MODULOS.get(mod, (mod, None, None, []))
        abierto = " open" if clase == "curso" else ""
        num = mod.split()[1]
        resumen = (f'<summary><span class="sn">Módulo {num}</span>'
                   f'<span class="stt">{html.escape(titulo_mod)}</span>'
                   f'<span class="est e-{clase}">{etiqueta}</span>'
                   f'<span class="sc">{conteo[mod]} documentos</span></summary>')
        sid = mod.lower().replace(" ", "-")
        toc.append((sid, f"Módulo {num}"))
        secciones.append(f'<section class="bloque" id="{sid}"><details class="modulo"{abierto}>'
                         f'{resumen}<div class="dentro">{"".join(cuerpo)}</div></details></section>')

    # --- transversales ---
    destacados_base = [
        tarjeta(pathlib.Path("README.md"), "README — puerta de entrada",
                "Qué es este repositorio, cómo está organizado y cuál es el flujo de trabajo.", "md", destacado=True),
        tarjeta(pathlib.Path("CONTRIBUIR.md"), "CONTRIBUIR — cómo aportar",
                "Dónde va cada cosa, nombres de archivo, ficha de autoría y lo que no se hace.", "md", destacado=True),
    ]
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
        primera = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", primera)
        primera = primera.replace("**", "").replace("`", "").replace("*", "")
        tarjetas.append(tarjeta(rel, titulo, primera[:150], "md"))
    sec("transversal", "Base del proyecto y decisiones",
        '<div class="grupo"><div class="docs">' + "".join(destacados_base + tarjetas) + "</div></div>")

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
                '<div class="grupo"><div class="docs">' + "".join(t2) + "</div></div>")

    barra = ('<div class="buscador" role="search">'
             '<input id="q" type="search" placeholder="Buscar por título, tema, autor o ruta…" '
             'aria-label="Buscar documentos" autocomplete="off">'
             '<div class="chips" id="chips">'
             '<button class="chip on" data-f="">Todo</button>'
             '<button class="chip" data-f="tipo:consolidado">Consolidado</button>'
             '<button class="chip" data-f="tipo:oficial">Material oficial</button>'
             '<button class="chip" data-f="tipo:aporte">Aportes</button>'
             '<button class="chip" data-f="autor:danny">Danny</button>'
             '<button class="chip" data-f="autor:camilo">Camilo</button>'
             '<button class="chip" data-f="autor:freddy">Freddy</button>'
             '</div><p class="cuenta" id="cuenta" aria-live="polite"></p></div>')
    vacio_js = '<p class="sinres" id="sinres" hidden>Ningún documento coincide con la búsqueda.</p>'

    toc_html = "".join(f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t in toc)
    cuerpo_total = barra + "".join(secciones) + vacio_js + SCRIPT
    n_html = cuerpo_total.count('<a class="doc')
    dst = RAIZ / "INDICE.html"
    dst.write_text(pagina(
        titulo="Índice del proyecto",
        kicker="Diplomado en Arquitectura de Software y Cloud Computing · Group 2",
        meta=f"{n_html} documentos enlazados · generado el {datetime.now():%d/%m/%Y %H:%M}",
        toc=toc_html,
        cuerpo=cuerpo_total,
        pie="<p>Generado con <code>_Base-Conocimiento/generar-indice.py</code>. "
            "No editar a mano: se regenera. Vuelve a ejecutarlo cada vez que añadas un documento.</p>",
        css_extra=CSS_INDICE), encoding="utf-8")
    print(f"{dst}  ({dst.stat().st_size // 1024} KB · {n_html} documentos · {len(toc)} secciones)")


SCRIPT = """<script>
(function(){
  var q=document.getElementById('q'), chips=document.getElementById('chips'),
      cuenta=document.getElementById('cuenta'), sinres=document.getElementById('sinres');
  var cards=[].slice.call(document.querySelectorAll('a.doc')), filtro='';
  function aplica(){
    var t=q.value.trim().toLowerCase(), activo=t!==''||filtro!=='', vis=0;
    cards.forEach(function(c){
      var ok=(t===''||c.dataset.q.indexOf(t)>-1);
      if(ok&&filtro){var p=filtro.split(':');ok=(c.dataset[p[0]]===p[1]);}
      c.hidden=!ok; if(ok)vis++;
    });
    [].forEach.call(document.querySelectorAll('.grupo'),function(g){
      g.hidden=!g.querySelector('a.doc:not([hidden])');});
    [].forEach.call(document.querySelectorAll('.bloque'),function(b){
      var d=b.querySelector('details.modulo'), hay=!!b.querySelector('a.doc:not([hidden])');
      if(activo&&b.id!=='ahora'){b.hidden=!hay; if(d&&hay)d.open=true;} else {b.hidden=false;}
      if(b.id==='ahora'){b.hidden=activo;}
    });
    cuenta.textContent=activo?(vis+' de '+cards.length+' documentos'):'';
    sinres.hidden=!(activo&&vis===0);
  }
  q.addEventListener('input',aplica);
  chips.addEventListener('click',function(e){
    var b=e.target.closest('.chip'); if(!b)return;
    [].forEach.call(chips.children,function(x){x.classList.remove('on');});
    b.classList.add('on'); filtro=b.dataset.f; aplica();
  });
})();
</script>"""


if __name__ == "__main__":
    main()
