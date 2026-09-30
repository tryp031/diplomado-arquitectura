"""Estilo y armazón HTML compartidos por los generadores del proyecto.

Una sola definición del CSS para que todos los documentos generados —consolidados,
índice— se vean igual. Cada página resultante queda AUTOCONTENIDA: el CSS se inserta
en línea, así un .html se puede enviar suelto por correo o meter en un ZIP sin
romperse.

Lo usan:
    .claude/skills/consolidar-conocimiento/consolidar_html.py
    _Base-Conocimiento/generar-indice.py

Si mueves este archivo, ambos dejan de funcionar: los dos lo localizan subiendo
hasta la raíz del proyecto.
"""

CSS = """
:root{
  --ground:#F1F4F4; --surface:#fff; --surface-2:#E7EDED;
  --ink:#0E2226; --ink-2:#3F5A61; --ink-3:#6E868C;
  --rule:#CDDADC; --rule-2:#E1E9EA;
  --accent:#0A6C7C; --accent-soft:#DBEDEF;
  --signal:#A85B0C; --signal-soft:#F7E8D4;
  --ok:#2B6A4B; --ok-soft:#E2EFE8;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  --serif:Georgia,"Times New Roman",serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color-scheme:light dark;
}
@media (prefers-color-scheme:dark){
  :root{
    --ground:#0A1517; --surface:#101F22; --surface-2:#16292D;
    --ink:#E3EBEC; --ink-2:#A5B9BE; --ink-3:#7C9399;
    --rule:#233A3F; --rule-2:#1A2E32;
    --accent:#5CB9C8; --accent-soft:#123338;
    --signal:#E0A257; --signal-soft:#33240F;
    --ok:#5FB584; --ok-soft:#10261B;
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:var(--serif);font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 90px;
  display:grid;grid-template-columns:1fr;gap:0 48px}
@media (min-width:1040px){.wrap{grid-template-columns:230px minmax(0,1fr)}}
header.mh{grid-column:1/-1;border-bottom:1px solid var(--rule);padding:48px 0 26px;margin-bottom:36px}
.kick{font-family:var(--mono);font-size:.7rem;letter-spacing:.13em;text-transform:uppercase;
  color:var(--accent);margin:0 0 14px}
h1{font-family:var(--sans);font-weight:600;font-size:clamp(1.9rem,4.4vw,2.8rem);
  line-height:1.07;letter-spacing:-.022em;margin:0 0 14px;text-wrap:balance}
.meta{font-family:var(--mono);font-size:.76rem;color:var(--ink-3);margin:0;line-height:1.8}
nav.rail{display:none}
@media (min-width:1040px){
  nav.rail{display:block;align-self:start;position:sticky;top:24px;
    font-family:var(--sans);font-size:.83rem;padding-bottom:40px;
    max-height:calc(100vh - 48px);overflow-y:auto}
}
nav.rail h2{font-family:var(--mono);font-size:.63rem;font-weight:500;letter-spacing:.13em;
  text-transform:uppercase;color:var(--ink-3);margin:0 0 12px;border:none;padding:0}
nav.rail ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:3px}
nav.rail a{display:block;color:var(--ink-2);text-decoration:none;padding:3px 0;line-height:1.35}
nav.rail a:hover{color:var(--accent)}
main{min-width:0}
h2{font-family:var(--sans);font-weight:600;font-size:1.55rem;line-height:1.22;
  letter-spacing:-.016em;margin:52px 0 14px;padding-top:14px;border-top:1px solid var(--rule);
  scroll-margin-top:16px;text-wrap:balance}
h2:first-of-type{border-top:none;padding-top:0;margin-top:0}
h3{font-family:var(--sans);font-weight:600;font-size:1.1rem;margin:32px 0 8px;scroll-margin-top:16px}
h4{font-family:var(--sans);font-weight:600;font-size:.98rem;margin:24px 0 6px}
p{margin:0 0 16px;max-width:72ch}
ul,ol{max-width:70ch;margin:0 0 16px;padding-left:22px}
li{margin-bottom:7px}
strong{font-weight:600;color:var(--ink)}
a{color:var(--accent)}
code{font-family:var(--mono);font-size:.86em;background:var(--surface-2);
  padding:.1em .34em;border-radius:2px}
pre{font-family:var(--mono);font-size:.82rem;line-height:1.65;background:var(--surface);
  border:1px solid var(--rule);border-radius:3px;padding:16px 18px;overflow-x:auto;margin:0 0 20px}
pre code{background:none;padding:0;font-size:1em}
hr{border:none;border-top:1px solid var(--rule-2);margin:36px 0}
blockquote{border-left:3px solid var(--accent);background:var(--surface);
  padding:14px 18px;margin:22px 0;max-width:72ch;border-radius:0 3px 3px 0}
blockquote p{margin:0}
.tw{overflow-x:auto;margin:22px 0;border:1px solid var(--rule);border-radius:3px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-family:var(--sans);font-size:.88rem;line-height:1.5}
th,td{padding:9px 13px;text-align:left;border-bottom:1px solid var(--rule-2);vertical-align:top}
thead th{font-family:var(--mono);font-size:.63rem;font-weight:500;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-3);background:var(--surface-2);white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
.pill{display:inline-block;font-family:var(--mono);font-size:.6rem;font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;padding:.2em .5em;border-radius:2px;
  vertical-align:.12em;white-space:nowrap}
.b-curso{background:var(--accent-soft);color:var(--accent)}
.b-compl{background:var(--surface-2);color:var(--ink-2)}
.b-recom{background:var(--signal-soft);color:var(--signal)}
.b-hipo{background:var(--ok-soft);color:var(--ok)}
footer{grid-column:1/-1;border-top:1px solid var(--rule);margin-top:48px;padding-top:22px;
  font-family:var(--mono);font-size:.74rem;color:var(--ink-3);line-height:1.7}
@media print{nav.rail{display:none} .wrap{grid-template-columns:1fr} body{background:#fff}}
"""

# Extras que solo usa el índice. Van aquí para que el CSS siga teniendo una sola casa.
CSS_INDICE = """
.docs{display:grid;gap:10px;margin:20px 0;grid-template-columns:1fr}
@media (min-width:720px){.docs{grid-template-columns:1fr 1fr}}
a.doc{display:block;background:var(--surface);border:1px solid var(--rule);border-radius:3px;
  padding:15px 17px;text-decoration:none;color:inherit;transition:border-color .12s}
a.doc:hover{border-color:var(--accent)}
a.doc .t{font-family:var(--sans);font-weight:600;font-size:.97rem;line-height:1.35;
  display:block;margin-bottom:5px;color:var(--ink)}
a.doc:hover .t{color:var(--accent)}
a.doc .d{font-family:var(--sans);font-size:.85rem;line-height:1.5;color:var(--ink-2);
  display:block;margin-bottom:9px}
a.doc .f{font-family:var(--mono);font-size:.67rem;color:var(--ink-3);
  display:flex;flex-wrap:wrap;gap:4px 10px;align-items:center}
a.doc.destacado{border-left:3px solid var(--accent)}
a.doc.apagado{opacity:.62}
.tipo{font-family:var(--mono);font-size:.6rem;font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;padding:.2em .5em;border-radius:2px;white-space:nowrap}
.t-consolidado{background:var(--accent-soft);color:var(--accent)}
.t-oficial{background:var(--signal-soft);color:var(--signal)}
.t-aporte{background:var(--surface-2);color:var(--ink-2)}
.t-herramienta{background:var(--ok-soft);color:var(--ok)}
.t-md{background:var(--surface-2);color:var(--ink-3)}
.vacio{font-family:var(--sans);font-size:.9rem;color:var(--ink-3);
  border:1px dashed var(--rule);border-radius:3px;padding:14px 16px;margin:20px 0}

/* --- navegación del índice --- */
[hidden]{display:none!important}
.bloque{margin:0 0 8px}
.bloque>h2{margin-top:40px}
.buscador{position:sticky;top:0;z-index:5;background:var(--ground);
  padding:12px 0 10px;margin:0 0 6px;border-bottom:1px solid var(--rule-2)}
.buscador input{width:100%;font:inherit;font-family:var(--sans);font-size:.95rem;
  padding:11px 14px;color:var(--ink);background:var(--surface);
  border:1px solid var(--rule);border-radius:3px}
.buscador input:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.chip{font-family:var(--mono);font-size:.68rem;letter-spacing:.04em;cursor:pointer;
  color:var(--ink-2);background:var(--surface);border:1px solid var(--rule);
  border-radius:99px;padding:5px 12px}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.cuenta{font-family:var(--mono);font-size:.7rem;color:var(--ink-3);margin:8px 0 0;min-height:1em}
.sinres{font-family:var(--sans);color:var(--ink-3);border:1px dashed var(--rule);
  border-radius:3px;padding:18px;margin:30px 0}

/* --- panel "Ahora" --- */
.ahora{display:grid;gap:22px;background:var(--surface);border:1px solid var(--rule);
  border-left:4px solid var(--accent);border-radius:3px;padding:22px 24px;margin:18px 0 22px}
@media (min-width:860px){.ahora{grid-template-columns:minmax(0,1fr) minmax(0,1.15fr)}}
.ah-k{font-family:var(--mono);font-size:.64rem;letter-spacing:.12em;text-transform:uppercase;
  color:var(--accent);margin:0 0 8px}
.ahora h3{font-size:1.3rem;margin:0 0 14px;line-height:1.25}
.hitos{list-style:none;margin:0;padding:0;font-family:var(--sans);font-size:.88rem}
.hitos li{display:flex;justify-content:space-between;gap:14px;padding:7px 0;
  border-top:1px solid var(--rule-2)}
.hitos li span{color:var(--ink-3)}
.botones{display:flex;flex-direction:column;gap:8px}
a.btn{display:block;font-family:var(--sans);font-weight:600;font-size:.9rem;line-height:1.3;
  text-decoration:none;color:var(--ink);background:var(--accent-soft);
  border:1px solid transparent;border-radius:3px;padding:11px 14px}
a.btn:hover{border-color:var(--accent);color:var(--accent)}

/* --- tira de módulos --- */
.modulos{display:grid;gap:10px;grid-template-columns:1fr}
@media (min-width:640px){.modulos{grid-template-columns:repeat(2,1fr)}}
@media (min-width:1100px){.modulos{grid-template-columns:repeat(5,1fr)}}
.mod{display:flex;flex-direction:column;gap:4px;background:var(--surface);
  border:1px solid var(--rule);border-radius:3px;padding:13px 14px;
  text-decoration:none;color:inherit;font-family:var(--sans)}
a.mod:hover{border-color:var(--accent)}
.mod.m-curso{border-color:var(--accent);box-shadow:inset 0 3px 0 var(--accent)}
.mod.m-proximo{opacity:.6}
.mn{font-family:var(--mono);font-size:.62rem;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-3)}
.mt{font-weight:600;font-size:.88rem;line-height:1.3;color:var(--ink);min-height:2.3em}
.mf{font-family:var(--mono);font-size:.68rem;color:var(--ink-3)}
.me{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;margin-top:5px;
  font-family:var(--mono);font-size:.64rem;color:var(--ink-3)}
.est{font-family:var(--mono);font-size:.58rem;font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;padding:.2em .55em;border-radius:2px;white-space:nowrap}
.e-curso{background:var(--accent);color:#fff}
.e-cerrado{background:var(--surface-2);color:var(--ink-2)}
.e-proximo{background:var(--signal-soft);color:var(--signal)}

/* --- módulos plegables --- */
details.modulo{border:1px solid var(--rule);border-radius:3px;background:var(--surface);margin:14px 0}
details.modulo>summary{list-style:none;cursor:pointer;display:flex;flex-wrap:wrap;align-items:baseline;
  gap:6px 14px;padding:16px 20px;font-family:var(--sans)}
details.modulo>summary::-webkit-details-marker{display:none}
details.modulo>summary::before{content:"▸";color:var(--accent);font-size:.9rem;
  transition:transform .12s;display:inline-block}
details.modulo[open]>summary::before{transform:rotate(90deg)}
details.modulo>summary:hover .stt{color:var(--accent)}
details.modulo[open]>summary{border-bottom:1px solid var(--rule-2)}
.sn{font-family:var(--mono);font-size:.7rem;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-3)}
.stt{font-weight:600;font-size:1.12rem;letter-spacing:-.01em;flex:1 1 240px}
.sc{font-family:var(--mono);font-size:.68rem;color:var(--ink-3)}
.dentro{padding:4px 20px 18px}
.grupo h3{font-family:var(--mono);font-size:.68rem;font-weight:500;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-3);margin:26px 0 0;
  border-bottom:1px solid var(--rule-2);padding-bottom:7px}
.grupo .docs{margin-top:14px}
a.doc .autor{color:var(--accent);font-weight:600}
a.doc{min-width:0;overflow-wrap:anywhere}
.docs>*{min-width:0}
"""


def pagina(titulo, kicker, meta, toc, cuerpo, pie, css_extra=""):
    """Devuelve el HTML completo y autocontenido de una página del proyecto."""
    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{titulo}</title>
<style>{CSS}{css_extra}</style>
</head><body>
<div class="wrap">
<header class="mh">
  <p class="kick">{kicker}</p>
  <h1>{titulo}</h1>
  <p class="meta">{meta}</p>
</header>
<nav class="rail" aria-label="Contenido"><h2>Contenido</h2><ol>{toc}</ol></nav>
<main>{cuerpo}</main>
<footer>{pie}</footer>
</div></body></html>
"""
