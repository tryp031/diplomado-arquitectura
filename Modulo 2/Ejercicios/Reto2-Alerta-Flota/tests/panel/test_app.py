import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

from panel.agregador import Agregador, LectorIncremental
from panel.app import create_app


class DockerFalso:
    def __init__(self, falla=False):
        self.cambios = []
        self.falla = falla

    async def contenedores(self):
        if self.falla:
            raise httpx.ConnectError("sin socket")
        return {"ingest-1": {"servicio": "ingest", "estado": "running", "detalle": "Up"}}

    async def cambiar(self, servicio, accion):
        if servicio not in {"mailpit", "redis", "notifier"}:
            raise ValueError("no permitido")
        self.cambios.append((servicio, accion))


class K6Falso:
    def __init__(self):
        self.iniciados = []
        self.ocupado = False
        self.modo = None
        self.ultima = None  # (inicio, fin) de la última carga terminada

    async def iniciar(self, modo, *, emergencias):
        if modo not in {"rafaga", "ritmo", "profesor"}:
            raise ValueError("modo")
        if self.ocupado:
            raise RuntimeError("ocupado")
        self.iniciados.append((modo, emergencias))
        self.ocupado = True

    def resumen(self):
        return {"estado": "corriendo" if self.ocupado else "inactivo"}

    def ventana(self):
        return None if self.ocupado else self.ultima


@pytest.fixture
def entorno(tmp_path):
    (tmp_path / "nginx").mkdir()
    (tmp_path / "ingest-a.log").write_text(json.dumps(
        {"ts": "2026-10-12T23:00:01.000-05:00", "service": "ingest", "event": "EVENT_RECEIVED", "event_id": "p1"}
    ) + "\n", encoding="utf-8")
    enviados = []

    def gateway(request):
        enviados.append(json.loads(request.content))
        return httpx.Response(200, json={"event_id": "nuevo", "status": "accepted"})

    async def redis_info():
        return {"ok": True, "stream": 0, "pendientes": 0, "dlq": 0}

    agregador, docker, k6 = Agregador(), DockerFalso(), K6Falso()
    app = create_app(
        agregador=agregador,
        lector_servicio=LectorIncremental(tmp_path, ("ingest-*.log", "notifier-*.log")),
        lector_nginx=LectorIncremental(tmp_path / "nginx", ("gateway-access.log",)),
        redis_info=redis_info, docker=docker, k6=k6,
        gateway=httpx.AsyncClient(transport=httpx.MockTransport(gateway)),
        gateway_url="http://gateway/events", log_dir=tmp_path,
    )
    cliente = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://panel")
    return cliente, agregador, docker, k6, enviados


async def test_estado_lee_los_logs_y_reune_todo(entorno):
    cliente, *_ = entorno
    async with cliente:
        estado = (await cliente.get("/api/estado")).json()
    assert estado["eventos"]["recibidos"] == 1
    assert estado["redis"]["ok"] is True
    assert estado["contenedores"]["ingest-1"]["estado"] == "running"
    assert estado["k6"]["estado"] == "inactivo"
    assert estado["smtp"] == {"host": "mailpit", "local": True}  # por defecto, modo dev


async def test_estado_marca_gmail_como_smtp_externo(tmp_path):
    app = create_app(
        agregador=Agregador(), lector_servicio=LectorIncremental(tmp_path, ()),
        lector_nginx=LectorIncremental(tmp_path, ()), redis_info=_redis_ok, docker=DockerFalso(),
        k6=K6Falso(), gateway=httpx.AsyncClient(), gateway_url="http://gateway/events",
        smtp_host="smtp.gmail.com",
    )
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://panel") as cliente:
        estado = (await cliente.get("/api/estado")).json()
    assert estado["smtp"] == {"host": "smtp.gmail.com", "local": False}


async def _redis_ok():
    return {"ok": True, "stream": 0, "pendientes": 0, "dlq": 0}


async def test_estado_sobrevive_sin_socket_de_docker(entorno, tmp_path):
    cliente, agregador, docker, k6, _ = entorno
    docker.falla = True
    async with cliente:
        estado = (await cliente.get("/api/estado")).json()
    assert estado["contenedores"] == {}
    assert "sin socket" in estado["docker_error"]


async def test_enviar_emergencia_va_por_el_gateway(entorno):
    cliente, _, _, _, enviados = entorno
    async with cliente:
        respuesta = await cliente.post("/api/emergencia")
    assert respuesta.status_code == 200
    assert respuesta.json()["status_gateway"] == 200
    assert enviados[0]["type"] == "Emergency"
    assert enviados[0]["vehicle_plate"].startswith("PNL-")


async def test_carga_reinicia_la_ventana_y_no_permite_dos_a_la_vez(entorno):
    cliente, agregador, _, k6, _ = entorno
    async with cliente:
        primera = await cliente.post("/api/carga", json={"modo": "ritmo", "emergencias": 5})
        segunda = await cliente.post("/api/carga", json={"modo": "rafaga", "emergencias": 5})
        invalida = await cliente.post("/api/carga", json={"modo": "otro", "emergencias": 5})
    assert primera.status_code == 202
    assert agregador.desde is not None
    assert k6.iniciados == [("ritmo", 5)]
    assert segunda.status_code == 409
    assert invalida.status_code == 400


async def test_carga_del_profesor_no_promete_cuantos_emergency_manda(entorno):
    cliente, agregador, _, k6, _ = entorno
    async with cliente:
        respuesta = await cliente.post("/api/carga", json={"modo": "profesor"})
    assert respuesta.status_code == 202
    assert respuesta.json() == {"modo": "profesor", "emergencias": None}  # lo decide su script
    assert k6.iniciados[0][0] == "profesor"
    assert agregador.desde is not None


async def test_servicios_respeta_la_lista_blanca(entorno):
    cliente, _, docker, _, _ = entorno
    async with cliente:
        ok = await cliente.post("/api/servicios/mailpit/apagar")
        prohibido = await cliente.post("/api/servicios/gateway/apagar")
    assert ok.status_code == 200
    assert docker.cambios == [("mailpit", "apagar")]
    assert prohibido.status_code == 400


async def test_reiniciar_ventana(entorno):
    cliente, agregador, *_ = entorno
    async with cliente:
        respuesta = await cliente.post("/api/ventana/reiniciar")
    assert respuesta.status_code == 200
    assert agregador.desde is not None


async def test_sirve_la_pagina(entorno):
    cliente, *_ = entorno
    async with cliente:
        respuesta = await cliente.get("/")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]


async def test_emergencia_tolera_respuestas_html_del_gateway():
    # nginx responde 429/502 con una página HTML, no con JSON.
    html = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda r: httpx.Response(429, text="<html>429 Too Many Requests</html>")))
    app2 = create_app(
        agregador=Agregador(), lector_servicio=LectorIncremental(Path("."), ()),
        lector_nginx=LectorIncremental(Path("."), ()), redis_info=None, docker=None, k6=None,
        gateway=html, gateway_url="http://gateway/events")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app2), base_url="http://panel") as c:
        respuesta = await c.post("/api/emergencia")
    assert respuesta.status_code == 200
    assert respuesta.json()["status_gateway"] == 429
    assert "Too Many Requests" in respuesta.json()["respuesta"]


# --- descarga de logs de la última carga ----------------------------------------------------

COL = timezone(timedelta(hours=-5))


async def test_descargar_logs_sin_carga_terminada_es_409(entorno):
    cliente, *_ = entorno
    async with cliente:
        respuesta = await cliente.get("/api/carga/logs")
    assert respuesta.status_code == 409


async def test_descargar_logs_de_la_ultima_carga_en_log_y_csv(entorno):
    cliente, _, _, k6, _ = entorno
    k6.modo = "profesor"
    k6.ultima = (datetime(2026, 10, 12, 23, 0, 0, tzinfo=COL), datetime(2026, 10, 12, 23, 0, 30, tzinfo=COL))
    async with cliente:
        log = await cliente.get("/api/carga/logs")
        tabla = await cliente.get("/api/carga/logs", params={"formato": "csv"})
        invalido = await cliente.get("/api/carga/logs", params={"formato": "xml"})
    assert log.status_code == 200
    assert log.headers["content-disposition"] == 'attachment; filename="carga-profesor-20261012-230000.log"'
    assert json.loads(log.text.splitlines()[0])["event_id"] == "p1"
    assert tabla.headers["content-disposition"].endswith('.csv"')
    assert "text/csv" in tabla.headers["content-type"]
    assert tabla.text.splitlines()[0] == "ts,service,replica,event,event_id,plate,detalle"
    assert invalido.status_code == 422


async def test_mientras_corre_una_carga_nueva_no_se_descarga_la_anterior(entorno):
    cliente, _, _, k6, _ = entorno
    k6.ultima = (datetime(2026, 10, 12, 23, 0, 0, tzinfo=COL), datetime(2026, 10, 12, 23, 0, 30, tzinfo=COL))
    async with cliente:
        await cliente.post("/api/carga", json={"modo": "rafaga", "emergencias": 1})
        respuesta = await cliente.get("/api/carga/logs")
    assert respuesta.status_code == 409
