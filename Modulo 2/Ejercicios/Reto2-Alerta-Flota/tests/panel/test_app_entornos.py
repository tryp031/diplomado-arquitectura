"""El switch local ↔ AWS del panel: lo que cambia y, sobre todo, lo que NO debe mezclarse."""
import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from panel.agregador import Agregador, LectorIncremental
from panel.app import create_app
from panel.corridas import Historial
from panel.entornos import EntornoAws
from tests.panel.test_app import DockerFalso, K6Falso

URL_AWS = "https://api.ejemplo/prod/event-notification"


class LectorFalso:
    """Lo que entregaría CloudWatch, ya convertido en (réplica, registro)."""

    def __init__(self, registros=()):
        self.registros, self.error, self.reiniciado = list(registros), None, 0

    def leer(self):
        registros, self.registros = self.registros, []
        return registros

    def reiniciar(self):
        self.reiniciado += 1


class SqsFalso:
    def get_queue_attributes(self, QueueUrl, AttributeNames):
        return {"Attributes": {k: "0" for k in AttributeNames}}


class LogsFalso:
    def __init__(self):
        self.pedidos = []

    def filter_log_events(self, **pedido):
        self.pedidos.append(pedido)
        registro = {"ts": "2026-10-12T20:00:01.000-05:00", "service": "ingesta", "event": "EVENT_RECEIVED"}
        return {"events": [{"eventId": "1", "timestamp": pedido["startTime"], "logStreamName": "s",
                            "message": json.dumps(registro)}]} if pedido["logGroupName"].endswith("ingesta") else {"events": []}


def _registro_aws(evento, **campos):
    return ("ingest-abc", {"ts": datetime.now(timezone.utc).isoformat(), "service": "ingest", "event": evento, **campos})


@pytest.fixture
def panel(tmp_path):
    (tmp_path / "nginx").mkdir()
    (tmp_path / "ingest-1.log").write_text(json.dumps(
        {"ts": datetime.now(timezone.utc).isoformat(), "service": "ingest", "event": "EVENT_RECEIVED", "event_id": "local"}
    ) + "\n", encoding="utf-8")
    enviados = []

    def destino(request):
        enviados.append(str(request.url))
        return httpx.Response(200, json={"event_id": "x", "status": "accepted"})

    async def redis_info():
        return {"ok": True, "stream": 0, "pendientes": 0, "dlq": 0}

    async def redis_vaciar():
        enviados.append("redis vaciado")

    lector_aws = LectorFalso([_registro_aws("EVENT_RECEIVED", event_id="nube")])
    k6_local, k6_aws, logs = K6Falso(), K6Falso(), LogsFalso()
    aws = EntornoAws(logs=logs, sqs=SqsFalso(), grupos={"ingest": "/aws/lambda/reto2-ingesta"},
                     cola_url="cola", dlq_url="dlq", k6=k6_aws, gateway_url=URL_AWS, lector=lector_aws)
    historial = Historial(tmp_path / "corridas.json")
    app = create_app(
        agregador=Agregador(), lector_servicio=LectorIncremental(tmp_path, ("ingest-*.log",)),
        lector_nginx=LectorIncremental(tmp_path / "nginx", ("gateway-access.log",)),
        redis_info=redis_info, redis_vaciar=redis_vaciar, docker=DockerFalso(), k6=k6_local,
        gateway=httpx.AsyncClient(transport=httpx.MockTransport(destino)),
        gateway_url="http://gateway/events", log_dir=tmp_path, historial=historial, aws=aws,
    )
    cliente = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://panel")
    return cliente, k6_local, k6_aws, enviados, historial, lector_aws, logs


async def test_arranca_en_local_y_anuncia_que_aws_esta_disponible(panel):
    cliente, *_ = panel
    async with cliente:
        estado = (await cliente.get("/api/estado")).json()
    assert estado["entorno"]["activo"] == "local"
    assert estado["entorno"]["aws_disponible"] is True
    assert estado["eventos"]["recibidos"] == 1  # el log local


async def test_al_cambiar_a_aws_lee_cloudwatch_y_no_mezcla_lo_local(panel):
    cliente, _, _, _, _, lector_aws, _ = panel
    async with cliente:
        await cliente.get("/api/estado")
        assert (await cliente.post("/api/entorno", json={"entorno": "aws"})).status_code == 200
        estado = (await cliente.get("/api/estado")).json()
    assert estado["entorno"] == {"activo": "aws", "gestionado": True, "error": None,
                                 "aws_disponible": True, "aws_motivo": None}
    assert estado["eventos"]["recibidos"] == 1  # solo el de la nube: la ventana se reinició
    assert estado["smtp"] == {"host": "Amazon SES", "local": False}
    assert estado["contenedores"] == {} and estado["docker_error"] is None
    assert lector_aws.reiniciado == 1


async def test_la_carga_y_el_emergency_van_contra_el_entorno_activo(panel):
    cliente, k6_local, k6_aws, enviados, historial, *_ = panel
    async with cliente:
        await cliente.post("/api/entorno", json={"entorno": "aws"})
        await cliente.post("/api/emergencia")
        corrida = (await cliente.post("/api/carga", json={"modo": "profesor"})).json()["corrida"]
    assert enviados == [URL_AWS]
    assert k6_aws.iniciados and not k6_local.iniciados
    assert historial.buscar(corrida)["entorno"] == "aws"
    assert historial.buscar(corrida)["smtp"] == "Amazon SES"


async def test_no_cambia_de_entorno_con_una_carga_en_curso(panel):
    cliente, k6_local, *_ = panel
    k6_local.ocupado = True
    async with cliente:
        respuesta = await cliente.post("/api/entorno", json={"entorno": "aws"})
    assert respuesta.status_code == 409


async def test_sin_configuracion_de_aws_el_switch_explica_por_que(tmp_path):
    async def redis_info():
        return {"ok": True}

    app = create_app(agregador=Agregador(), lector_servicio=LectorIncremental(tmp_path, ()),
                     lector_nginx=LectorIncremental(tmp_path, ()), redis_info=redis_info, docker=DockerFalso(),
                     k6=K6Falso(), gateway=httpx.AsyncClient(), gateway_url="http://gateway/events",
                     aws_motivo="Falta AWS_API_URL")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://panel") as cliente:
        estado = (await cliente.get("/api/estado")).json()
        respuesta = await cliente.post("/api/entorno", json={"entorno": "aws"})
    assert estado["entorno"]["aws_disponible"] is False
    assert estado["entorno"]["aws_motivo"] == "Falta AWS_API_URL"
    assert respuesta.status_code == 400 and "AWS_API_URL" in respuesta.json()["error"]


async def test_en_aws_no_se_apagan_servicios(panel):
    cliente, *_ = panel
    async with cliente:
        await cliente.post("/api/entorno", json={"entorno": "aws"})
        respuesta = await cliente.post("/api/servicios/notifier/apagar")
    assert respuesta.status_code == 400


async def test_borrar_datos_en_aws_no_toca_redis_ni_las_corridas_locales(panel):
    cliente, _, _, enviados, historial, *_ = panel
    ahora = datetime.now(timezone.utc)
    historial.abrir(ahora, "profesor", "mailpit", "local")
    historial.abrir(ahora, "profesor", "Amazon SES", "aws")
    async with cliente:
        await cliente.post("/api/entorno", json={"entorno": "aws"})
        assert (await cliente.post("/api/datos/limpiar")).status_code == 200
    assert "redis vaciado" not in enviados
    assert [c["entorno"] for c in historial.listar()] == ["local"]


async def test_los_logs_de_una_corrida_salen_del_entorno_donde_corrio(panel):
    cliente, _, _, _, historial, _, logs = panel
    inicio = datetime.now(timezone.utc) - timedelta(minutes=2)
    n = historial.abrir(inicio, "profesor", "Amazon SES", "aws")["n"]
    historial.actualizar(n, fin=(inicio + timedelta(seconds=30)).isoformat())
    async with cliente:  # se mira local, pero la corrida es de AWS
        respuesta = await cliente.get(f"/api/corridas/{n}/logs", params={"formato": "csv"})
    assert respuesta.status_code == 200
    assert "-aws-" in respuesta.headers["content-disposition"]
    assert logs.pedidos and "EVENT_RECEIVED" in respuesta.text
