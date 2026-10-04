from medir import analizar

K6 = {
    "started_at": "2026-10-13T04:00:00.000Z",   # 23:00:00 -05:00
    "ended_at": "2026-10-13T04:00:28.000Z",     # 23:00:28 -05:00
    "metrics": {"http_reqs": 1000, "http_req_failed_rate": 0.0,
                "http_req_duration_p95_ms": 12.5, "checks_rate": 1.0},
}


def reg(ts, event, **extra):
    return {"ts": f"2026-10-12T{ts}-05:00", "event": event, **extra}


SERVICIO = [
    reg("22:59:00.000", "EMAIL_SENT", event_id="viejo", ms_since_received=10),  # corrida anterior
    reg("23:00:01.000", "EVENT_RECEIVED", event_id="p1"),
    reg("23:00:02.000", "EVENT_RECEIVED", event_id="p2"),
    reg("23:00:03.000", "EVENT_RECEIVED", event_id="p3"),
    reg("23:00:27.900", "EMERGENCY_RECEIVED", event_id="e1"),
    reg("23:00:27.901", "EMERGENCY_ENQUEUED", event_id="e1"),
    reg("23:00:30.500", "EMAIL_SENT", event_id="e1", ms_since_received=2600),
]

# 1791864000 = 2026-10-13T04:00:00Z; el primer registro cae antes de la ventana.
NGINX = [{"msec": 1791864000.0 + s, "status": st}
         for s, st in [(-100, 200), (1, 200), (2, 200), (3, 200), (4, 429), (27.9, 200)]]


def test_reporte_de_una_corrida():
    r = analizar(SERVICIO, NGINX, K6)
    assert r.eventos_recibidos == 4
    assert r.emergencias_recibidas == 1
    assert r.emergencias_encoladas == 1
    assert r.correos_enviados == 1
    assert r.correos_dlq == 0
    assert r.recepcion_a_envio_max_ms == 2600
    assert r.fin_k6_a_ultimo_correo_s == 2.5
    # última petición en nginx: 23:00:27.900 → correo 23:00:30.500
    assert r.ultima_peticion_a_ultimo_correo_s == 2.6
    assert (r.nginx_total, r.nginx_429, r.nginx_otros_errores) == (5, 1, 0)
    assert (r.k6_peticiones, r.k6_p95_ms) == (1000, 12.5)


def test_sin_correos_la_medida_queda_vacia():
    r = analizar([reg("23:00:01.000", "EVENT_RECEIVED", event_id="p1")], [], K6)
    assert r.correos_enviados == 0
    assert r.fin_k6_a_ultimo_correo_s is None
    assert r.ultima_peticion_a_ultimo_correo_s is None
    assert r.recepcion_a_envio_max_ms is None
