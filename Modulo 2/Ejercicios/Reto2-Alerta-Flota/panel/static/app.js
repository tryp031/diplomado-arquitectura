// Panel Reto 2. Consulta /api/estado cada segundo y pinta. Todo dato que viene de los
// eventos (placas, errores) es NO confiable: se inserta con textContent, nunca con innerHTML.

const INTERVALO_MS = 1000;
const ACTIVO_S = 2.5;
const RATE = 15;
const ZONA = "America/Bogota";

const $ = (sel) => document.querySelector(sel);
const fmtNum = new Intl.NumberFormat("es-CO");
const fmtSeg = new Intl.NumberFormat("es-CO", { minimumFractionDigits: 3, maximumFractionDigits: 3 });
const fmtHora = new Intl.DateTimeFormat("es-CO", {
  timeZone: ZONA, hour: "2-digit", minute: "2-digit", second: "2-digit", fractionalSecondDigits: 3, hour12: false,
});
const fmtFecha = new Intl.DateTimeFormat("es-CO", { timeZone: ZONA, day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false });
const fmtHoraCorta = new Intl.DateTimeFormat("es-CO", { timeZone: ZONA, hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });

// Nombre visible de cada modo de carga: el panel debe dejar claro qué k6 está corriendo.
const NOMBRE_MODO = { rafaga: "ráfaga", ritmo: "ritmo de referencia", profesor: "k6 del profesor" };
const AYUDA_MODO = {
  profesor: "Script oficial del profesor (k6/profesor.js), solo con la URL hacia nuestro gateway. "
    + "10 VUs · 1000 iteraciones · pausa 0,1 s. Él decide cuántos Emergency manda: normalmente 1, a veces 0 o 2.",
  rafaga: "Script propio (k6/carga.js) sin pausas: las 1000 peticiones llegan en menos de 1 s.",
  ritmo: "Script propio (k6/carga.js) a ~35 req/s durante ~28 s, como la salida de referencia del enunciado.",
};

function el(tag, props = {}, ...hijos) {
  const nodo = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "dataset") Object.assign(nodo.dataset, v);
    else if (k === "className") nodo.className = v;
    else nodo.setAttribute(k, v);
  }
  for (const h of hijos) if (h !== null && h !== undefined) nodo.append(h instanceof Node ? h : document.createTextNode(String(h)));
  return nodo;
}
const svgEl = (tag, attrs = {}) => {
  const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
};
const hora = (iso) => (iso ? fmtHora.format(new Date(iso)) : "—");
const num = (n) => (n === null || n === undefined ? "—" : fmtNum.format(n));

let ultimoEstado = null;
let proximaCorrida = 1;
const descargando = new Set();  // "n-formato" de las descargas en curso: su botón sigue deshabilitado

// ------------------------------------------------------------------ ciclo de consulta
async function ciclo() {
  try {
    const r = await fetch("/api/estado", { cache: "no-store" });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    ultimoEstado = await r.json();
    $("#aviso-conexion").hidden = true;
    pintar(ultimoEstado);
  } catch {
    $("#aviso-conexion").hidden = false;
    fijarPildora($("#salud"), "critical", "Panel sin conexión");
  } finally {
    setTimeout(ciclo, INTERVALO_MS);
  }
}

function pintar(e) {
  const ahora = e.serie.length ? e.serie[e.serie.length - 1].t : Date.now() / 1000;
  pintarSalud(e);
  pintarCorrida(e);
  pintarMedida(e.medida_rubrica, e.corrida);
  pintarKpis(e);
  pintarSegundaMedida(e);
  pintarLinea(e);
  pintarConsola(e.k6);
  pintarHistorial(e.historial, e.corrida);
  pintarFlujo(e, ahora);
  pintarAcciones(e);
  pintarGrafica(e.serie);
  pintarEmergencias(e.emergencias);
  pintarFeed(e.feed);
  $("#actualizado").textContent = `Actualizado ${fmtHoraCorta.format(new Date())}`;
}

function fijarPildora(nodo, nivel, texto) {
  nodo.dataset.nivel = nivel;
  nodo.querySelector("span:last-child").textContent = texto;
}

// ------------------------------------------------------------------ salud general
const ESENCIALES = ["gateway-1", "ingest-1", "ingest-2", "notifier-1", "redis-1"];
function pintarSalud(e) {
  if (e.docker_error) return fijarPildora($("#salud"), "warning", "Sin acceso a Docker");
  const caidos = ESENCIALES.filter((c) => e.contenedores[c]?.estado !== "running");
  if (caidos.length) return fijarPildora($("#salud"), "critical", `${caidos.length} componente${caidos.length > 1 ? "s" : ""} detenido${caidos.length > 1 ? "s" : ""}`);
  if (!e.redis.ok) return fijarPildora($("#salud"), "critical", "Redis no responde");
  fijarPildora($("#salud"), "good", "Sistema operativo");
}

// ------------------------------------------------------------------ medida de la rúbrica
const NIVELES = {
  good: { icono: "✓", texto: "< 15 s · 2,5 pts" },
  warning: { icono: "!", texto: "15–45 s · 1,5 pts" },
  critical: { icono: "✕", texto: "> 45 s · 0,5 pts" },
};
function pintarMedida(m, corrida) {
  const marca = $("#escala-marca");
  const estado = $("#medida-estado");
  const neutro = (texto) => {
    $("#medida-valor").textContent = "—";
    estado.dataset.nivel = "neutral";
    estado.querySelector(".estado-icono").textContent = "•";
    $("#medida-texto").textContent = texto;
    marca.hidden = true;
  };
  // La medida pertenece a una corrida. Mientras k6 envía, la "última petición" todavía no existe.
  if (!corrida) return neutro("Lanza una corrida para medir");
  if (!corrida.fin) return neutro("Corrida en curso: la medida se fija cuando k6 termina");
  if (m.segundos === null) return neutro("Sin correos de esta corrida todavía");
  const efectivo = Math.max(m.segundos, 0);
  $("#medida-valor").textContent = fmtSeg.format(efectivo);
  const n = NIVELES[m.nivel];
  estado.dataset.nivel = m.nivel;
  estado.querySelector(".estado-icono").textContent = n.icono;
  $("#medida-texto").textContent = m.segundos < 0 ? `${n.texto} · el correo salió antes de la última petición` : n.texto;
  marca.hidden = false;
  marca.style.left = `${(Math.min(efectivo, 60) / 60) * 100}%`;
}

// ------------------------------------------------------------------ Emergency → correo
const CRITERIO_PROFESOR_S = 16;  // reportado por Freddy (06/10); la rúbrica escrita dice 15 s
function pintarSegundaMedida(e) {
  const peor = e.emergencia_a_correo;
  const valor = $("#e2c-valor");
  if (!e.corrida || peor.segundos === null) {
    valor.textContent = "—";
    delete valor.dataset.nivel;
    $("#e2c-detalle").textContent = "peor caso · criterio reportado < 16 s";
    return;
  }
  valor.textContent = `${fmtSeg.format(peor.segundos)} s`;
  valor.dataset.nivel = peor.segundos < CRITERIO_PROFESOR_S ? "good" : "critical";
  $("#e2c-detalle").textContent = `peor caso (${peor.placa}) · criterio < 16 s`;
}

// ------------------------------------------------------------------ salida de k6
// El texto completo viaja por /api/k6/salida, y solo cuando cambia la cantidad de líneas.
let lineasMostradas = -1;
let inicioMostrado = null;
let pidiendoSalida = false;
function pintarConsola(k6) {
  const estado = { corriendo: "corriendo", terminado: "terminada", fallido: `falló (código ${k6.codigo})` }[k6.estado] ?? "sin carga todavía";
  const modo = k6.modo ? `${NOMBRE_MODO[k6.modo] ?? k6.modo} · ` : "";
  $("#k6-resumen").textContent = `· ${modo}${estado} · ${num(k6.lineas)} líneas`;
  $("#k6-estado-consola").textContent = k6.inicio ? `Inicio ${hora(k6.inicio)}${k6.fin ? ` · fin ${hora(k6.fin)}` : ""}` : "";
  if (pidiendoSalida || (k6.lineas === lineasMostradas && k6.inicio === inicioMostrado)) return;
  pidiendoSalida = true;
  fetch("/api/k6/salida", { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
    .then(({ lineas }) => {
      const consola = $("#k6-salida");
      const alFinal = consola.scrollHeight - consola.scrollTop - consola.clientHeight < 24;
      consola.textContent = lineas.join("\n");
      if (alFinal || k6.inicio !== inicioMostrado) consola.scrollTop = consola.scrollHeight;  // no arrastra a quien lee arriba
      lineasMostradas = k6.lineas;
      inicioMostrado = k6.inicio;
    })
    .catch(() => { /* se reintenta en el próximo ciclo */ })
    .finally(() => { pidiendoSalida = false; });
}

$("#k6-ajustar").addEventListener("change", (ev) => $("#k6-salida").classList.toggle("ajustada", ev.currentTarget.checked));
$("#k6-copiar").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText($("#k6-salida").textContent);
    avisar("Salida de k6 copiada al portapapeles.");
  } catch {
    avisar("El navegador no permitió copiar: seleccione el texto y use Cmd/Ctrl+C.");
  }
});
$("#k6-descargar").addEventListener("click", () => {
  const url = URL.createObjectURL(new Blob([$("#k6-salida").textContent + "\n"], { type: "text/plain;charset=utf-8" }));
  const n = ultimoEstado?.corrida?.n;
  el("a", { href: url, download: n ? `k6-corrida-${n}.txt` : "k6-salida.txt" }).click();
  URL.revokeObjectURL(url);
});

// ------------------------------------------------------------------ borrar datos
const dialogo = $("#dialogo-limpiar");
$("#btn-limpiar").addEventListener("click", () => { dialogo.returnValue = ""; dialogo.showModal(); });
dialogo.addEventListener("close", async () => {
  if (dialogo.returnValue !== "borrar") return;
  try {
    await post("/api/datos/limpiar");
    lineasMostradas = -1;
    avisar("Datos borrados. La próxima es la corrida #1, con data limpia.");
  } catch (err) {
    avisar(`No se pudieron borrar los datos: ${err.message}`);
  }
});

// ------------------------------------------------------------------ corrida actual
function pintarCorrida(e) {
  const c = e.corrida;
  if (!c) {
    $("#corrida-titulo").textContent = "Sin corrida";
    $("#corrida-horas").textContent = "los contadores muestran todo lo registrado";
    return;
  }
  $("#corrida-titulo").textContent = `Corrida #${c.n} · ${NOMBRE_MODO[c.modo] ?? c.modo}`;
  const inicio = fmtHoraCorta.format(new Date(c.inicio));
  $("#corrida-horas").textContent = c.fin ? `${inicio} → ${fmtHoraCorta.format(new Date(c.fin))}` : `${inicio} → en curso`;
}

// ------------------------------------------------------------------ línea de tiempo (SVG propio)
// Tres filas rotuladas sobre el mismo eje de tiempo: la carga de k6, cuándo entró cada Emergency y
// cuándo salió su correo. Una línea vertical une cada Emergency con su correo. Abajo, el tramo que
// mide la rúbrica en números, porque a la escala de la carga (~30 s) unos milisegundos no se ven.
function pintarLinea(e) {
  const c = e.corrida;
  const visible = Boolean(c && e.ultima_peticion);
  $("#linea-cuerpo").hidden = !visible;
  $("#linea-vacio").hidden = visible;
  $("#linea-vacio").textContent = c ? "Esperando la primera petición de la corrida…" : "Lanza una corrida para ver su línea de tiempo.";
  if (!visible) return;

  const svg = $("#linea-svg");
  const t0 = new Date(c.inicio).getTime();
  const ultima = new Date(e.ultima_peticion).getTime();
  const emergencias = e.emergencias.filter((em) => em.en_corrida).map((em) => {
    const recibida = new Date(em.recibida).getTime();
    return { ...em, t: recibida, correo: em.ms_envio === null ? null : recibida + em.ms_envio };
  });
  const correos = emergencias.filter((em) => em.correo !== null).map((em) => em.correo);
  const ultimoCorreo = correos.length ? Math.max(...correos) : null;
  const tFin = Math.max(ultima, ultimoCorreo ?? 0, c.fin ? new Date(c.fin).getTime() : Date.now());

  const ancho = svg.clientWidth || 640;
  const etiquetas = ancho < 520 ? 92 : 130;
  const m = { izq: etiquetas, der: 12 };
  const w = ancho - m.izq - m.der;
  const x = (t) => m.izq + ((t - t0) / Math.max(tFin - t0, 1)) * w;
  const filas = { carga: 24, emergencia: 64, correo: 104 };
  const alto = 146;
  svg.setAttribute("viewBox", `0 0 ${ancho} ${alto}`);
  svg.replaceChildren();
  const texto = (contenido, attrs) => { const t = svgEl("text", attrs); t.textContent = contenido; svg.append(t); return t; };
  const conTitulo = (nodo, titulo) => { const t = svgEl("title"); t.textContent = titulo; nodo.append(t); svg.append(nodo); };

  for (const [clave, rotulo] of [["carga", "Peticiones k6"], ["emergencia", "Emergency recibido"], ["correo", "Correo enviado"]]) {
    svg.append(svgEl("line", { class: "carril", x1: m.izq, x2: m.izq + w, y1: filas[clave], y2: filas[clave] }));
    texto(rotulo, { class: "rotulo", x: 0, y: filas[clave] + 4 });
  }
  const duracion = (ultima - t0) / 1000;
  conTitulo(svgEl("rect", { class: "carga", x: m.izq, y: filas.carga - 9, width: Math.max(x(ultima) - m.izq, 2), height: 18, rx: 5 }),
    `k6 envió ${num(e.http.total)} peticiones en ${fmtNum.format(Math.round(duracion * 10) / 10)} s`);
  texto(`${num(e.http.total)} en ${fmtNum.format(Math.round(duracion * 10) / 10)} s`, { class: "dentro", x: m.izq + 8, y: filas.carga + 4 });

  for (const em of emergencias) {
    if (em.correo !== null) svg.append(svgEl("line", { class: "union", x1: x(em.t), x2: x(em.correo), y1: filas.emergencia, y2: filas.correo }));
  }
  for (const em of emergencias) {
    const detalle = `${em.placa} · recibido ${hora(em.recibida)}${em.ms_envio === null ? " · correo pendiente" : ` · correo +${num(em.ms_envio)} ms`}`;
    conTitulo(svgEl("circle", { class: "hito", cx: x(em.t), cy: filas.emergencia, r: 5, style: "stroke:var(--serie-2)" }), detalle);
    if (em.correo !== null) conTitulo(svgEl("circle", { class: "hito", cx: x(em.correo), cy: filas.correo, r: 5, style: "stroke:var(--good)" }), detalle);
  }
  svg.append(svgEl("line", { class: "guia", x1: x(ultima), x2: x(ultima), y1: filas.carga - 12, y2: filas.correo + 10 }));
  conTitulo(svgEl("circle", { class: "hito", cx: x(ultima), cy: filas.carga, r: 6, style: "stroke:var(--serie-1)" }), `Última petición ${hora(e.ultima_peticion)}`);
  texto(fmtHoraCorta.format(new Date(t0)), { class: "eje-texto", x: m.izq, y: alto - 4 });
  texto(fmtHoraCorta.format(new Date(tFin)), { class: "eje-texto", x: m.izq + w, y: alto - 4, "text-anchor": "end" });
  svg.setAttribute("aria-label", `Corrida #${c.n}: ${emergencias.length} Emergency, ${correos.length} correos, carga de ${fmtNum.format(Math.round(duracion))} s`);

  $("#tramo-desde").textContent = hora(e.ultima_peticion);
  $("#tramo-hasta").textContent = ultimoCorreo === null ? "pendiente" : hora(new Date(ultimoCorreo).toISOString());
  $("#tramo-valor").textContent = e.medida_rubrica.segundos === null ? "—" : `${fmtSeg.format(Math.max(e.medida_rubrica.segundos, 0))} s`;
}

// ------------------------------------------------------------------ historial de corridas
const NOMBRE_CORTO_MODO = { rafaga: "ráfaga", ritmo: "ritmo", profesor: "profesor" };
function pintarHistorial(lista, actual) {
  $("#historial-vacio").hidden = lista.length > 0;
  $("#historial").replaceChildren(...lista.map((c) => {
    const medida = c.medida?.segundos ?? null;
    const boton = (formato) => el("button", {
      className: "btn btn-chico", type: "button", dataset: { n: c.n, formato },
      ...(!c.fin || descargando.has(`${c.n}-${formato}`) ? { disabled: "" } : {}),
    }, `.${formato}`);
    const duracion = c.fin ? (new Date(c.fin) - new Date(c.inicio)) / 1000 : null;
    return el("tr", c.n === actual?.n ? { className: "actual" } : {},
      el("td", {}, c.n),
      el("td", { title: hora(c.inicio) }, fmtFecha.format(new Date(c.inicio))),
      el("td", {}, NOMBRE_CORTO_MODO[c.modo] ?? c.modo),
      el("td", {}, nombreSmtp(c.smtp) === "mailpit" ? "Mailpit" : nombreSmtp(c.smtp)),
      el("td", { class: "num" }, duracion === null ? "—" : `${fmtNum.format(Math.round(duracion * 10) / 10)} s`),
      el("td", { class: "num" }, num(c.procesados)),
      el("td", { class: "num" }, num(c.emergencias)),
      el("td", { class: "num" }, num(c.rechazadas_429)),
      el("td", { class: "num" }, !c.fin ? "en curso" : medida === null ? "—" : `${fmtSeg.format(Math.max(medida, 0))} s`),
      el("td", { class: "num" }, c.emergencia_a_correo == null ? "—" : `${fmtSeg.format(c.emergencia_a_correo)} s`),
      el("td", {}, c.medida?.nivel ? el("span", { className: "insignia", dataset: { nivel: c.medida.nivel } }, fmtNum.format(c.medida.puntos)) : "—"),
      el("td", { className: "acciones-fila" }, boton("log"), boton("csv")),
    );
  }));
}

// ------------------------------------------------------------------ KPIs
function pintarKpis(e) {
  $("#kpi-aceptadas").textContent = num(e.http.aceptadas);
  $("#kpi-aceptadas-pie").textContent = `de ${num(e.http.total)} recibidas por el gateway${e.http.otros_errores ? ` · ${num(e.http.otros_errores)} otros errores` : ""}`;
  $("#kpi-429").textContent = num(e.http.rechazadas_429);
  $("#kpi-enviadas").textContent = num(e.eventos.enviadas);
  $("#kpi-emergencias").textContent = num(e.eventos.emergencias);
  $("#kpi-emergencias-pie").textContent = [`${num(e.eventos.reintentos)} reintentos`, e.eventos.dlq && `${num(e.eventos.dlq)} en DLQ`, e.eventos.fallidas && `${num(e.eventos.fallidas)} sin encolar`].filter(Boolean).join(" · ");
  $("#kpi-procesados").textContent = num(e.eventos.procesados);
  $("#kpi-pendientes").textContent = e.redis.ok ? num(e.redis.pendientes) : "—";
  $("#kpi-cola-pie").textContent = e.redis.ok ? `pendientes sin ACK · DLQ ${num(e.redis.dlq)}` : "Redis no responde";
}

// ------------------------------------------------------------------ arquitectura viva
function reciente(iso, ahora) {
  return iso && ahora - new Date(iso).getTime() / 1000 <= ACTIVO_S;
}
function saludDe(e, ...contenedores) {
  if (e.docker_error) return "neutral";
  const estados = contenedores.map((c) => e.contenedores[c]?.estado);
  if (estados.every((s) => s === undefined)) return "neutral";
  return estados.every((s) => s === "running") ? "good" : "critical";
}
function pintarFlujo(e, ahora) {
  const nodos = {
    k6: { activo: e.k6.estado === "corriendo", salud: e.k6.estado === "fallido" ? "critical" : "neutral",
          dato: e.k6.estado === "corriendo" ? `Corriendo · ${NOMBRE_MODO[e.k6.modo] ?? e.k6.modo}` : e.k6.estado === "terminado" ? "Última carga terminada" : "En espera" },
    gateway: { activo: reciente(e.ultimo_visto.gateway, ahora), salud: saludDe(e, "gateway-1"),
               dato: `${num(e.http.total)} peticiones · ${num(e.http.rechazadas_429)} × 429` },
    ingest: { activo: reciente(e.ultimo_visto.ingest, ahora), salud: saludDe(e, "ingest-1", "ingest-2") },
    redis: { activo: reciente(e.ultimo_visto.ingest, ahora) && e.eventos.emergencias > 0, salud: e.redis.ok ? "good" : "critical",
             dato: e.redis.ok ? `Pend. ${num(e.redis.pendientes)} · DLQ ${num(e.redis.dlq)}` : "No responde" },
    notifier: { activo: reciente(e.ultimo_visto.notifier, ahora), salud: saludDe(e, "notifier-1"),
                dato: `${num(e.eventos.enviadas)} enviados · ${num(e.eventos.reintentos)} reintentos` },
    mailpit: { activo: reciente(e.ultimo_visto.notifier, ahora) && e.eventos.enviadas > 0,
               salud: e.smtp.local ? saludDe(e, "mailpit-1") : "neutral",
               dato: `${num(e.eventos.enviadas)} correos` },
  };
  for (const [clave, n] of Object.entries(nodos)) {
    const nodo = document.querySelector(`[data-nodo="${clave}"]`);
    nodo.classList.toggle("activo", Boolean(n.activo));
    nodo.classList.toggle("caido", n.salud === "critical");
    nodo.dataset.salud = n.salud;
    const dato = nodo.querySelector(".nodo-dato");
    if (dato) dato.textContent = n.dato;
  }
  $("#smtp-rol").textContent = e.smtp.local ? "Mailpit (desarrollo)" : `${nombreSmtp(e.smtp.host)} (externo)`;
  const replicas = $('[data-dato="replicas"]');
  const filas = Object.entries(e.por_replica).sort();
  replicas.replaceChildren(...(filas.length
    ? filas.map(([nombre, n]) => el("li", {}, el("span", { title: nombre }, nombre.replace("ingest-", "")), el("span", {}, num(n))))
    : [el("li", {}, el("span", {}, "sin tráfico"), el("span", {}, "—"))]));
}

// ------------------------------------------------------------------ acciones
function pintarAcciones(e) {
  const corriendo = e.k6.estado === "corriendo";
  $("#btn-carga").disabled = corriendo;
  $("#btn-limpiar").disabled = corriendo;
  $("#btn-limpiar").title = corriendo ? "Espere a que termine la carga" : "Borra historial, logs y colas para empezar con data limpia";
  proximaCorrida = (e.historial[0]?.n ?? 0) + 1;
  $("#btn-carga").textContent = corriendo ? `Corrida #${e.corrida?.n ?? ""} en curso…` : textoBotonCarga();
  const nivelK6 = { corriendo: "activo", terminado: "good", fallido: "critical" }[e.k6.estado] ?? "neutral";
  const textoK6 = { corriendo: `Corriendo (${NOMBRE_MODO[e.k6.modo] ?? e.k6.modo})`, terminado: `Terminada (${NOMBRE_MODO[e.k6.modo] ?? e.k6.modo})`, fallido: `Falló (código ${e.k6.codigo})` }[e.k6.estado] ?? "Inactivo";
  fijarPildora($("#k6-estado"), nivelK6, textoK6);
  for (const fila of document.querySelectorAll("#fallas li")) {
    const contenedor = e.contenedores[`${fila.dataset.servicio}-1`];
    const estado = fila.querySelector(".falla-estado");
    const boton = fila.querySelector("button");
    if (fila.dataset.servicio === "mailpit" && !e.smtp.local) {
      // En modo Gmail el SMTP es externo: Mailpit no participa y apagarlo no simularía nada.
      $("#smtp-nombre").textContent = `(${nombreSmtp(e.smtp.host)})`;
      estado.textContent = "Externo";
      estado.dataset.nivel = "neutral";
      boton.textContent = "—";
      boton.disabled = true;
      boton.title = "Es un servicio externo: no se puede apagar desde el panel. Para probar la caída del SMTP, use el modo dev (Mailpit).";
      continue;
    }
    if (fila.dataset.servicio === "mailpit") {
      $("#smtp-nombre").textContent = "(Mailpit)";
      boton.title = "";
    }
    if (!contenedor) {
      estado.textContent = e.docker_error ? "sin Docker" : "no levantado";
      estado.dataset.nivel = "neutral";
      boton.textContent = "—";
      boton.disabled = true;
      continue;
    }
    const enMarcha = contenedor.estado === "running";
    estado.textContent = enMarcha ? "En marcha" : "Detenido";
    estado.dataset.nivel = enMarcha ? "good" : "critical";
    if (!boton.dataset.ocupado) {
      boton.textContent = enMarcha ? "Apagar" : "Encender";
      boton.disabled = false;
      boton.dataset.accion = enMarcha ? "apagar" : "encender";
    }
  }
}

function avisar(texto) {
  $("#mensaje").textContent = texto;
}

async function post(url, cuerpo) {
  const r = await fetch(url, {
    method: "POST",
    headers: cuerpo ? { "Content-Type": "application/json" } : {},
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(datos.error || datos.detail || `HTTP ${r.status}`);
  return datos;
}

$("#btn-emergencia").addEventListener("click", async (ev) => {
  const boton = ev.currentTarget;
  boton.disabled = true;
  try {
    const d = await post("/api/emergencia");
    const corrida = ultimoEstado?.corrida?.n;
    const efecto = corrida
      ? `No altera la corrida #${corrida}: aparece en «Recorrido de cada emergencia» marcada «fuera de corrida».`
      : "Aparece en «Recorrido de cada emergencia» y en los eventos del sistema.";
    avisar(`Emergency ${d.placa} enviada por el gateway → HTTP ${d.status_gateway}. ${efecto}`);
  } catch (err) {
    avisar(`No se pudo enviar: ${err.message}`);
  } finally {
    boton.disabled = false;
  }
});

// Los botones del historial se repintan cada segundo: el clic se escucha en la tabla.
$("#historial").addEventListener("click", async (ev) => {
  const boton = ev.target.closest("button[data-formato]");
  if (!boton || boton.disabled) return;
  const { n, formato } = boton.dataset;
  descargando.add(`${n}-${formato}`);
  boton.disabled = true;
  try {
    const r = await fetch(`/api/corridas/${n}/logs?formato=${formato}`);
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || `HTTP ${r.status}`);
    const nombre = /filename="([^"]+)"/.exec(r.headers.get("Content-Disposition") ?? "")?.[1] ?? `corrida-${n}.${formato}`;
    const url = URL.createObjectURL(await r.blob());
    el("a", { href: url, download: nombre }).click();
    URL.revokeObjectURL(url);
    avisar(`Descargado ${nombre}.`);
  } catch (err) {
    avisar(`No se pudieron descargar los logs: ${err.message}`);
  } finally {
    descargando.delete(`${n}-${formato}`);
  }
});

$("#btn-carga").addEventListener("click", async () => {
  const modo = modoElegido();
  const profesor = modo === "profesor";
  const emergencias = Number($("#emergencias").value);
  try {
    const d = await post("/api/carga", profesor ? { modo } : { modo, emergencias });
    const detalle = profesor ? "k6/profesor.js decide los Emergency" : `${emergencias} Emergency`;
    avisar(`Corrida #${d.corrida} lanzada con ${NOMBRE_MODO[modo]} (${detalle}). Solo cuenta lo que entra mientras k6 envía.`);
  } catch (err) {
    avisar(`No se pudo lanzar la carga: ${err.message}`);
  }
});

$("#fallas").addEventListener("click", async (ev) => {
  const boton = ev.target.closest("button");
  if (!boton || boton.disabled) return;
  const servicio = boton.closest("li").dataset.servicio;
  const accion = boton.dataset.accion;
  boton.dataset.ocupado = "1";
  boton.disabled = true;
  boton.textContent = accion === "apagar" ? "Apagando…" : "Encendiendo…";
  try {
    await post(`/api/servicios/${servicio}/${accion}`);
    avisar(`${servicio}: ${accion === "apagar" ? "apagado" : "encendido"}.`);
  } catch (err) {
    avisar(`No se pudo ${accion} ${servicio}: ${err.message}`);
  } finally {
    delete boton.dataset.ocupado;
  }
});

// ------------------------------------------------------------------ tema
(function tema() {
  const raiz = document.documentElement;
  try {
    const guardado = localStorage.getItem("panel-tema");
    if (guardado) raiz.dataset.theme = guardado;
  } catch { /* sin almacenamiento: se usa el del sistema */ }
  $("#btn-tema").addEventListener("click", () => {
    const oscuro = raiz.dataset.theme ? raiz.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    raiz.dataset.theme = oscuro ? "light" : "dark";
    try { localStorage.setItem("panel-tema", raiz.dataset.theme); } catch { /* ignorar */ }
    if (ultimoEstado) { pintarGrafica(ultimoEstado.serie); pintarLinea(ultimoEstado); }
  });
})();

// ------------------------------------------------------------------ gráfica (SVG propio)
let indiceHover = null;

function maximoRedondo(v) {
  const paso = 10 ** Math.floor(Math.log10(v));
  for (const m of [1, 2, 2.5, 5, 10]) if (m * paso >= v) return m * paso;
  return 10 * paso;
}

function barraRedondeada(x, y, w, h, r) {
  if (h <= 0) return "";
  r = Math.min(r, w / 2, h);
  return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
}

function pintarGrafica(serie) {
  const svg = $("#grafica-svg");
  const ancho = svg.clientWidth || 800;
  const alto = svg.clientHeight || 240;
  const m = { izq: 44, der: 64, arr: 10, aba: 24 };
  const w = ancho - m.izq - m.der;
  const h = alto - m.arr - m.aba;
  const maxDato = Math.max(...serie.map((p) => p.aceptadas + p.rechazadas), 0);
  const yMax = maximoRedondo(Math.max(RATE * 1.6, maxDato));
  const y = (v) => m.arr + h - (v / yMax) * h;
  const paso = w / serie.length;
  const anchoBarra = Math.max(paso - 2, 1);

  svg.setAttribute("viewBox", `0 0 ${ancho} ${alto}`);
  svg.replaceChildren();

  for (let i = 0; i <= 4; i++) {
    const v = (yMax / 4) * i;
    svg.append(svgEl("line", { class: i === 0 ? "base" : "rejilla", x1: m.izq, x2: m.izq + w, y1: y(v), y2: y(v) }));
    const t = svgEl("text", { class: "tick", x: m.izq - 8, y: y(v) + 4, "text-anchor": "end" });
    t.textContent = fmtNum.format(v);
    svg.append(t);
  }
  serie.forEach((p, i) => {
    const desde = serie.length - 1 - i;
    if (desde % 10 === 0) {
      const t = svgEl("text", { class: "tick", x: m.izq + i * paso + paso / 2, y: alto - 6, "text-anchor": "middle" });
      t.textContent = desde === 0 ? "ahora" : `−${desde} s`;
      svg.append(t);
    }
  });

  serie.forEach((p, i) => {
    const x = m.izq + i * paso + (paso - anchoBarra) / 2;
    const alturaA = h * (p.aceptadas / yMax);
    const alturaR = h * (p.rechazadas / yMax);
    const opacidad = indiceHover === null || indiceHover === i ? 1 : 0.45;
    if (p.aceptadas) {
      svg.append(svgEl("path", { class: "barra-1", opacity: opacidad,
        d: barraRedondeada(x, y(p.aceptadas), anchoBarra, alturaA, p.rechazadas ? 0 : 4) }));
    }
    if (p.rechazadas) {
      const base = y(p.aceptadas) - (p.aceptadas ? 2 : 0);  // 2 px de superficie entre segmentos
      svg.append(svgEl("path", { class: "barra-2", opacity: opacidad, d: barraRedondeada(x, base - alturaR, anchoBarra, alturaR, 4) }));
    }
  });

  svg.append(svgEl("line", { class: "rate", x1: m.izq, x2: m.izq + w, y1: y(RATE), y2: y(RATE) }));
  const etiqueta = svgEl("text", { class: "rate-etiqueta", x: m.izq + w + 6, y: y(RATE) + 4 });
  etiqueta.textContent = "15 r/s";
  svg.append(etiqueta);

  if (indiceHover !== null) {
    const cx = m.izq + indiceHover * paso + paso / 2;
    svg.append(svgEl("line", { class: "cursor", x1: cx, x2: cx, y1: m.arr, y2: m.arr + h }));
  }
  const zona = svgEl("rect", { class: "zona", x: m.izq, y: m.arr, width: w, height: h });
  const mover = (ev) => {
    const caja = svg.getBoundingClientRect();
    const i = Math.min(serie.length - 1, Math.max(0, Math.floor((ev.clientX - caja.left - m.izq * (caja.width / ancho)) / (paso * (caja.width / ancho)))));
    if (i !== indiceHover) { indiceHover = i; pintarGrafica(serie); }
    mostrarTooltip(serie[i], (m.izq + i * paso + paso / 2) * (caja.width / ancho), caja.width);
  };
  zona.addEventListener("pointermove", mover);
  zona.addEventListener("pointerleave", () => { indiceHover = null; $("#grafica-tooltip").hidden = true; pintarGrafica(serie); });
  svg.append(zona);
  if (indiceHover !== null) mostrarTooltip(serie[indiceHover], null, null);

  const filas = serie.filter((p) => p.aceptadas || p.rechazadas);
  $("#grafica-tabla").replaceChildren(...(filas.length
    ? filas.map((p) => el("tr", {}, el("td", {}, fmtHoraCorta.format(new Date(p.t * 1000))), el("td", { class: "num" }, num(p.aceptadas)), el("td", { class: "num" }, num(p.rechazadas))))
    : [el("tr", {}, el("td", { colspan: "3" }, "Sin tráfico en los últimos 60 s"))]));
}

function mostrarTooltip(p, x, anchoCaja) {
  const tip = $("#grafica-tooltip");
  const fila = (clase, valor, nombre) => el("div", { className: "t-fila" }, el("span", { className: "t-clave", style: `background:var(${clase})` }), el("strong", {}, num(valor)), el("span", {}, nombre));
  tip.replaceChildren(
    el("div", { className: "t-titulo" }, fmtHoraCorta.format(new Date(p.t * 1000))),
    fila("--serie-1", p.aceptadas, "aceptadas"),
    fila("--serie-2", p.rechazadas, "rechazadas (429)"),
  );
  tip.hidden = false;
  if (x !== null) {
    const izquierda = x + 170 > anchoCaja ? x - 170 : x + 12;
    tip.style.left = `${Math.max(0, izquierda)}px`;
    tip.style.top = "8px";
  }
}

// ------------------------------------------------------------------ emergencias y feed
const ESTADOS_EMERGENCIA = {
  enviada: ["good", "Correo enviado"],
  encolada: ["activo", "En cola"],
  reintentando: ["warning", "Reintentando"],
  dlq: ["critical", "En DLQ"],
  fallida: ["critical", "No encolada (503)"],
  recibida: ["neutral", "Recibida"],
};
function pintarEmergencias(lista) {
  $("#emergencias-vacio").hidden = lista.length > 0;
  $("#tabla-emergencias").replaceChildren(...lista.map((em) => {
    const [nivel, texto] = ESTADOS_EMERGENCIA[em.estado] ?? ["neutral", em.estado];
    return el("tr", em.en_corrida ? {} : { className: "fuera", title: "Entró después de que k6 terminó: no cuenta en la corrida" },
      el("td", { class: "placa" }, em.placa, em.en_corrida ? null : el("span", { className: "etiqueta-fuera" }, "fuera de corrida")),
      el("td", {}, hora(em.recibida)),
      el("td", { class: "num" }, em.ms_encolada === null ? "—" : `+${num(em.ms_encolada)} ms`),
      el("td", { class: "num" }, em.ms_envio === null ? "—" : `+${num(em.ms_envio)} ms`),
      el("td", { class: "num" }, num(em.intentos)),
      el("td", {}, el("span", { className: "insignia", dataset: { nivel } }, texto)),
    );
  }));
}

const NOMBRES_EVENTO = {
  EMERGENCY_RECEIVED: "Emergency recibida",
  EMERGENCY_ENQUEUE_FAILED: "No se pudo encolar (503)",
  EMAIL_SENT: "Correo enviado",
  EMAIL_RETRY: "Reintento de envío",
  EMAIL_DLQ: "Enviado a la DLQ",
  CONSUMER_ERROR: "Error leyendo la cola",
  WORKER_ERROR: "Error del worker",
  NOTIFIER_STARTED: "Notifier iniciado",
  PENDING_CLAIMED: "Pendientes reclamados",
};
function pintarFeed(feed) {
  $("#feed-vacio").hidden = feed.length > 0;
  $("#feed").replaceChildren(...feed.map((f) => el("li", {},
    el("time", { datetime: f.ts }, hora(f.ts)),
    el("span", { className: "f-evento" }, NOMBRES_EVENTO[f.evento] ?? f.evento),
    el("span", { className: "f-detalle", title: f.detalle ?? "" }, [f.placa, f.detalle].filter(Boolean).join(" · ") || f.servicio),
  )));
}

addEventListener("resize", () => { if (ultimoEstado) { pintarGrafica(ultimoEstado.serie); pintarLinea(ultimoEstado); } });
ciclo();

// ------------------------------------------------------------------ modo de carga
function modoElegido() {
  return document.querySelector('input[name="modo"]:checked').value;
}

function textoBotonCarga() {
  return `Lanzar corrida #${proximaCorrida}`;
}

function nombreSmtp(host) {
  return host === "smtp.gmail.com" ? "Gmail" : host;
}

function pintarModo() {
  const modo = modoElegido();
  $("#modo-ayuda").textContent = AYUDA_MODO[modo];
  $("#campo-emergencias").hidden = modo === "profesor"; // ese script decide cuántos manda
  if (!$("#btn-carga").disabled) $("#btn-carga").textContent = textoBotonCarga();
}

for (const radio of document.querySelectorAll('input[name="modo"]')) radio.addEventListener("change", pintarModo);
pintarModo();
