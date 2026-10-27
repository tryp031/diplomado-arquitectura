/* Panel Reto 3. Consulta /api/estado cada 1,5 s y pinta.
 * Todo dato que viene de la red entra con textContent (o como atributo de SVG), nunca con innerHTML. */
(function () {
  'use strict';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var $ = function (id) { return document.getElementById(id); };
  var ultimo = null, ocupado = false, ultimaManual = null;
  var hechasPrev = null, nivelPrev = null, iterMaxPrev = 0;
  var firmas = {};  // última firma pintada por bloque: las tablas solo se redibujan si cambian sus datos
  var sinMovimiento = matchMedia('(prefers-reduced-motion: reduce)');

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
  function fechaHora(seg) {
    return new Date(seg * 1000).toLocaleString('es-CO', {day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false});
  }
  function tag(n) { return n ? el('span', {class: 'tag l' + n, text: 'N' + n}) : document.createTextNode('—'); }
  function cambio(clave, valor) {
    var f = JSON.stringify(valor);
    if (firmas[clave] === f) return false;
    firmas[clave] = f;
    return true;
  }
  function marcar(nodo, clase, ms) {
    nodo.classList.remove(clase);
    void nodo.getBoundingClientRect();  // reinicia la animación CSS si ya estaba puesta
    nodo.classList.add(clase);
    setTimeout(function () { nodo.classList.remove(clase); }, ms);
  }

  async function api(metodo, ruta, cuerpo) {
    var r = await fetch(ruta, {method: metodo, headers: {'Content-Type': 'application/json'},
      body: cuerpo ? JSON.stringify(cuerpo) : undefined});
    var datos = await r.json().catch(function () { return {}; });
    if (!r.ok) throw new Error(datos.error || ('HTTP ' + r.status));
    return datos;
  }
  function mostrarError(msg) { var e = $('errorGlobal'); e.hidden = !msg; e.textContent = msg || ''; }

  /* ── 1 · Nivel: del servidor si se puede leer; si no, el último que vio el cliente ── */
  function nivelVigente(s) {
    var ahora = new Date(s.reloj.minuto).getTime();
    if (s.servidor.lectura && s.nivel.actual) return {n: s.nivel.actual, fuente: 'servidor · DynamoDB'};
    var cand = [];
    if (s.k6.ultimas.length && s.k6.ultimas[0].nivel) cand.push({t: new Date(s.k6.ultimas[0].ts).getTime(), n: s.k6.ultimas[0].nivel});
    if (ultimaManual && ultimaManual.n) cand.push(ultimaManual);
    cand.sort(function (a, b) { return b.t - a.t; });
    if (cand.length && cand[0].t >= ahora) return {n: cand[0].n, fuente: 'según el cliente'};
    return {n: null, fuente: s.servidor.lectura ? 'sin tráfico este minuto' : 'sin datos'};
  }
  function filaDe(s, minuto) { return s.coherencia.filas.filter(function (f) { return f.minuto === minuto; })[0]; }
  function objetivo(errores, r) { return errores >= r.minimo ? 3 : errores >= r.degradado ? 2 : 1; }

  function pintarNivel(s) {
    var v = nivelVigente(s), r = s.regla, t = $('tarjetaNivel');
    t.dataset.nivel = v.n || 0;
    $('nivelFuente').textContent = v.fuente;
    if (v.n && nivelPrev && v.n !== nivelPrev) {
      marcar(t, 'cambio', 1900);
      var nodo = document.querySelector('.nodo.nv[data-n="' + v.n + '"]');
      if (nodo) marcar(nodo, 'cambio', 2500);
    }
    if (v.n) nivelPrev = v.n;
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
    } else p.textContent = '';
    $('reglaTxt').textContent = '≥ ' + r.degradado + ' → N2 · ≥ ' + r.minimo + ' → N3 · permanencia ' + r.permanencia + ' min';
    return v.n;
  }

  /* ── 2 · Flujo: ruta activa, conteo por Lambda y un punto por cada petición nueva ── */
  function pintarFlujo(s, n) {
    var d = $('diagrama'), k = s.k6;
    d.querySelectorAll('.nv').forEach(function (x) { x.classList.toggle('activo', +x.dataset.n === n); });
    var conteo = {1: 0, 2: 0, 3: 0};
    k.ultimas.forEach(function (it) { if (it.nivel) conteo[it.nivel]++; });
    d.querySelectorAll('.nodo.nv').forEach(function (g) {
      var c = conteo[g.dataset.n];
      g.querySelector('.cuenta-nv').textContent = c + (c === 1 ? ' petición' : ' peticiones') + ' en la corrida';
    });
    // Solo se anima lo nuevo desde la consulta anterior; al abrir el panel no se reproduce el historial.
    if (hechasPrev !== null && k.hechas > hechasPrev) {
      k.ultimas.slice(0, Math.min(k.hechas - hechasPrev, 6)).reverse().forEach(function (it, i) {
        setTimeout(function () { viaje(it.nivel, it.error); }, i * 320);
      });
    }
    hechasPrev = k.hechas;
  }

  function recorrer(punto, tramos, ms, alTerminarTramo, fin) {
    var largos = tramos.map(function (t) { return t.camino.getTotalLength(); });
    var total = largos.reduce(function (a, b) { return a + b; }, 0), inicio = null, hecho = -1;
    function paso(t) {
      if (inicio === null) inicio = t;
      var avance = Math.min((t - inicio) / ms, 1) * total, i = 0;
      while (i < tramos.length - 1 && avance > largos[i]) { avance -= largos[i]; i++; }
      while (hecho < i - 1) { hecho++; alTerminarTramo(hecho); }
      var l = Math.min(avance, largos[i]);
      var pt = tramos[i].camino.getPointAtLength(tramos[i].inverso ? largos[i] - l : l);
      punto.setAttribute('cx', pt.x); punto.setAttribute('cy', pt.y);
      if (t - inicio < ms) requestAnimationFrame(paso);
      else { while (hecho < tramos.length - 1) { hecho++; alTerminarTramo(hecho); } fin(); }
    }
    requestAnimationFrame(paso);
  }

  function viaje(nivel, conError) {
    if (sinMovimiento.matches || document.hidden) return;
    var d = $('diagrama'), capa = $('capaPuntos');
    var punto = sv('circle', {class: 'punto ' + (conError ? 'err' : 'l' + (nivel || 0)), r: 7, cx: 120, cy: 120});
    capa.appendChild(punto);
    var golpes = [$('nGw'), $('nRouter')];
    recorrer(punto, [{camino: $('v1')}, {camino: $('v2')}], 700, function (i) { marcar(golpes[i], 'golpe', 450); }, function () {
      // El router consulta y actualiza el estado del minuto en DynamoDB antes de despachar.
      var ida = sv('circle', {class: 'punto dbd', r: 5});
      capa.appendChild(ida);
      recorrer(ida, [{camino: $('vDb')}, {camino: $('vDb'), inverso: true}], 520, function (i) { if (i === 0) marcar($('nDb'), 'golpe', 450); }, function () {
        capa.removeChild(ida);
        var ruta = nivel && d.querySelector('path.nv[data-n="' + nivel + '"]');
        if (!ruta) { capa.removeChild(punto); return; }
        recorrer(punto, [{camino: ruta}], 520, function () {
          var nodo = d.querySelector('.nodo.nv[data-n="' + nivel + '"]');
          if (nodo) marcar(nodo, 'golpe', 450);
        }, function () { capa.removeChild(punto); });
      });
    });
  }

  function pintarUltimoEvento(s) {
    var caja = $('ultimoEv'), ev = s.servidor.lectura && s.servidor.eventos.filter(function (e) { return e.evento === 'CAMBIO_NIVEL'; })[0];
    if (!cambio('ultimoEv', ev || s.servidor.lectura)) return;
    vaciar(caja);
    caja.className = 'ultimo-ev' + (ev ? ' ' + ev.motivo : '');
    if (!ev) {
      caja.appendChild(el('span', {class: 'vacio', text: s.servidor.lectura ? 'Sin cambios de nivel todavía.' : 'Sin lectura de CloudWatch.'}));
      return;
    }
    caja.appendChild(el('span', {class: 'h', text: 'Último cambio · ' + hora(ev.ts)}));
    caja.appendChild(el('span', {class: 't', text: 'N' + ev.de + ' → N' + ev.a + ' · ' + (ev.motivo === 'degradacion' ? 'degradación' : 'recuperación')}));
    caja.appendChild(el('span', {class: 'd', text: ev.errores_minuto_anterior + ' errores en el minuto anterior'}));
  }

  /* ── 3 · Corrida del k6 y guion ── */
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
      corriendo: k.esperando_segundo_00 ? 'Esperando el segundo 00 para arrancar…' : 'Corriendo…',
      terminado: 'Corrida terminada.',
      fallido: 'k6 terminó con error: ' + (k.error || ''),
      detenido: 'Corrida detenida a mano.'
    };
    $('estadoK6').textContent = textos[k.estado] || k.estado;
    $('barraK6').style.width = (k.hechas / k.total * 100) + '%';
    $('contK6').textContent = k.hechas + ' / ' + k.total;
    chips($('secuencia'), k.secuencia);
    chips($('secEsperada'), k.secuencia_esperada);
    Array.prototype.forEach.call($('veredicto').children, function (li) {
      // Un criterio se marca ✗ solo con la corrida cerrada; «sin saltos» se cumple desde el inicio y solo puede romperse.
      var v = k.veredicto[li.dataset.k], cerrada = k.estado !== 'corriendo' && k.hechas > 0;
      if (li.dataset.k === 'sin_saltos') li.className = k.hechas ? (v ? 'si' : 'no') : '';
      else li.className = v ? 'si' : (cerrada ? 'no' : '');
    });
  }

  function pintarGuion(s) {
    var k = s.k6, actual = k.estado === 'corriendo' && k.ultimas.length ? k.ultimas[0].minuto_logico : null;
    if (!cambio('guion', [s.guion, actual])) return;
    var g = $('guion');
    vaciar(g);
    s.guion.forEach(function (m) {
      var lv = el('div', {class: 'lv'}, [el('span', {class: 'esp l' + m.nivel_esperado, text: 'N' + m.nivel_esperado, title: 'Predicción de la regla'})]);
      m.niveles_vistos.forEach(function (n) { lv.appendChild(el('span', {class: 'l' + n, text: 'N' + n, title: 'Respondió el sistema'})); });
      var ok = !m.iteraciones ? '' : (m.niveles_vistos.length === 1 && m.niveles_vistos[0] === m.nivel_esperado ? 'si' : 'no');
      g.appendChild(el('div', {class: 'gm' + (m.cola ? ' cola' : '') + (actual === m.minuto ? ' ahora' : ''),
        title: m.cola ? 'Cola: iteraciones que caen después del minuto 7 por la latencia' : ''}, [
        el('span', {class: 'min', text: m.cola ? 'cola' : 'min ' + m.minuto}),
        el('span', {class: 'iny'}, [document.createTextNode(m.cola ? '—' : m.errores), el('small', {text: m.cola ? '' : ' err'})]),
        lv,
        el('div', {class: 'ok ' + ok, text: ok === 'si' ? '✓' : ok === 'no' ? (m.niveles_vistos.length > 1 ? '↔ borde' : '✗') : ''})
      ]));
    });
  }

  /* ── 4 · Gráfica: nivel por minuto y peticiones apiladas (errores abajo, para leerlos contra los umbrales) ── */
  function contarIteraciones(rango) {
    if (!rango) return 0;
    var p = String(rango).split('-');
    return +p[1] - +p[0] + 1;
  }
  function pintarGrafica(s, forzar) {
    var filas = s.coherencia.filas, r = s.regla, lectura = s.servidor.lectura;
    var W = $('grafica').clientWidth;
    if (!cambio('grafica', [filas, lectura, W, s.reloj.minuto]) && !forzar) return;
    var sN = $('svgNivel'), sP = $('svgPet');
    vaciar(sN); vaciar(sP);
    $('graficaVacia').hidden = filas.length > 0;
    sN.style.display = sP.style.display = filas.length ? '' : 'none';
    if (!filas.length) return;
    // hN y hP son las alturas de .svg-nivel y .svg-pet en estilos.css: cambian juntas.
    var IZQ = 44, DER = 10, hN = 200, hP = 150;
    var ancho = (W - IZQ - DER) / filas.length;
    var x = function (i) { return IZQ + i * ancho; };
    var yN = function (n) { return {1: 158, 2: 100, 3: 42}[n]; };
    sN.setAttribute('viewBox', '0 0 ' + W + ' ' + hN);
    sP.setAttribute('viewBox', '0 0 ' + W + ' ' + hP);
    [1, 2, 3].forEach(function (n) {
      sN.appendChild(sv('rect', {class: 'banda l' + n, x: IZQ, y: yN(n) - 24, width: W - IZQ - DER, height: 48, rx: 8}));
      sN.appendChild(sv('text', {class: 'eje n', x: IZQ - 10, y: yN(n) + 4, 'text-anchor': 'end'}, 'N' + n));
    });
    var paso = Math.ceil(filas.length / Math.max(1, Math.floor((W - IZQ) / 64)));
    filas.forEach(function (f, i) {
      if (i % paso === 0) sN.appendChild(sv('text', {class: 'eje', x: x(i) + ancho / 2, y: hN - 2, 'text-anchor': 'middle'}, horaMin(f.minuto * 60000)));
    });
    function escalones(clave, cls) {
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
        sN.appendChild(sv('circle', {class: 'cli l' + n + (malo ? ' malo' : ''), cx: x(i) + ancho / 2 + j * 12 - (f.niveles_cliente.length - 1) * 6, cy: yN(n), r: 6}));
      });
    });
    var datos = filas.map(function (f) {
      var pet = lectura ? f.peticiones : contarIteraciones(f.iteraciones), err = lectura ? f.errores : f.errores_cliente;
      return {pet: Math.max(pet, err), err: err};
    });
    var tope = Math.max(15, Math.max.apply(null, datos.map(function (d) { return d.pet; }))), base = hP - 20;
    var y = function (v) { return base - v / tope * (base - 24); };
    [[r.degradado, 'u2'], [r.minimo, 'u3']].forEach(function (u) {
      sP.appendChild(sv('line', {class: 'umbral ' + u[1], x1: IZQ, x2: W - DER, y1: y(u[0]), y2: y(u[0])}));
      sP.appendChild(sv('text', {class: 'lbl', x: IZQ - 6, y: y(u[0]) + 4, 'text-anchor': 'end'}, u[0]));
    });
    sP.appendChild(sv('line', {class: 'grid', x1: IZQ, x2: W - DER, y1: base, y2: base}));
    sP.appendChild(sv('text', {class: 'lbl', x: IZQ - 6, y: base + 4, 'text-anchor': 'end'}, '0'));
    sP.appendChild(sv('text', {class: 'lbl', x: IZQ, y: hP - 2}, lectura ? 'peticiones por minuto · DynamoDB' : 'peticiones por minuto · vistas por el k6'));
    datos.forEach(function (d, i) {
      if (!d.pet) return;
      var bw = Math.min(ancho - 8, 44), bx = x(i) + (ancho - bw) / 2, ok = d.pet - d.err;
      if (d.err) sP.appendChild(sv('rect', {class: 'err-b', x: bx, y: y(d.err), width: bw, height: base - y(d.err), rx: 3}));
      if (ok) {
        var techo = y(d.pet), piso = d.err ? y(d.err) - 2 : base;
        sP.appendChild(sv('rect', {class: 'ok-b', x: bx, y: techo, width: bw, height: Math.max(piso - techo, 1), rx: 3}));
      }
      if (d.err) sP.appendChild(sv('text', {class: 'val', x: x(i) + ancho / 2, y: y(d.pet) - 5}, d.err + ' err'));
    });
    var ahora = Math.floor(new Date(s.reloj.minuto).getTime() / 60000);
    filas.forEach(function (f, i) {
      if (f.minuto === ahora) sN.appendChild(sv('line', {class: 'ahora-l', x1: x(i) + 1, x2: x(i) + 1, y1: 14, y2: 184}));
      [sN, sP].forEach(function (svg) {
        var h = sv('rect', {class: 'hit', x: x(i), y: 0, width: ancho, height: svg === sN ? hN : hP, tabindex: 0});
        var mostrar = function (ev) { tip(f, datos[i], ev); };
        h.addEventListener('pointermove', mostrar); h.addEventListener('focus', mostrar);
        h.addEventListener('pointerleave', function () { $('tip').hidden = true; });
        h.addEventListener('blur', function () { $('tip').hidden = true; });
        svg.appendChild(h);
      });
    });
  }

  function tip(f, d, ev) {
    var t = $('tip'), caja = $('grafica').getBoundingClientRect();
    vaciar(t);
    t.appendChild(el('h4', {text: horaMin(f.minuto * 60000) + ' · minuto de reloj'}));
    [['DynamoDB', f.nivel_servidor ? 'N' + f.nivel_servidor : '—'], ['Regla', f.nivel_regla ? 'N' + f.nivel_regla : '—'],
      ['Cliente', f.niveles_cliente.length ? 'N' + f.niveles_cliente.join(' · N') : '—'],
      ['Peticiones', String(d.pet)], ['Errores', String(d.err)]].forEach(function (p) {
      t.appendChild(el('div', {}, [el('b', {text: p[1]}), el('span', {text: p[0]})]));
    });
    t.hidden = false;
    var px = (ev.clientX || caja.left + caja.width / 2) - caja.left, py = (ev.clientY || caja.top + 40) - caja.top;
    t.style.left = Math.min(Math.max(px + 14, 0), caja.width - 210) + 'px';
    t.style.top = Math.max(py - 20, 0) + 'px';
  }

  function pintarCoherencia(s) {
    var c = s.coherencia, a = $('coherencia'), b = $('cohRegla');
    a.className = 'coh' + (c.minutos ? (c.todo_coincide ? ' si' : ' no') : '');
    a.textContent = c.minutos ? 'Cliente = DynamoDB en ' + c.coinciden + '/' + c.minutos + ' min' : '';
    b.className = 'coh' + (c.minutos_regla ? (c.regla_se_cumple ? ' si' : ' no') : '');
    b.textContent = c.minutos_regla ? 'Regla cumplida en ' + c.coinciden_regla + '/' + c.minutos_regla + ' min' : '';
  }

  /* ── 5 · Datos crudos (pestañas) ── */
  function filaVacia(tb, cols, texto) { tb.appendChild(el('tr', {}, [el('td', {colspan: cols, class: 'vacio', text: texto})])); }

  function pintarRespuestas(k) {
    $('cntResp').textContent = k.hechas;
    if (!cambio('resp', [k.hechas, k.inicio])) return;
    var tb = $('respuestas');
    vaciar(tb);
    if (!k.ultimas.length) { filaVacia(tb, 5, 'Sin respuestas todavía.'); iterMaxPrev = 0; return; }
    k.ultimas.forEach(function (it) {
      var nueva = iterMaxPrev && it.iteracion > iterMaxPrev;
      tb.appendChild(el('tr', {class: (it.nivel ? 'l' + it.nivel : '') + (nueva ? ' nueva' : '')}, [
        el('td', {class: 'n', text: it.iteracion}),
        el('td', {class: 'm', text: hora(it.ts)}),
        el('td', {class: 'm', text: it.error ? 'true' : 'false'}),
        el('td', {class: 'n' + (it.status >= 500 ? ' st5' : ''), text: it.status}),
        el('td', {class: 'msg', text: it.mensaje || '(sin respuesta)'})
      ]));
    });
    iterMaxPrev = k.ultimas[0].iteracion;
  }

  function pintarDynamo(s) {
    var items = s.servidor.minutos;
    $('cntDb').textContent = s.servidor.lectura ? items.length : '—';
    if (!cambio('db', [items, s.servidor.lectura])) return;
    var tb = $('filasDb');
    vaciar(tb);
    if (!items.length) {
      filaVacia(tb, 7, s.servidor.lectura ? 'Sin ítems en la ventana observada: cada minuto con tráfico crea uno.'
        : 'Sin permiso de lectura de DynamoDB: ' + (s.servidor.motivo || ''));
      return;
    }
    items.slice().reverse().forEach(function (it) {
      tb.appendChild(el('tr', {}, [
        el('td', {class: 'm', text: it.pk}),
        el('td', {class: 'm', text: horaMin(it.minuto * 60000)}),
        el('td', {}, [tag(it.nivel)]),
        el('td', {class: 'n', text: it.peticiones}),
        el('td', {class: 'n' + (it.errores ? ' st5' : ''), text: it.errores}),
        el('td', {class: 'm', text: it.degradado_en != null ? horaMin(it.degradado_en * 60000) : '—'}),
        el('td', {class: 'm', text: it.ttl ? fechaHora(it.ttl) : '—'})
      ]));
    });
  }

  function pintarEventos(s) {
    var sv_ = s.servidor;
    $('cntEv').textContent = sv_.lectura ? sv_.eventos.length : '—';
    if (!cambio('ev', [sv_.eventos, sv_.lectura, sv_.error])) return;
    var ol = $('eventos');
    vaciar(ol);
    var vacio = function (t) { ol.appendChild(el('li', {class: 'vacio', text: t})); };
    if (!sv_.lectura) return vacio('Sin permiso de lectura de CloudWatch: ' + (sv_.motivo || ''));
    if (sv_.error) return vacio(sv_.error);
    if (!sv_.eventos.length) return vacio('Sin cambios de nivel registrados.');
    sv_.eventos.forEach(function (e) {
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
      ol.appendChild(el('li', {class: clase}, [el('span', {class: 'h', text: hora(e.ts)}), el('span', {class: 't', text: titulo}), el('span', {class: 'd', text: detalle})]));
    });
  }

  function pintarMinutos(s) {
    var filas = s.coherencia.filas;
    if (!cambio('min', [filas, s.servidor.lectura])) return;
    var tb = $('filasMin');
    vaciar(tb);
    if (!filas.length) return filaVacia(tb, 7, 'Sin minutos con tráfico.');
    filas.forEach(function (f) {
      var cli = el('td');
      if (!f.niveles_cliente.length) cli.textContent = '—';
      f.niveles_cliente.forEach(function (n) { cli.appendChild(tag(n)); cli.appendChild(document.createTextNode(' ')); });
      tb.appendChild(el('tr', {}, [
        el('td', {class: 'm', text: horaMin(f.minuto * 60000)}),
        el('td', {class: 'n', text: s.servidor.lectura ? f.errores : f.errores_cliente}),
        el('td', {class: 'n', text: f.peticiones || '—'}),
        el('td', {}, [tag(f.nivel_servidor)]), el('td', {}, [tag(f.nivel_regla)]), cli,
        el('td', {class: 'm', text: f.iteraciones || '—'})
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
      '. La regla se verifica con lo que ve el k6; faltan el nivel del servidor, DynamoDB y los logs.';
    $('url').textContent = e.url || 'sin despliegue: corra scripts/deploy.sh ' + (e.activo === 'aws' ? 'aws' : 'localstack');
    $('url').title = e.url || '';
    $('bReiniciar').hidden = !e.permite_reinicio;
    ['bOk', 'bErr'].forEach(function (id) { $(id).disabled = !e.url; });
    var hay = !!s.k6.inicio;
    document.querySelectorAll('.descargas a').forEach(function (a) {
      a.setAttribute('aria-disabled', hay ? 'false' : 'true');
      a.href = hay ? '/api/descargas/' + a.dataset.tipo : '#';
    });
    $('notaDescargas').textContent = !hay ? '' : s.k6.estado === 'corriendo' ? 'La corrida sigue en curso: lo que descargue ahora es parcial.'
      : 'Evidencia de la corrida del ' + hora(s.k6.inicio) + '. El ZIP trae además el resumen y el diff que prueba que solo cambió la URL.';
    mostrarError(s.servidor.error ? 'No se pudo leer el servidor (' + e.activo + '): ' + s.servidor.error : '');
  }

  async function refrescar() {
    if (ocupado) return;
    ocupado = true;
    try {
      var s = await api('GET', '/api/estado');
      ultimo = s;
      pintarEntorno(s);
      var n = pintarNivel(s);
      pintarFlujo(s, n); pintarUltimoEvento(s);
      pintarK6(s.k6); pintarGuion(s);
      pintarCoherencia(s); pintarGrafica(s);
      pintarRespuestas(s.k6); pintarDynamo(s); pintarEventos(s); pintarMinutos(s);
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
      viaje(n ? +n[1] : null, error);
      vaciar(caja);
      caja.appendChild(el('span', {class: r.status < 500 ? 'ok' : 'mal', text: r.status + ' · ' + r.ms + ' ms'}));
      caja.appendChild(document.createTextNode(' · ' + r.mensaje));
    };
  }
  accion($('bOk'), manual(false));
  accion($('bErr'), manual(true));
  accion($('bReiniciar'), async function () {
    if (!confirm('¿Borrar el estado por minuto de LocalStack? El sistema vuelve a N1.')) return;
    await api('POST', '/api/reiniciar');
  });
  document.querySelectorAll('.seg-ctl button').forEach(function (b) {
    accion(b, function () { ultimaManual = null; hechasPrev = null; nivelPrev = null; iterMaxPrev = 0; firmas = {};
      return api('POST', '/api/entorno', {entorno: b.dataset.entorno}); });
  });
  document.querySelectorAll('.pestanas button').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.pestanas button').forEach(function (o) {
        o.setAttribute('aria-selected', o === b ? 'true' : 'false');
        $(o.dataset.p).hidden = o !== b;
      });
    });
  });
  $('bTema').addEventListener('click', function () {
    var f = document.documentElement.getAttribute('data-theme');
    var oscuro = f === 'dark' || (!f && matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.setAttribute('data-theme', oscuro ? 'light' : 'dark');
    if (ultimo) pintarGrafica(ultimo, true);
  });
  window.addEventListener('resize', function () { if (ultimo) pintarGrafica(ultimo); });
  setInterval(function () { $('reloj').textContent = new Date().toLocaleTimeString('es-CO', {hour12: false}); }, 1000);

  refrescar();
  setInterval(refrescar, 1500);
})();
