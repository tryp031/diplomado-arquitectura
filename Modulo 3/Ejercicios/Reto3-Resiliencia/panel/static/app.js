/* Panel Reto 3. Consulta /api/estado cada 1,5 s y pinta. Todo dato que viene de la red entra con
 * textContent (o como atributo de SVG), nunca con innerHTML. */
(function () {
  'use strict';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var $ = function (id) { return document.getElementById(id); };
  var ultimo = null, ocupado = false, ultimaManual = null, hechasPrev = 0, tablaVisible = false;

  function el(tag, attrs, hijos) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') n.textContent = attrs[k]; else if (k === 'class') n.className = attrs[k]; else n.setAttribute(k, attrs[k]);
    });
    (hijos || []).forEach(function (h) { if (h) n.appendChild(h); });
    return n;
  }
  function sv(tag, attrs, texto) {
    var n = document.createElementNS(SVGNS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (texto !== undefined) n.textContent = texto;
    return n;
  }
  function vaciar(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function hora(v) { return new Date(v).toLocaleTimeString('es-CO', {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false}); }
  function horaMin(v) { return new Date(v).toLocaleTimeString('es-CO', {hour: '2-digit', minute: '2-digit', hour12: false}); }
  function objetivo(errores, r) { return errores >= r.minimo ? 3 : errores >= r.degradado ? 2 : 1; }

  async function api(metodo, ruta, cuerpo) {
    var r = await fetch(ruta, {method: metodo, headers: {'Content-Type': 'application/json'},
      body: cuerpo ? JSON.stringify(cuerpo) : undefined});
    var datos = await r.json().catch(function () { return {}; });
    if (!r.ok) throw new Error(datos.error || ('HTTP ' + r.status));
    return datos;
  }
  function mostrarError(msg) { var e = $('errorGlobal'); e.hidden = !msg; e.textContent = msg || ''; }

  /* ── Nivel actual: del servidor si se puede leer; si no, el último que vio el cliente ── */
  function nivelVigente(s) {
    var ahora = new Date(s.reloj.minuto).getTime();
    if (s.servidor.lectura && s.nivel.actual) return {n: s.nivel.actual, fuente: 'servidor · DynamoDB'};
    var cand = [];
    if (s.k6.ultimas.length && s.k6.ultimas[0].nivel) cand.push({t: new Date(s.k6.ultimas[0].ts).getTime(), n: s.k6.ultimas[0].nivel});
    if (ultimaManual && ultimaManual.n) cand.push(ultimaManual);
    cand.sort(function (a, b) { return b.t - a.t; });
    if (cand.length && cand[0].t >= ahora) return {n: cand[0].n, fuente: 'según el cliente'};
    return {n: null, fuente: s.servidor.lectura ? 'sin peticiones este minuto' : 'solo cliente · sin datos'};
  }

  function filaDe(s, minuto) {
    return s.coherencia.filas.filter(function (f) { return f.minuto === minuto; })[0];
  }

  function pintarNivel(s) {
    var v = nivelVigente(s), r = s.regla;
    $('tarjetaNivel').dataset.nivel = v.n || 0;
    $('nivelFuente').textContent = v.fuente;
    var ahora = Math.floor(new Date(s.reloj.minuto).getTime() / 60000);
    var prev = filaDe(s, ahora - 1), act = filaDe(s, ahora);
    var errPrev = s.servidor.lectura ? s.nivel.errores_minuto_anterior : (prev ? prev.errores_cliente : 0);
    var errAct = s.servidor.lectura ? s.nivel.errores_minuto_actual : (act ? act.errores_cliente : 0);
    $('errPrev').textContent = errPrev;
    $('errAct').textContent = errAct;
    var tope = Math.max(15, errPrev);
    $('rellenoErr').style.width = Math.min(errPrev / tope, 1) * 100 + '%';
    $('rellenoErr').style.background = 'var(--n' + objetivo(errPrev, r) + ')';
    $('tick5').style.left = (r.degradado / tope * 100) + '%';
    $('tick10').style.left = (r.minimo / tope * 100) + '%';
    var seg = s.reloj.segundos_a_proximo;
    $('cuenta').textContent = seg;
    $('arco').style.strokeDashoffset = (326.7 * (1 - seg / 60)).toFixed(1);
    var p = $('permanencia');
    if (s.nivel.degradado_en && v.n > 1) {
      var desde = new Date(s.nivel.degradado_en).getTime();
      p.textContent = 'Degradó ' + horaMin(desde) + ' · se sostiene hasta ' + horaMin(desde + r.permanencia * 60000);
    } else {
      p.textContent = '';
    }
    $('reglaTxt').textContent = '≥ ' + r.degradado + ' → N2 · ≥ ' + r.minimo + ' → N3 · permanencia ' + r.permanencia + ' min';
    pintarDiagrama(v.n, s.k6);
  }

  /* ── Diagrama: resalta la Lambda activa y anima una petición por iteración del k6 ── */
  function pintarDiagrama(n, k6) {
    var d = $('diagrama');
    d.querySelectorAll('.nv').forEach(function (x) { x.classList.toggle('activo', +x.dataset.n === n); });
    d.classList.toggle('corriendo', k6.estado === 'corriendo');
    if (k6.hechas > hechasPrev && n) pulso(n);
    hechasPrev = k6.hechas;
  }
  function pulso(n) {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var d = $('diagrama'), punto = $('flujo');
    var tramos = [$('v1'), $('v2'), d.querySelector('path.nv[data-n="' + n + '"]')];
    var largos = tramos.map(function (t) { return t.getTotalLength(); });
    var total = largos.reduce(function (a, b) { return a + b; }, 0), inicio = null;
    punto.style.opacity = 1;
    function paso(t) {
      if (!inicio) inicio = t;
      var avance = Math.min((t - inicio) / 900, 1) * total, i = 0;
      while (i < tramos.length - 1 && avance > largos[i]) { avance -= largos[i]; i++; }
      var pt = tramos[i].getPointAtLength(Math.min(avance, largos[i]));
      punto.setAttribute('cx', pt.x); punto.setAttribute('cy', pt.y);
      if ((t - inicio) < 900) requestAnimationFrame(paso); else punto.style.opacity = '';
    }
    requestAnimationFrame(paso);
  }

  /* ── Corrida k6 y guion ── */
  function chips(cont, sec) {
    vaciar(cont);
    if (!sec.length) { cont.appendChild(el('span', {class: 'vacio', text: '—'})); return; }
    sec.forEach(function (n, i) {
      if (i) cont.appendChild(el('span', {class: 'flecha', text: '→'}));
      cont.appendChild(el('span', {class: 'chip l' + n, text: 'N' + n}));
    });
  }

  function pintarK6(k) {
    var corriendo = k.estado === 'corriendo';
    $('bK6').disabled = corriendo || !ultimo.entorno.url;
    $('bK6Stop').hidden = !corriendo;
    var textos = {
      inactivo: 'Sin corrida en este entorno.',
      corriendo: k.esperando_segundo_00 ? 'Esperando el segundo 00 del reloj para arrancar…' : 'Corriendo…',
      terminado: 'Corrida terminada.',
      fallido: 'k6 terminó con error: ' + (k.error || ''),
      detenido: 'Corrida detenida a mano.'
    };
    $('estadoK6').textContent = textos[k.estado] || k.estado;
    $('barraK6').style.width = (k.hechas / k.total * 100) + '%';
    $('contK6').textContent = k.hechas + ' / ' + k.total + ' iteraciones';
    chips($('secuencia'), k.secuencia);
    chips($('secEsperada'), k.secuencia_esperada);
    Array.prototype.forEach.call($('veredicto').children, function (li) {
      // Un criterio se marca ✗ solo con la corrida cerrada; mientras corre, lo no cumplido está pendiente.
      // «Sin saltos» es al revés: se cumple desde el inicio y solo puede romperse.
      var v = k.veredicto[li.dataset.k], cerrada = k.estado !== 'corriendo' && k.hechas > 0;
      if (li.dataset.k === 'sin_saltos') li.className = k.hechas ? (v ? 'si' : 'no') : '';
      else li.className = v ? 'si' : (cerrada ? 'no' : '');
    });
    var tb = $('respuestas');
    vaciar(tb);
    if (!k.ultimas.length) tb.appendChild(el('tr', {}, [el('td', {colspan: 5, class: 'vacio', text: 'Sin respuestas todavía.'})]));
    k.ultimas.forEach(function (it) {
      tb.appendChild(el('tr', {class: it.nivel ? 'l' + it.nivel : ''}, [
        el('td', {class: 'n', text: it.iteracion}),
        el('td', {class: 'm', text: hora(it.ts)}),
        el('td', {class: 'm', text: it.error ? 'true' : 'false'}),
        el('td', {class: 'n' + (it.status >= 500 ? ' st5' : ''), text: it.status}),
        el('td', {class: 'msg', text: it.mensaje || '(sin respuesta)'})
      ]));
    });
  }

  function pintarGuion(s) {
    var g = $('guion'), k = s.k6;
    vaciar(g);
    var actual = k.estado === 'corriendo' && k.ultimas.length ? k.ultimas[0].minuto_logico : null;
    s.guion.forEach(function (m) {
      var lv = el('div', {class: 'lv'}, [el('span', {class: 'esp l' + m.nivel_esperado, text: 'N' + m.nivel_esperado, title: 'Predicción de la regla'})]);
      m.niveles_vistos.forEach(function (n) { lv.appendChild(el('span', {class: 'l' + n, text: 'N' + n, title: 'Respondió el sistema'})); });
      var ok = !m.iteraciones ? '' : (m.niveles_vistos.length === 1 && m.niveles_vistos[0] === m.nivel_esperado ? 'si' : 'no');
      var cls = 'gm' + (m.cola ? ' cola' : '') + (actual === m.minuto ? ' ahora' : '');
      g.appendChild(el('div', {class: cls, title: m.cola ? 'Cola: iteraciones que caen después del minuto 7 por la latencia' : ''}, [
        el('span', {class: 'min', text: m.cola ? 'cola' : 'min ' + m.minuto}),
        el('span', {class: 'iny'}, [document.createTextNode(m.cola ? '—' : m.errores), el('small', {text: m.cola ? '' : ' err'})]),
        lv,
        el('div', {class: 'ok ' + ok, text: ok === 'si' ? '✓' : ok === 'no' ? (m.niveles_vistos.length > 1 ? '↔ borde' : '✗') : ''})
      ]));
    });
  }

  /* ── Gráfica: nivel por minuto (servidor, regla, cliente) y errores por minuto ── */
  function pintarGrafica(s) {
    var filas = s.coherencia.filas, r = s.regla, lectura = s.servidor.lectura;
    var sN = $('svgNivel'), sE = $('svgErr');
    vaciar(sN); vaciar(sE);
    $('graficaVacia').hidden = filas.length > 0;
    sN.style.display = sE.style.display = filas.length ? '' : 'none';
    pintarTabla(filas);
    if (!filas.length) return;
    // hN y hE son las alturas de .svg-nivel y .svg-err en estilos.css: cambian juntas.
    var W = $('grafica').clientWidth, IZQ = 44, DER = 10, hN = 228, hE = 140;
    var ancho = (W - IZQ - DER) / filas.length;
    var x = function (i) { return IZQ + i * ancho; };
    var yN = function (n) { return {1: 180, 2: 112, 3: 44}[n]; };
    sN.setAttribute('viewBox', '0 0 ' + W + ' ' + hN);
    sE.setAttribute('viewBox', '0 0 ' + W + ' ' + hE);
    [1, 2, 3].forEach(function (n) {
      sN.appendChild(sv('rect', {class: 'banda l' + n, x: IZQ, y: yN(n) - 26, width: W - IZQ - DER, height: 52, rx: 8}));
      sN.appendChild(sv('text', {class: 'eje n', x: IZQ - 10, y: yN(n) + 4, 'text-anchor': 'end'}, 'N' + n));
    });
    var paso = Math.ceil(filas.length / Math.max(1, Math.floor((W - IZQ) / 64)));
    filas.forEach(function (f, i) {
      if (i % paso === 0) sN.appendChild(sv('text', {class: 'eje', x: x(i) + ancho / 2, y: hN - 2, 'text-anchor': 'middle'}, horaMin(f.minuto * 60000)));
    });
    function escalones(clave, cls) {
      // Un tramo horizontal por minuto; entre minutos contiguos, el salto es vertical en el borde.
      var d = '', enTramo = false;
      filas.forEach(function (f, i) {
        var n = f[clave];
        if (!n) { enTramo = false; return; }
        d += (enTramo ? ' V' + yN(n) : ' M' + x(i) + ' ' + yN(n)) + ' H' + (x(i) + ancho);
        enTramo = true;
      });
      if (d) sN.appendChild(sv('path', {class: cls, d: d}));
    }
    escalones('nivel_regla', 'reg');
    if (lectura) escalones('nivel_servidor', 'srv');
    filas.forEach(function (f, i) {
      f.niveles_cliente.forEach(function (n, j) {
        var malo = (f.nivel_regla && n !== f.nivel_regla) || (f.nivel_servidor && n !== f.nivel_servidor);
        sN.appendChild(sv('circle', {class: 'cli l' + n + (malo ? ' malo' : ''), cx: x(i) + ancho / 2 + j * 12 - (f.niveles_cliente.length - 1) * 6,
          cy: yN(n), r: 6}));
      });
    });
    // Errores: una sola escala; umbrales como líneas de referencia.
    var errores = filas.map(function (f) { return lectura ? f.errores : f.errores_cliente; });
    var tope = Math.max(15, Math.max.apply(null, errores)), base = hE - 18;
    // 26 px libres arriba: la cifra de la barra más alta queda dentro del SVG y no pisa las horas de la gráfica de niveles.
    var yE = function (e) { return base - (e / tope) * (base - 26); };
    [[r.degradado, 'u2', 'N2'], [r.minimo, 'u3', 'N3']].forEach(function (u) {
      sE.appendChild(sv('line', {class: 'umbral ' + u[1], x1: IZQ, x2: W - DER, y1: yE(u[0]), y2: yE(u[0])}));
      sE.appendChild(sv('text', {class: 'lbl', x: IZQ - 6, y: yE(u[0]) + 4, 'text-anchor': 'end'}, u[0]));
    });
    sE.appendChild(sv('line', {class: 'grid', x1: IZQ, x2: W - DER, y1: base, y2: base}));
    sE.appendChild(sv('text', {class: 'lbl', x: IZQ - 6, y: base + 4, 'text-anchor': 'end'}, '0'));
    sE.appendChild(sv('text', {class: 'lbl', x: IZQ, y: hE - 2}, lectura ? 'errores por minuto (servidor)' : 'errores por minuto (vistos por el k6)'));
    errores.forEach(function (e, i) {
      if (!e) return;
      var bw = Math.min(ancho - 6, 46), bx = x(i) + (ancho - bw) / 2;
      sE.appendChild(sv('rect', {class: 'barra l' + objetivo(e, r), x: bx, y: yE(e), width: bw, height: base - yE(e), rx: 4}));
      sE.appendChild(sv('text', {class: 'val', x: x(i) + ancho / 2, y: yE(e) - 5}, e));
    });
    var ahora = Math.floor(new Date(s.reloj.minuto).getTime() / 60000);
    filas.forEach(function (f, i) {
      if (f.minuto === ahora) sN.appendChild(sv('line', {class: 'ahora-l', x1: x(i) + 1, x2: x(i) + 1, y1: 14, y2: 206}));
      [sN, sE].forEach(function (svg) {
        var h = sv('rect', {class: 'hit', x: x(i), y: 0, width: ancho, height: svg === sN ? hN : hE, tabindex: 0});
        h.addEventListener('pointermove', function (ev) { tip(f, ev, lectura); });
        h.addEventListener('focus', function (ev) { tip(f, ev, lectura); });
        h.addEventListener('pointerleave', function () { $('tip').hidden = true; });
        h.addEventListener('blur', function () { $('tip').hidden = true; });
        svg.appendChild(h);
      });
    });
  }

  function tip(f, ev, lectura) {
    var t = $('tip'), caja = $('grafica').getBoundingClientRect();
    vaciar(t);
    t.appendChild(el('h4', {text: horaMin(f.minuto * 60000) + ' · minuto de reloj'}));
    var filas = [
      ['Servidor', f.nivel_servidor ? 'N' + f.nivel_servidor : (lectura ? '—' : 'sin lectura')],
      ['Regla', f.nivel_regla ? 'N' + f.nivel_regla : '—'],
      ['Cliente', f.niveles_cliente.length ? 'N' + f.niveles_cliente.join(' · N') : '—'],
      ['Errores', String(lectura ? f.errores : f.errores_cliente)],
      ['Peticiones', String(lectura ? f.peticiones : (f.iteraciones ? f.iteraciones : '—'))]
    ];
    filas.forEach(function (p) { t.appendChild(el('div', {}, [el('b', {text: p[1]}), el('span', {text: p[0]})])); });
    t.hidden = false;
    var px = (ev.clientX || caja.left + caja.width / 2) - caja.left, py = (ev.clientY || caja.top + 40) - caja.top;
    t.style.left = Math.min(Math.max(px + 14, 0), caja.width - 210) + 'px';
    t.style.top = Math.max(py - 20, 0) + 'px';
  }

  function tag(n) { return n ? el('span', {class: 'tag l' + n, text: 'N' + n}) : document.createTextNode('—'); }
  function pintarTabla(filas) {
    var tb = $('filasMin');
    vaciar(tb);
    filas.forEach(function (f) {
      var cli = el('td');
      if (!f.niveles_cliente.length) cli.textContent = '—';
      f.niveles_cliente.forEach(function (n) { cli.appendChild(tag(n)); cli.appendChild(document.createTextNode(' ')); });
      tb.appendChild(el('tr', {}, [
        el('td', {class: 'm', text: horaMin(f.minuto * 60000)}),
        el('td', {class: 'n', text: ultimo.servidor.lectura ? f.errores : f.errores_cliente}),
        el('td', {class: 'n', text: f.peticiones || '—'}),
        el('td', {}, [tag(f.nivel_servidor)]), el('td', {}, [tag(f.nivel_regla)]), cli,
        el('td', {class: 'm', text: f.iteraciones || '—'})
      ]));
    });
  }

  function pintarCoherencia(s) {
    var c = s.coherencia;
    var a = $('coherencia');
    a.className = 'coh' + (c.minutos ? (c.todo_coincide ? ' si' : ' no') : '');
    a.textContent = c.minutos ? 'Cliente = servidor en ' + c.coinciden + '/' + c.minutos + ' min' : '';
    var b = $('cohRegla');
    b.className = 'coh' + (c.minutos_regla ? (c.regla_se_cumple ? ' si' : ' no') : '');
    b.textContent = c.minutos_regla ? 'Regla cumplida en ' + c.coinciden_regla + '/' + c.minutos_regla + ' min' : '';
  }

  function pintarEventos(s) {
    var ol = $('eventos');
    vaciar(ol);
    if (!s.servidor.lectura) { ol.appendChild(el('li', {class: 'vacio', text: 'Sin permiso de lectura de CloudWatch: ' + (s.servidor.motivo || '')})); return; }
    if (s.servidor.error) { ol.appendChild(el('li', {class: 'vacio', text: s.servidor.error})); return; }
    if (!s.servidor.eventos.length) { ol.appendChild(el('li', {class: 'vacio', text: 'Sin cambios de nivel registrados.'})); return; }
    s.servidor.eventos.forEach(function (e) {
      var titulo, detalle, clase;
      if (e.evento === 'CAMBIO_NIVEL') {
        titulo = 'N' + e.de + ' → N' + e.a + ' · ' + (e.motivo === 'degradacion' ? 'degradación' : 'recuperación');
        detalle = e.errores_minuto_anterior + ' errores en el minuto anterior · umbrales ' + e.umbrales.degradado + '/' + e.umbrales.minimo +
          (e.umbrales.permanencia ? ' · permanencia ' + e.umbrales.permanencia + ' min' : '');
        clase = e.motivo;
      } else {
        titulo = e.evento.replace(/_/g, ' ').toLowerCase();
        detalle = e.detalle || '';
        clase = 'falla';
      }
      ol.appendChild(el('li', {class: clase}, [
        el('span', {class: 'h', text: hora(e.ts)}), el('span', {class: 't', text: titulo}), el('span', {class: 'd', text: detalle})
      ]));
    });
  }

  function pintarEntorno(s) {
    var e = s.entorno;
    document.querySelectorAll('.seg-ctl button').forEach(function (b) {
      b.setAttribute('aria-checked', b.dataset.entorno === e.activo ? 'true' : 'false');
      if (b.dataset.entorno === 'aws') {
        b.disabled = !e.aws_disponible;
        b.title = e.aws_disponible ? 'Despliegue en AWS (us-east-2)' : (e.aws_motivo || 'AWS no configurado');
      }
    });
    var m = $('modo');
    m.className = 'modo ' + (s.servidor.lectura ? 'total' : 'cliente');
    m.textContent = s.servidor.lectura ? 'Cliente + servidor' : 'Solo cliente';
    var av = $('avisoLectura');
    av.hidden = s.servidor.lectura;
    av.textContent = s.servidor.lectura ? '' : 'Modo solo cliente: ' + (s.servidor.motivo || '') +
      '. El k6 y las pruebas manuales funcionan, y la regla se verifica con los errores que ve el propio k6. Faltan el nivel del servidor y los logs.';
    $('url').textContent = e.url || 'sin despliegue: corra scripts/deploy.sh ' + (e.activo === 'aws' ? 'aws' : 'localstack');
    $('url').title = e.url || '';
    $('bReiniciar').hidden = !e.permite_reinicio;
    ['bOk', 'bErr'].forEach(function (id) { $(id).disabled = !e.url; });
    var hay = !!s.k6.inicio;
    document.querySelectorAll('.descargas a').forEach(function (a) {
      a.setAttribute('aria-disabled', hay ? 'false' : 'true');
      a.href = hay ? '/api/descargas/' + a.dataset.tipo : '#';
    });
    $('notaDescargas').textContent = hay
      ? (s.k6.estado === 'corriendo' ? 'La corrida sigue en curso: lo que descargue ahora es parcial.' :
        'Evidencia de la corrida del ' + hora(s.k6.inicio) + '. El ZIP incluye el diff que demuestra que el script oficial solo cambió en la URL.')
      : 'Disponible cuando haya una corrida del k6 en este entorno.';
    mostrarError(s.servidor.error ? 'No se pudo leer el servidor (' + e.activo + '): ' + s.servidor.error : '');
  }

  async function refrescar() {
    if (ocupado) return;
    ocupado = true;
    try {
      var s = await api('GET', '/api/estado');
      ultimo = s;
      pintarEntorno(s); pintarNivel(s); pintarK6(s.k6); pintarGuion(s); pintarCoherencia(s); pintarGrafica(s); pintarEventos(s);
    } catch (err) {
      mostrarError('El panel no responde: ' + err.message);
    } finally {
      ocupado = false;
    }
  }

  /* ── Acciones ── */
  function accion(boton, fn) {
    boton.addEventListener('click', async function () {
      boton.disabled = true;
      try { await fn(); mostrarError(''); } catch (err) { mostrarError(err.message); }
      finally { boton.disabled = false; refrescar(); }
    });
  }
  accion($('bK6'), function () { return api('POST', '/api/k6'); });
  accion($('bK6Stop'), function () { return api('POST', '/api/k6/detener'); });
  function manual(error) {
    return async function () {
      var r = await api('POST', '/api/peticion', {error: error});
      var caja = $('respManual'), n = /^Nivel (\d):/.exec(r.mensaje || '');
      ultimaManual = n ? {t: Date.now(), n: +n[1]} : null;
      if (n) pulso(+n[1]);
      vaciar(caja);
      caja.appendChild(el('span', {class: 'st ' + (r.status < 500 ? 'ok' : 'mal'), text: r.status + ' · ' + r.ms + ' ms · error: ' + error}));
      caja.appendChild(el('span', {text: r.mensaje}));
    };
  }
  accion($('bOk'), manual(false));
  accion($('bErr'), manual(true));
  accion($('bReiniciar'), async function () {
    if (!confirm('¿Borrar el estado por minuto de LocalStack? El sistema vuelve a N1.')) return;
    await api('POST', '/api/reiniciar');
  });
  document.querySelectorAll('.seg-ctl button').forEach(function (b) {
    accion(b, function () { ultimaManual = null; return api('POST', '/api/entorno', {entorno: b.dataset.entorno}); });
  });
  $('bTabla').addEventListener('click', function () {
    tablaVisible = !tablaVisible;
    this.setAttribute('aria-pressed', tablaVisible);
    this.textContent = tablaVisible ? 'Ver gráfica' : 'Ver tabla';
    $('tablaMin').hidden = !tablaVisible;
    $('grafica').hidden = tablaVisible;
    $('leyenda').hidden = tablaVisible;
  });
  $('bTema').addEventListener('click', function () {
    var f = document.documentElement.getAttribute('data-theme');
    var oscuro = f === 'dark' || (!f && matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.setAttribute('data-theme', oscuro ? 'light' : 'dark');
    if (ultimo) pintarGrafica(ultimo);
  });
  window.addEventListener('resize', function () { if (ultimo) pintarGrafica(ultimo); });
  setInterval(function () { $('reloj').textContent = new Date().toLocaleTimeString('es-CO', {hour12: false}); }, 1000);

  refrescar();
  setInterval(refrescar, 1500);
})();
