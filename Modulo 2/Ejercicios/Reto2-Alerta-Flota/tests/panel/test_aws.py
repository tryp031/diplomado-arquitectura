import json
import time
from datetime import datetime, timedelta, timezone

from panel.agregador import Agregador
from panel.aws import LectorCloudWatch, estado_sqs, leer_ventana, peticiones_desde_ingesta

COLOMBIA = timezone(timedelta(hours=-5))
T0 = datetime(2026, 10, 12, 20, 0, 0, tzinfo=COLOMBIA)


def linea(segundo, evento, rol="ingesta", eid=None, stream="2026/10/12/[$LATEST]abcdef123456", **campos):
    """Un evento de CloudWatch tal como lo devuelve FilterLogEvents, con el JSON de la Lambda."""
    momento = T0 + timedelta(seconds=segundo)
    registro = {"ts": momento.isoformat(timespec="milliseconds"), "service": rol, "event": evento, **campos}
    return {"eventId": eid or f"{evento}-{segundo}", "timestamp": int(momento.timestamp() * 1000),
            "logStreamName": stream, "message": json.dumps(registro)}


class LogsFalso:
    """filter_log_events con paginación: devuelve lo del grupo dentro de [startTime, endTime]."""

    def __init__(self, por_grupo, por_pagina=2, falla=None):
        self.por_grupo, self.por_pagina, self.falla = por_grupo, por_pagina, falla
        self.llamadas = []

    def filter_log_events(self, logGroupName, startTime, endTime=None, nextToken=None):
        self.llamadas.append((logGroupName, startTime, endTime, nextToken))
        if self.falla:
            raise self.falla
        eventos = [e for e in self.por_grupo.get(logGroupName, [])
                   if e["timestamp"] >= startTime and (endTime is None or e["timestamp"] <= endTime)]
        inicio = int(nextToken or 0)
        pagina = eventos[inicio:inicio + self.por_pagina]
        siguiente = inicio + self.por_pagina
        return {"events": pagina, **({"nextToken": str(siguiente)} if siguiente < len(eventos) else {})}


GRUPOS = {"ingest": "/aws/lambda/reto2-ingesta", "notifier": "/aws/lambda/reto2-notifier"}


def lector(logs, ahora_s, **opciones):
    reloj = {"t": (T0 + timedelta(seconds=ahora_s)).timestamp()}
    return LectorCloudWatch(logs, GRUPOS, reloj=lambda: reloj["t"], segundo_plano=False, **opciones), reloj


def test_lee_ambos_grupos_ordenado_por_hora_y_con_los_roles_del_panel():
    logs = LogsFalso({
        GRUPOS["notifier"]: [linea(3, "EMAIL_SENT", rol="notifier", event_id="e1", attempt=1)],
        GRUPOS["ingest"]: [linea(1, "EMERGENCY_RECEIVED", event_id="e1", plate="ABC-123"),
                           linea(2, "EMERGENCY_ENQUEUED", event_id="e1")],
    })
    lec, _ = lector(logs, 60)
    registros = lec.leer()
    assert [r["event"] for _, r in registros] == ["EMERGENCY_RECEIVED", "EMERGENCY_ENQUEUED", "EMAIL_SENT"]
    assert {r["service"] for _, r in registros} == {"ingest", "notifier"}  # «ingesta» → rol del panel
    assert registros[0][0] == "ingest-abcdef"  # la réplica es la instancia (log stream)


def test_retiene_lo_mas_reciente_hasta_que_pase_la_retencion():
    # Riesgo: el EMAIL_SENT llega a CloudWatch antes que su EMERGENCY_RECEIVED y el agregador lo pierde.
    eventos = {GRUPOS["ingest"]: [linea(1, "EVENT_RECEIVED", event_id="p1"), linea(9, "EVENT_RECEIVED", event_id="p2")]}
    lec, reloj = lector(LogsFalso(eventos), 10, retencion_s=5)
    assert [r["event_id"] for _, r in lec.leer()] == ["p1"]  # p2 tiene 1 s: todavía espera
    reloj["t"] += 5
    assert [r["event_id"] for _, r in lec.leer()] == ["p2"]  # sale después, una sola vez


def test_no_repite_lineas_aunque_las_consultas_se_solapen():
    eventos = {GRUPOS["ingest"]: [linea(1, "EVENT_RECEIVED", event_id="p1")]}
    lec, reloj = lector(LogsFalso(eventos), 30)
    assert len(lec.leer()) == 1
    reloj["t"] += 3
    assert lec.leer() == []


def test_entrega_una_linea_que_llega_tarde_dentro_del_solape():
    eventos = {GRUPOS["ingest"]: [linea(10, "EVENT_RECEIVED", event_id="p1")]}
    logs = LogsFalso(eventos)
    lec, reloj = lector(logs, 30)
    lec.leer()
    eventos[GRUPOS["ingest"]].append(linea(8, "EVENT_RECEIVED", eid="tarde", event_id="p0"))  # ingesta lenta
    reloj["t"] += 3
    assert [r["event_id"] for _, r in lec.leer()] == ["p0"]


def test_respeta_el_intervalo_entre_consultas_por_la_cuota_de_cloudwatch():
    logs = LogsFalso({})
    lec, reloj = lector(logs, 30, intervalo_s=2)
    lec.leer()
    llamadas = len(logs.llamadas)
    reloj["t"] += 1
    lec.leer()
    assert len(logs.llamadas) == llamadas  # dentro del intervalo no se consulta


def test_recorre_todas_las_paginas():
    eventos = {GRUPOS["ingest"]: [linea(i, "EVENT_RECEIVED", event_id=f"p{i}") for i in range(5)]}
    lec, _ = lector(LogsFalso(eventos, por_pagina=2), 60)
    assert len(lec.leer()) == 5


def test_ignora_las_lineas_de_lambda_que_no_son_json():
    reporte = {"eventId": "r", "timestamp": int(T0.timestamp() * 1000), "logStreamName": "x",
               "message": "REPORT RequestId: 1 Duration: 3.1 ms"}
    lec, _ = lector(LogsFalso({GRUPOS["ingest"]: [reporte, linea(1, "EVENT_RECEIVED", event_id="p1")]}), 60)
    assert len(lec.leer()) == 1


def test_un_error_de_aws_no_rompe_y_queda_visible():
    lec, _ = lector(LogsFalso({}, falla=RuntimeError("ExpiredToken")), 60)
    assert lec.leer() == []
    assert "ExpiredToken" in lec.error


def test_las_lineas_de_aws_alimentan_el_agregador_igual_que_las_locales():
    # El punto del diseño: misma forma de log → el agregador y la medida de la rúbrica no cambian.
    logs = LogsFalso({
        GRUPOS["ingest"]: [linea(1, "EVENT_RECEIVED", event_id="p1"),
                           linea(2, "EMERGENCY_RECEIVED", event_id="e1", plate="FTE-710"),
                           linea(2.1, "EMERGENCY_ENQUEUED", event_id="e1")],
        GRUPOS["notifier"]: [linea(3.8, "EMAIL_SENT", rol="notifier", event_id="e1", attempt=1)],
    })
    lec, _ = lector(logs, 60)
    registros = lec.leer()
    agregador = Agregador()
    agregador.ingerir_servicio(registros)
    agregador.ingerir_nginx(peticiones_desde_ingesta(registros))
    resumen = agregador.resumen(T0 + timedelta(seconds=60))
    assert resumen["http"]["aceptadas"] == 2  # p1 + e1 (el Emergency se cuenta una vez)
    assert resumen["eventos"]["enviadas"] == 1
    assert resumen["medida_rubrica"]["segundos"] == 1.7  # última petición (2.1) → correo (3.8)


def test_peticiones_cuentan_el_503_de_un_emergency_no_encolado():
    registros = [("ingest-a", {"ts": T0.isoformat(), "service": "ingest", "event": "EMERGENCY_RECEIVED"}),
                 ("ingest-a", {"ts": T0.isoformat(), "service": "ingest", "event": "EMERGENCY_ENQUEUE_FAILED"}),
                 ("notifier-a", {"ts": T0.isoformat(), "service": "notifier", "event": "EMAIL_SENT"})]
    assert [p["status"] for p in peticiones_desde_ingesta(registros)] == [503]


def test_leer_ventana_trae_solo_lo_de_la_corrida():
    logs = LogsFalso({GRUPOS["ingest"]: [linea(1, "EVENT_RECEIVED", event_id="p1"),
                                         linea(100, "EVENT_RECEIVED", event_id="fuera")]})
    pares = leer_ventana(logs, GRUPOS, T0, T0 + timedelta(seconds=30))
    assert [r["event_id"] for _, r in pares] == ["p1"]


class SqsFalso:
    def __init__(self, falla=False):
        self.falla = falla

    def get_queue_attributes(self, QueueUrl, AttributeNames):
        if self.falla:
            raise RuntimeError("AccessDenied")
        valores = {"cola": {"ApproximateNumberOfMessages": "3", "ApproximateNumberOfMessagesNotVisible": "1"},
                   "dlq": {"ApproximateNumberOfMessages": "2"}}[QueueUrl]
        return {"Attributes": {k: valores[k] for k in AttributeNames}}


def test_estado_sqs_usa_el_mismo_formato_que_redis():
    assert estado_sqs(SqsFalso(), "cola", "dlq") == {"ok": True, "stream": 3, "pendientes": 1, "dlq": 2}


def test_estado_sqs_sin_configurar_o_sin_permiso():
    assert estado_sqs(SqsFalso(), None, "dlq")["ok"] is False
    assert "AccessDenied" in estado_sqs(SqsFalso(falla=True), "cola", "dlq")["error"]


# --- Regresión 12/10 (HEA-587): el correo llegó a Gmail, pero el panel dejó la emergencia en «recibida».
def _linea_servicio(segundo, evento, **campos):
    momento = T0 + timedelta(seconds=segundo)
    rol = "notifier" if evento.startswith("EMAIL") else "ingest"
    return (f"{rol}-a", {"ts": momento.isoformat(timespec="milliseconds"), "service": rol, "event": evento,
                         "event_id": "e1", "plate": "HEA-587", **campos})


def test_un_emergency_received_repetido_no_borra_el_recorrido():
    agregador = Agregador()
    agregador.ingerir_servicio([_linea_servicio(0, "EMERGENCY_RECEIVED"), _linea_servicio(0.3, "EMERGENCY_ENQUEUED"),
                                _linea_servicio(0.7, "EMAIL_SENT", attempt=1)])
    agregador.ingerir_servicio([_linea_servicio(0, "EMERGENCY_RECEIVED")])  # entregado otra vez
    emergencia = agregador.resumen(T0 + timedelta(seconds=60))["emergencias"][0]
    assert emergencia["estado"] == "enviada" and emergencia["ms_envio"] == 700


def test_un_correo_que_llega_antes_que_su_emergency_no_se_pierde():
    # CloudWatch no garantiza el orden entre dos grupos de logs: el notifier puede aparecer primero.
    agregador = Agregador()
    agregador.ingerir_servicio([_linea_servicio(0.7, "EMAIL_SENT", attempt=1)])
    agregador.ingerir_servicio([_linea_servicio(0, "EMERGENCY_RECEIVED"), _linea_servicio(0.3, "EMERGENCY_ENQUEUED")])
    resumen = agregador.resumen(T0 + timedelta(seconds=60))
    assert resumen["emergencias"][0]["estado"] == "enviada"
    assert resumen["eventos"]["enviadas"] == 1


def test_dos_consultas_simultaneas_no_entregan_dos_veces_la_misma_linea():
    import threading
    eventos = {GRUPOS["ingest"]: [linea(1, "EMERGENCY_RECEIVED", event_id="e1")]}

    class LogsLento(LogsFalso):
        def filter_log_events(self, **pedido):
            time.sleep(0.05)  # ambas consultas quedan en vuelo a la vez
            return super().filter_log_events(**pedido)

    lec = LectorCloudWatch(LogsLento(eventos), GRUPOS, intervalo_s=0, segundo_plano=False,
                           reloj=lambda: (T0 + timedelta(seconds=60)).timestamp())
    entregados = []
    hilos = [threading.Thread(target=lambda: entregados.extend(lec.leer())) for _ in range(2)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    assert len(entregados) == 1


def test_en_segundo_plano_leer_no_espera_a_cloudwatch():
    # Regresión 12/10: /api/estado tardaba 5-6 s porque esperaba la paginación de CloudWatch.
    eventos = {GRUPOS["ingest"]: [linea(1, "EVENT_RECEIVED", event_id="p1")]}

    class LogsLento(LogsFalso):
        def filter_log_events(self, **pedido):
            time.sleep(0.3)
            return super().filter_log_events(**pedido)

    lec = LectorCloudWatch(LogsLento(eventos), GRUPOS, intervalo_s=0,
                           reloj=lambda: (T0 + timedelta(seconds=60)).timestamp())
    inicio = time.perf_counter()
    assert lec.leer() == []  # vuelve de inmediato: la consulta sigue en su hilo
    assert time.perf_counter() - inicio < 0.1
    time.sleep(0.8)
    assert [r["event_id"] for _, r in lec.leer()] == ["p1"]  # y lo entrega en la siguiente lectura
