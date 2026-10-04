import asyncio
import json

import fakeredis
import httpx
import pytest

from panel.infra import Docker, EjecutorK6, estado_redis


# --- Docker ------------------------------------------------------------------------------

def docker_falso(llamadas):
    def responder(request: httpx.Request) -> httpx.Response:
        llamadas.append((request.method, request.url.path, dict(request.url.params)))
        if request.url.path == "/containers/json":
            return httpx.Response(200, json=[{
                "State": "running", "Status": "Up 3 minutes (healthy)",
                "Labels": {"com.docker.compose.service": "ingest", "com.docker.compose.container-number": "2"},
            }])
        return httpx.Response(204)
    return Docker("reto2-alerta-flota", transport=httpx.MockTransport(responder))


async def test_docker_lista_los_contenedores_del_proyecto():
    llamadas = []
    contenedores = await docker_falso(llamadas).contenedores()
    assert contenedores == {"ingest-2": {"servicio": "ingest", "estado": "running", "detalle": "Up 3 minutes (healthy)"}}
    filtros = json.loads(llamadas[0][2]["filters"])
    assert filtros == {"label": ["com.docker.compose.project=reto2-alerta-flota"]}


async def test_docker_apaga_y_enciende_solo_servicios_permitidos():
    llamadas = []
    docker = docker_falso(llamadas)
    await docker.cambiar("mailpit", "apagar")
    await docker.cambiar("mailpit", "encender")
    assert [(m, p) for m, p, _ in llamadas] == [
        ("POST", "/containers/reto2-alerta-flota-mailpit-1/stop"),
        ("POST", "/containers/reto2-alerta-flota-mailpit-1/start"),
    ]


@pytest.mark.parametrize("servicio, accion", [("gateway", "apagar"), ("ingest", "apagar"), ("mailpit", "borrar")])
async def test_docker_rechaza_lo_que_no_esta_en_la_lista_blanca(servicio, accion):
    with pytest.raises(ValueError):
        await docker_falso([]).cambiar(servicio, accion)


# --- k6 ----------------------------------------------------------------------------------

class ProcesoFalso:
    def __init__(self, lineas, codigo=0):
        self.stdout = self._lineas(lineas)
        self._codigo = codigo
        self.liberar = asyncio.Event()

    async def _lineas(self, lineas):
        for linea in lineas:
            yield linea.encode() + b"\n"
        await self.liberar.wait()

    async def wait(self):
        return self._codigo


async def test_k6_arma_el_comando_segun_el_modo(tmp_path):
    lanzados = []
    proceso = ProcesoFalso(["\x1b[32mrunning (0m01.0s)\x1b[0m"])

    async def lanzar(*args, **kwargs):
        lanzados.append(args)
        return proceso

    k6 = EjecutorK6("/app/k6/carga.js", "http://gateway/events", tmp_path / "k6.json", lanzar=lanzar)
    await k6.iniciar("ritmo", emergencias=3)
    assert lanzados[0][:3] == ("k6", "run", "--no-color")
    comando = " ".join(lanzados[0])
    for esperado in ("TARGET_URL=http://gateway/events", "EMERGENCIES=3", "SLEEP_S=0.28", "/app/k6/carga.js"):
        assert esperado in comando
    with pytest.raises(RuntimeError):  # una sola carga a la vez
        await k6.iniciar("rafaga", emergencias=1)
    proceso.liberar.set()
    await asyncio.wait_for(k6.esperar(), 1)
    estado = k6.resumen()
    assert estado["estado"] == "terminado"
    assert estado["salida"] == ["running (0m01.0s)"]  # sin códigos de color


@pytest.mark.parametrize("modo, emergencias", [("otro", 1), ("rafaga", -1), ("rafaga", 101)])
async def test_k6_valida_los_parametros(tmp_path, modo, emergencias):
    k6 = EjecutorK6("s.js", "http://g", tmp_path / "k6.json", lanzar=None)
    with pytest.raises(ValueError):
        await k6.iniciar(modo, emergencias=emergencias)


def test_k6_resumen_incluye_el_archivo_de_k6_si_existe(tmp_path):
    resumen = tmp_path / "k6.json"
    resumen.write_text('{"metrics": {"http_reqs": 1000}}', encoding="utf-8")
    k6 = EjecutorK6("s.js", "http://g", resumen, lanzar=None)
    assert k6.resumen()["ultimo_resumen"] == {"metrics": {"http_reqs": 1000}}


# --- Redis -------------------------------------------------------------------------------

async def test_estado_redis_reporta_stream_pendientes_y_dlq():
    client = fakeredis.FakeAsyncRedis(decode_responses=True)
    await client.xgroup_create("em", "g", id="0", mkstream=True)
    await client.xadd("em", {"a": "1"})
    await client.xreadgroup("g", "c", {"em": ">"})
    await client.xadd("em-dlq", {"a": "1"})
    assert await estado_redis(client, "em", "em-dlq", "g") == {"ok": True, "stream": 1, "pendientes": 1, "dlq": 1}


async def test_estado_redis_caido():
    class Caido:
        async def ping(self):
            raise ConnectionError("no hay redis")
    estado = await estado_redis(Caido(), "em", "em-dlq", "g")
    assert estado["ok"] is False and "no hay redis" in estado["error"]
