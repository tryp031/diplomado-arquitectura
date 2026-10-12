import json
from datetime import datetime, timedelta, timezone

from panel.agregador import Agregador, LectorIncremental, calificar

T0 = datetime(2026, 10, 13, 4, 0, 0, tzinfo=timezone.utc)  # 23:00:00 -05:00
EPOCH0 = T0.timestamp()


def ts(segundos: float) -> str:
    return (T0 + timedelta(seconds=segundos)).astimezone(timezone(timedelta(hours=-5))).isoformat(timespec="milliseconds")


def svc(segundos, event, service="ingest", **extra):
    return {"ts": ts(segundos), "service": service, "event": event, **extra}


def nginx(segundos, status=200, uri="/events"):
    return {"msec": EPOCH0 + segundos, "status": status, "uri": uri}


# --- LectorIncremental ----------------------------------------------------------------

def escribir(path, *registros, final="\n"):
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(r) for r in registros) + final)


def test_lector_devuelve_solo_lo_nuevo_con_el_nombre_del_archivo(tmp_path):
    archivo = tmp_path / "ingest-abc.log"
    escribir(archivo, {"n": 1})
    lector = LectorIncremental(tmp_path, ("ingest-*.log",))
    assert lector.leer() == [("ingest-abc", {"n": 1})]
    assert lector.leer() == []
    escribir(archivo, {"n": 2})
    assert lector.leer() == [("ingest-abc", {"n": 2})]


def test_lector_espera_la_linea_a_medio_escribir(tmp_path):
    archivo = tmp_path / "ingest-abc.log"
    archivo.write_text('{"n": 1}\n{"n": ', encoding="utf-8")
    lector = LectorIncremental(tmp_path, ("ingest-*.log",))
    assert lector.leer() == [("ingest-abc", {"n": 1})]
    with archivo.open("a", encoding="utf-8") as f:
        f.write('2}\n')
    assert lector.leer() == [("ingest-abc", {"n": 2})]


def test_lector_vuelve_a_empezar_si_el_archivo_se_trunca(tmp_path):
    archivo = tmp_path / "ingest-abc.log"
    escribir(archivo, {"n": 1}, {"n": 2})
    lector = LectorIncremental(tmp_path, ("ingest-*.log",))
    lector.leer()
    archivo.write_text('{"n": 3}\n', encoding="utf-8")
    assert lector.leer() == [("ingest-abc", {"n": 3})]


# --- Agregador -------------------------------------------------------------------------

def corrida():
    a = Agregador()
    a.ingerir_nginx([nginx(-50), nginx(1), nginx(1.5), nginx(2, 429), nginx(2, 200, "/health"), nginx(27.9)])
    a.ingerir_servicio([
        ("ingest-a", svc(1, "EVENT_RECEIVED", event_id="p1")),
        ("ingest-b", svc(1.5, "EVENT_RECEIVED", event_id="p2")),
        ("ingest-a", svc(27.9, "EMERGENCY_RECEIVED", event_id="e1", plate="VFH-600")),
        ("ingest-a", svc(27.901, "EMERGENCY_ENQUEUED", event_id="e1", plate="VFH-600")),
        ("notifier-x", svc(28.5, "EMAIL_RETRY", service="notifier", event_id="e1", attempt=1, error="SMTPConnectError: x")),
        ("notifier-x", svc(30.5, "EMAIL_SENT", service="notifier", event_id="e1", attempt=2, ms_since_received=2600)),
    ])
    return a


def test_cuenta_peticiones_sin_health_checks():
    r = corrida().resumen(T0 + timedelta(seconds=31))
    assert r["http"] == {"total": 5, "aceptadas": 4, "rechazadas_429": 1, "otros_errores": 0}


def test_sigue_cada_emergencia_de_punta_a_punta():
    r = corrida().resumen(T0 + timedelta(seconds=31))
    [em] = r["emergencias"]
    assert (em["event_id"], em["placa"], em["estado"], em["intentos"]) == ("e1", "VFH-600", "enviada", 2)
    assert em["ms_encolada"] == 1
    assert em["ms_envio"] == 2600
    assert r["eventos"]["emergencias"] == 1
    assert r["eventos"]["enviadas"] == 1
    assert r["eventos"]["recibidos"] == 3
    assert r["por_replica"] == {"ingest-a": 2, "ingest-b": 1}


def test_medida_de_la_rubrica_desde_la_ultima_peticion():
    medida = corrida().resumen(T0 + timedelta(seconds=31))["medida_rubrica"]
    assert medida["segundos"] == 2.6
    assert (medida["nivel"], medida["puntos"]) == ("good", 2.5)


def test_reiniciar_la_ventana_descarta_lo_anterior():
    a = corrida()
    a.reiniciar(T0 + timedelta(seconds=40))
    a.ingerir_nginx([nginx(41)])
    a.ingerir_servicio([("ingest-a", svc(20, "EVENT_RECEIVED", event_id="viejo"))])
    r = a.resumen(T0 + timedelta(seconds=42))
    assert r["http"]["total"] == 1
    assert r["eventos"]["recibidos"] == 0
    assert r["emergencias"] == [] and r["medida_rubrica"]["segundos"] is None


def test_serie_por_segundo_de_los_ultimos_60_s():
    serie = corrida().resumen(T0 + timedelta(seconds=31))["serie"]
    assert len(serie) == 60
    por_t = {p["t"]: p for p in serie}
    assert por_t[int(EPOCH0) + 2] == {"t": int(EPOCH0) + 2, "aceptadas": 0, "rechazadas": 1}
    assert por_t[int(EPOCH0) + 1]["aceptadas"] == 2


def test_feed_trae_lo_notable_mas_reciente_primero():
    feed = corrida().resumen(T0 + timedelta(seconds=31))["feed"]
    assert [f["evento"] for f in feed] == ["EMAIL_SENT", "EMAIL_RETRY", "EMERGENCY_RECEIVED"]


def test_calificar_con_los_cortes_de_la_rubrica():
    assert calificar(None) == {"segundos": None, "nivel": None, "puntos": None}
    assert calificar(-0.3)["puntos"] == 2.5  # correo antes de la última petición
    assert calificar(14.9)["puntos"] == 2.5
    assert calificar(15)["puntos"] == 1.5
    assert calificar(45.1) == {"segundos": 45.1, "nivel": "critical", "puntos": 0.5}


def test_feed_ordena_por_hora_aunque_lleguen_en_lotes_por_archivo():
    # Al ponerse al día, el lector entrega primero todo el ingest y luego todo el notifier.
    a = Agregador()
    a.ingerir_servicio([
        ("ingest-a", svc(1, "EMERGENCY_RECEIVED", event_id="e1")),
        ("ingest-a", svc(9, "EMERGENCY_RECEIVED", event_id="e2")),
        ("notifier-x", svc(2, "EMAIL_SENT", service="notifier", event_id="e1", attempt=1, ms_since_received=1000)),
    ])
    feed = a.resumen(T0 + timedelta(seconds=10))["feed"]
    assert [(f["evento"], f["event_id"]) for f in feed] == [
        ("EMERGENCY_RECEIVED", "e2"), ("EMAIL_SENT", "e1"), ("EMERGENCY_RECEIVED", "e1")]


# --- corrida: la medida pertenece a la carga, no a la ventana ---------------------------

def test_cerrar_la_corrida_excluye_un_emergency_manual_posterior():
    # Bug visto el 07/10: un Emergency manual tras la carga entraba en la medida y en «2/2».
    a = corrida()
    a.cerrar(T0 + timedelta(seconds=28))  # k6 terminó a los 28 s
    a.ingerir_nginx([nginx(40)])
    a.ingerir_servicio([
        ("ingest-a", svc(40, "EMERGENCY_RECEIVED", event_id="manual", plate="PNL-001")),
        ("notifier-x", svc(40.5, "EMAIL_SENT", service="notifier", event_id="manual", attempt=1)),
    ])
    r = a.resumen(T0 + timedelta(seconds=41))
    assert r["medida_rubrica"]["segundos"] == 2.6  # sigue siendo la de la carga
    assert r["eventos"]["emergencias"] == 1 and r["eventos"]["enviadas"] == 1
    assert r["http"]["total"] == 5
    assert r["ultima_peticion"] == (T0 + timedelta(seconds=27.9)).isoformat(timespec="milliseconds")
    fuera = next(e for e in r["emergencias"] if e["event_id"] == "manual")
    assert fuera["en_corrida"] is False
    assert next(e for e in r["emergencias"] if e["event_id"] == "e1")["en_corrida"] is True


def test_un_correo_de_la_carga_que_sale_despues_del_cierre_si_cuenta():
    # Un reintento puede terminar después de que k6 acabó: el correo sigue siendo de la carga.
    a = Agregador()
    a.ingerir_nginx([nginx(10)])
    a.ingerir_servicio([("ingest-a", svc(10, "EMERGENCY_RECEIVED", event_id="e1"))])
    a.cerrar(T0 + timedelta(seconds=11))
    a.ingerir_servicio([("notifier-x", svc(25, "EMAIL_SENT", service="notifier", event_id="e1", attempt=3))])
    assert a.resumen(T0 + timedelta(seconds=26))["medida_rubrica"]["segundos"] == 15.0


def test_reiniciar_reabre_la_corrida():
    a = corrida()
    a.cerrar(T0 + timedelta(seconds=28))
    a.reiniciar(T0 + timedelta(seconds=40))
    assert a.hasta is None


def test_procesados_cuenta_eventos_validados_y_emergencias_con_correo():
    # Un evento normal termina al validarse y registrarse; un Emergency, al enviarse su correo.
    r = corrida().resumen(T0 + timedelta(seconds=31))
    assert r["eventos"]["procesados"] == 3  # p1, p2 y e1 (correo enviado)


def test_emergencia_a_correo_es_el_peor_caso_de_la_corrida():
    a = Agregador()
    a.ingerir_servicio([
        ("ingest-a", svc(1, "EMERGENCY_RECEIVED", event_id="e1", plate="AAA-111")),
        ("ingest-a", svc(5, "EMERGENCY_RECEIVED", event_id="e2", plate="BBB-222")),
        ("notifier-x", svc(1.2, "EMAIL_SENT", service="notifier", event_id="e1", attempt=1)),
        ("notifier-x", svc(8, "EMAIL_SENT", service="notifier", event_id="e2", attempt=2)),
    ])
    peor = a.resumen(T0 + timedelta(seconds=9))["emergencia_a_correo"]
    assert peor == {"segundos": 3.0, "placa": "BBB-222"}
    assert Agregador().resumen(T0)["emergencia_a_correo"] == {"segundos": None, "placa": None}
