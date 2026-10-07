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
  pintarMedida(e.medida_rubrica, e.k6.estado === "corriendo");
  pintarKpis(e);
  pintarFlujo(e, ahora);
  pintarAcciones(e);
  pintarGrafica(e.serie);
  pintarEmergencias(e.emergencias);
  pintarFeed(e.feed);
  $("#ventana").textContent = e.ventana_desde ? `Ventana desde ${fmtHoraCorta.format(new Date(e.ventana_desde))}` : "Ventana: todo el historial";
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
function pintarMedida(m, cargaEnCurso) {
  const marca = $("#escala-marca");
  const estado = $("#medida-estado");
  const neutro = (texto) => {
    $("#medida-valor").textContent = "—";
    estado.dataset.nivel = "neutral";
    estado.querySelector(".estado-icono").textContent = "•";
    $("#medida-texto").textContent = texto;
    marca.hidden = true;
  };
  // Mientras k6 envía, la "última petición" todavía no existe: la medida no es válida aún.
  if (cargaEnCurso) return neutro("Carga en curso: la medida se fija cuando k6 termina");
  if (m.segundos === null) return neutro("Sin correos en esta ventana");
  const efectivo = Math.max(m.segundos, 0);
  $("#medida-valor").textContent = fmtSeg.format(efectivo);
  const n = NIVELES[m.nivel];
  estado.dataset.nivel = m.nivel;
  estado.querySelector(".estado-icono").textContent = n.icono;
  $("#medida-texto").textContent = m.segundos < 0 ? `${n.texto} · el correo salió antes de la última petición` : n.texto;
  marca.hidden = false;
  marca.style.left = `${(Math.min(efectivo, 60) / 60) * 100}%`;
}

// ------------------------------------------------------------------ KPIs
function pintarKpis(e) {
  $("#kpi-aceptadas").textContent = num(e.http.aceptadas);
  $("#kpi-aceptadas-pie").textContent = `de ${num(e.http.total)} recibidas por el gateway${e.http.otros_errores ? ` · ${num(e.http.otros_errores)} otros errores` : ""}`;
  $("#kpi-429").textContent = num(e.http.rechazadas_429);
  $("#kpi-enviadas").textContent = num(e.eventos.enviadas);
  $("#kpi-emergencias").textContent = num(e.eventos.emergencias);
  const extra = [e.eventos.reintentos && `${num(e.eventos.reintentos)} reintentos`, e.eventos.dlq && `${num(e.eventos.dlq)} en DLQ`, e.eventos.fallidas && `${num(e.eventos.fallidas)} sin encolar`].filter(Boolean);
  $("#kpi-emergencias-pie").textContent = extra.length ? extra.join(" · ") : "correos enviados / detectadas";
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
  $("#btn-carga").textContent = corriendo ? "Carga en curso…" : textoBotonCarga();
  const nivelK6 = { corriendo: "activo", terminado: "good", fallido: "critical" }[e.k6.estado] ?? "neutral";
  const textoK6 = { corriendo: `Corriendo (${NOMBRE_MODO[e.k6.modo] ?? e.k6.modo})`, terminado: `Terminada (${NOMBRE_MODO[e.k6.modo] ?? e.k6.modo})`, fallido: `Falló (código ${e.k6.codigo})` }[e.k6.estado] ?? "Inactivo";
  fijarPildora($("#k6-estado"), nivelK6, textoK6);
  // Solo se descarga una carga terminada (bien o mal); una carga nueva reemplaza a la anterior.
  const descargable = e.k6.estado === "terminado" || e.k6.estado === "fallido";
  for (const boton of document.querySelectorAll(".descargas button")) {
    if (!boton.dataset.ocupado) boton.disabled = !descargable;
  }
  const consola = $("#k6-salida");
  const texto = e.k6.salida.join("\n");
  if (consola.textContent !== texto) {
    consola.textContent = texto;
    consola.scrollTop = consola.scrollHeight;
  }
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
    avisar(`Emergency ${d.placa} enviada por el gateway → HTTP ${d.status_gateway}.`);
  } catch (err) {
    avisar(`No se pudo enviar: ${err.message}`);
  } finally {
    boton.disabled = false;
  }
});

for (const boton of document.querySelectorAll(".descargas button")) {
  boton.addEventListener("click", async () => {
    boton.dataset.ocupado = "1";
    boton.disabled = true;
    try {
      const r = await fetch(`/api/carga/logs?formato=${boton.dataset.formato}`);
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || `HTTP ${r.status}`);
      const nombre = /filename="([^"]+)"/.exec(r.headers.get("Content-Disposition") ?? "")?.[1] ?? `carga.${boton.dataset.formato}`;
      const url = URL.createObjectURL(await r.blob());
      el("a", { href: url, download: nombre }).click();
      URL.revokeObjectURL(url);
      avisar(`Descargado ${nombre}.`);
    } catch (err) {
      avisar(`No se pudieron descargar los logs: ${err.message}`);
    } finally {
      delete boton.dataset.ocupado;
    }
  });
}

$("#btn-carga").addEventListener("click", async () => {
  const modo = modoElegido();
  const profesor = modo === "profesor";
  const emergencias = Number($("#emergencias").value);
  try {
    await post("/api/carga", profesor ? { modo } : { modo, emergencias });
    const detalle = profesor ? "k6/profesor.js decide los Emergency" : `${emergencias} Emergency`;
    avisar(`Carga lanzada con ${NOMBRE_MODO[modo]} (${detalle}). La ventana se reinició para observar solo esta corrida.`);
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

$("#btn-ventana").addEventListener("click", async () => {
  try {
    await post("/api/ventana/reiniciar");
    avisar("Ventana reiniciada: los contadores empiezan desde ahora.");
  } catch (err) {
    avisar(`No se pudo reiniciar: ${err.message}`);
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
    if (ultimoEstado) pintarGrafica(ultimoEstado.serie);
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
    return el("tr", {},
      el("td", { class: "placa" }, em.placa),
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

addEventListener("resize", () => ultimoEstado && pintarGrafica(ultimoEstado.serie));
ciclo();

// ------------------------------------------------------------------ modo de carga
function modoElegido() {
  return document.querySelector('input[name="modo"]:checked').value;
}

function textoBotonCarga() {
  return modoElegido() === "profesor" ? "Lanzar carga · k6 del profesor" : "Lanzar carga · k6 propio";
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
