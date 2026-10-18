/* Panel Reto 3. Consulta /api/estado cada 1,5 s y pinta. Todo dato del servidor entra con
 * textContent, nunca con innerHTML: los mensajes vienen de la red. */
(function () {
  'use strict';
  var NOMBRES = {1: 'Full', 2: 'Degradado', 3: 'Mínimo'};
  var CAPS = {
    1: 'Valida, registra, análisis de riesgo y notificación.',
    2: 'Solo lo esencial: valida y registra. Análisis y notificación diferidos.',
    3: 'No procesa: responde el mensaje de operación mínima o de mantenimiento.'
  };
  var $ = function (id) { return document.getElementById(id); };
  var ultimo = null, ocupado = false;

  function el(tag, attrs, hijos) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') n.textContent = attrs[k]; else if (k === 'class') n.className = attrs[k]; else n.setAttribute(k, attrs[k]);
    });
    (hijos || []).forEach(function (h) { if (h) n.appendChild(h); });
    return n;
  }
  function vaciar(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function hora(valor) {
    var d = typeof valor === 'number' ? new Date(valor) : new Date(valor);
    return d.toLocaleTimeString('es-CO', {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false});
  }
  function horaMin(iso) {
    return new Date(iso).toLocaleTimeString('es-CO', {hour: '2-digit', minute: '2-digit', hour12: false});
  }

  async function api(metodo, ruta, cuerpo) {
    var r = await fetch(ruta, {method: metodo, headers: {'Content-Type': 'application/json'},
      body: cuerpo ? JSON.stringify(cuerpo) : undefined});
    var datos = await r.json().catch(function () { return {}; });
    if (!r.ok) throw new Error(datos.error || ('HTTP ' + r.status));
    return datos;
  }
  function mostrarError(msg) {
    var e = $('errorGlobal');
    e.hidden = !msg;
    e.textContent = msg || '';
  }

  /* ── Pintado ── */
  function pintarNivel(s) {
    var n = s.nivel.actual;
    $('tarjetaNivel').dataset.nivel = n || 0;
    $('nivelN').textContent = n ? 'N' + n : '—';
    $('nivelNom').textContent = n ? NOMBRES[n] : 'sin peticiones este minuto';
    var previos = s.servidor.minutos.filter(function (m) { return m.nivel; });
    var ult = previos[previos.length - 1];
    $('nivelCaps').textContent = n ? CAPS[n]
      : 'El nivel se decide con la primera petición de cada minuto de reloj.' +
        (ult ? ' Último nivel fijado: N' + ult.nivel + ' (' + horaMin(ult.minuto * 60000) + ').' : '');
    $('errPrev').textContent = s.nivel.errores_minuto_anterior;
    $('errAct').textContent = s.nivel.errores_minuto_actual;
    $('cuenta').textContent = s.reloj.segundos_a_proximo + ' s';
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
    var sec = $('secuencia');
    vaciar(sec);
    if (!k.secuencia.length) sec.appendChild(el('span', {class: 'vacio', text: '—'}));
    k.secuencia.forEach(function (n, i) {
      if (i) sec.appendChild(el('span', {class: 'flecha', text: '→'}));
      sec.appendChild(el('span', {class: 'chip l' + n, text: 'N' + n}));
    });
    Array.prototype.forEach.call($('veredicto').children, function (li) {
      // Un criterio se marca ✗ solo con la corrida cerrada; mientras corre, lo no cumplido aún está pendiente.
      // «Sin saltos 3 → 1» es al revés: se cumple desde el inicio y solo puede romperse.
      var v = k.veredicto[li.dataset.k];
      var cerrada = k.estado !== 'corriendo' && k.hechas > 0;
      if (li.dataset.k === 'sin_salto_3_a_1') li.className = k.hechas ? (v ? 'si' : 'no') : '';
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

  function pintarLinea(s) {
    var cont = $('linea'), filas = s.coherencia.filas;
    vaciar(cont);
    if (!filas.length) { cont.appendChild(el('p', {class: 'vacio', text: 'Sin minutos con tráfico en la ventana observada.'})); }
    var ahora = new Date(s.reloj.minuto).getTime();
    filas.forEach(function (f) {
      var n = f.nivel_servidor;
      var marca = f.coincide === null ? null : el('span', {class: 'c ' + (f.coincide ? 'si' : 'no'),
        text: f.coincide ? '✓' : '✗', title: f.coincide ? 'El k6 vio el mismo nivel' : 'El k6 vio: N' + f.niveles_cliente.join(', N')});
      cont.appendChild(el('div', {class: 'seg ' + (n ? 'l' + n : 'vacio-n') + (f.minuto * 60000 === ahora ? ' ahora' : '')}, [
        marca,
        el('b', {text: n ? 'N' + n : '—'}),
        el('span', {class: 'h', text: horaMin(f.minuto * 60000)}),
        el('span', {class: 'e', text: f.errores + ' err · ' + f.peticiones + ' pet'})
      ]));
    });
    var c = $('coherencia');
    c.className = 'coh' + (s.coherencia.minutos ? (s.coherencia.todo_coincide ? ' si' : ' no') : '');
    c.textContent = s.coherencia.minutos
      ? 'Cliente y servidor coinciden en ' + s.coherencia.coinciden + ' de ' + s.coherencia.minutos + ' minutos'
      : '';
  }

  function pintarEventos(s) {
    var ol = $('eventos');
    vaciar(ol);
    if (s.servidor.error) { ol.appendChild(el('li', {class: 'vacio', text: s.servidor.error})); return; }
    if (!s.servidor.eventos.length) { ol.appendChild(el('li', {class: 'vacio', text: 'Sin cambios de nivel registrados.'})); return; }
    s.servidor.eventos.forEach(function (e) {
      var titulo, detalle, clase;
      if (e.evento === 'CAMBIO_NIVEL') {
        titulo = 'N' + e.de + ' → N' + e.a + ' · ' + (e.motivo === 'degradacion' ? 'degradación' : 'recuperación');
        detalle = e.errores_minuto_anterior + ' errores en el minuto anterior · umbrales ' + e.umbrales.degradado + '/' + e.umbrales.minimo;
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
        b.title = e.aws_disponible ? 'Observar el despliegue en AWS (us-east-2)' : (e.aws_motivo || 'AWS no configurado');
      }
    });
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
      pintarEntorno(s); pintarNivel(s); pintarK6(s.k6); pintarLinea(s); pintarEventos(s);
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
      var caja = $('respManual');
      vaciar(caja);
      caja.appendChild(el('span', {class: 'st ' + (r.status < 500 ? 'ok' : 'mal'),
        text: r.status + ' · ' + r.ms + ' ms · error: ' + error}));
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
    accion(b, function () { return api('POST', '/api/entorno', {entorno: b.dataset.entorno}); });
  });
  $('bTema').addEventListener('click', function () {
    var f = document.documentElement.getAttribute('data-theme');
    var oscuro = f === 'dark' || (!f && matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.setAttribute('data-theme', oscuro ? 'light' : 'dark');
  });
  setInterval(function () { $('reloj').textContent = new Date().toLocaleTimeString('es-CO', {hour12: false}); }, 1000);

  refrescar();
  setInterval(refrescar, 1500);
})();
