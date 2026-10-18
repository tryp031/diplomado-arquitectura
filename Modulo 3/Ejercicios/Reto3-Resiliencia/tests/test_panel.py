"""Panel de control: lógica de evidencia y API con entornos falsos (sin red, sin k6)."""
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from panel.evidencia import coherencia, como_csv, resumen_coherencia
from panel.k6 import URL_PROFESOR, EjecutorK6, Iteracion, ScriptAlterado, parsear_linea, preparar_script, secuencia

OFICIAL = Path(__file__).resolve().parents[3] / "Material-Clase" / "k6-script-profesor-reto3.js"
LINEA = ('time="2026-10-18T18:09:00-05:00" level=info msg="Minute: 1, Iteration: 1, Error: true, Status: 500, '
         'Message: {\\"message\\": \\"Nivel 1: Operación Full con Error\\"}" source=console')


def test_preparar_script_solo_cambia_la_url(tmp_path):
    diff = preparar_script(OFICIAL, "http://localhost:4566/x", tmp_path / "copia.js")
    assert "-  const url = '" + URL_PROFESOR in diff and "+  const url = 'http://localhost:4566/x'" in diff
    assert (tmp_path / "copia.js").read_text().count("localhost:4566/x") == 1


def test_preparar_script_rechaza_un_script_sin_la_url(tmp_path):
    otro = tmp_path / "otro.js"
    otro.write_text("const url = 'https://otra';\n")
    with pytest.raises(ScriptAlterado):
        preparar_script(otro, "http://x", tmp_path / "c.js")


def test_parsear_linea_real_del_k6():
    it = parsear_linea(LINEA)
    assert it == Iteracion(ts="2026-10-18T18:09:00-05:00", minuto_logico=1, iteracion=1, error=True,
                           status=500, mensaje="Nivel 1: Operación Full con Error", nivel=1)
    assert parsear_linea("running (0m03.1s), 1/1 VUs") is None


def test_sin_respuesta_no_tiene_nivel():
    it = parsear_linea(LINEA.replace("Status: 500", "Status: 0").split("Message: ")[0] + 'Message: null" source=console')
    assert it.status == 0 and it.nivel is None


def test_secuencia_comprime():
    assert secuencia([1, 1, None, 2, 2, 1]) == [1, 2, 1]


def _it(ts, n, i=1):
    return Iteracion(ts=ts, minuto_logico=1, iteracion=i, error=False, status=200, mensaje=f"Nivel {n}: OK", nivel=n)


def test_coherencia_cliente_servidor():
    m = int(datetime(2026, 10, 18, 23, 9, tzinfo=timezone.utc).timestamp() // 60)
    its = [_it("2026-10-18T18:09:01-05:00", 1, 1), _it("2026-10-18T18:10:02-05:00", 2, 2),
           _it("2026-10-18T18:11:00-05:00", 1, 3)]
    minutos = [{"minuto": m, "nivel": 1, "errores": 5, "peticiones": 1},
               {"minuto": m + 1, "nivel": 2, "errores": 0, "peticiones": 1},
               {"minuto": m + 2, "nivel": 3, "errores": 0, "peticiones": 1}]  # el cliente vio N1: no coincide
    filas = coherencia(its, minutos)
    assert [f["coincide"] for f in filas] == [True, True, False]
    assert resumen_coherencia(filas) == {"minutos": 3, "coinciden": 2, "todo_coincide": False}
    assert como_csv(filas).splitlines()[1] == "2026-10-18 23:09,1,5,1,1,1-1,si"


class EntornoFalso:
    def __init__(self, nombre="local", url="http://api/x", permite_reinicio=True):
        self.nombre, self.url, self.permite_reinicio = nombre, url, permite_reinicio
        self.reiniciado = False

    def minutos(self, desde, hasta):
        return [{"minuto": hasta, "iso": "", "nivel": 2, "errores": 1, "peticiones": 3}]

    def eventos_clave(self, desde_ms):
        return [{"ts": 1, "evento": "CAMBIO_NIVEL", "de": 1, "a": 2, "motivo": "degradacion",
                 "errores_minuto_anterior": 5, "umbrales": {"degradado": 5, "minimo": 10}}]

    def registros(self, desde_ms, hasta_ms=None):
        return [{"grupo": "/aws/lambda/reto3-router", "ts": 1, "mensaje": '{"evento": "PETICION"}'}]

    def reiniciar(self):
        if not self.permite_reinicio:
            raise PermissionError("solo LocalStack")
        self.reiniciado = True
        return 4


@pytest.fixture
def cliente(tmp_path):
    from panel.app import crear_app
    k6 = EjecutorK6(OFICIAL, tmp_path / ".build", tmp_path / "logs")
    api = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda req: httpx.Response(503, json={"message": "Nivel 3: Sistema bajo mantenimiento, intente más tarde"})))
    entornos = {"local": EntornoFalso(), "aws": EntornoFalso("aws", "https://aws/x", permite_reinicio=False)}
    return TestClient(crear_app(entornos=entornos, k6=k6, cliente_http=api)), k6, entornos


def test_estado_muestra_nivel_y_eventos(cliente):
    c, _, _ = cliente
    s = c.get("/api/estado").json()
    assert s["nivel"]["actual"] == 2 and s["nivel"]["errores_minuto_actual"] == 1
    assert s["servidor"]["eventos"][0]["evento"] == "CAMBIO_NIVEL"
    assert s["k6"]["estado"] == "inactivo"
    assert c.get("/").status_code == 200


def test_peticion_manual_devuelve_el_mensaje(cliente):
    c, _, _ = cliente
    r = c.post("/api/peticion", json={"error": True}).json()
    assert r["status"] == 503 and r["mensaje"].startswith("Nivel 3: Sistema bajo mantenimiento")


def test_reiniciar_solo_en_localstack(cliente):
    c, _, entornos = cliente
    assert c.post("/api/reiniciar").json() == {"borrados": 4}
    c.post("/api/entorno", json={"entorno": "aws"})
    assert c.post("/api/reiniciar").status_code == 403


def test_descargas_sin_corrida_es_404(cliente):
    c, _, _ = cliente
    assert c.get("/api/descargas/zip").status_code == 404


def test_zip_de_evidencia_tras_una_corrida(cliente, tmp_path):
    c, k6, _ = cliente
    # Simula una corrida terminada sin lanzar k6.
    k6.entorno, k6.estado = "local", "terminado"
    k6.inicio, k6.fin = datetime(2026, 10, 18, 23, 8, tzinfo=timezone.utc), datetime(2026, 10, 18, 23, 16, tzinfo=timezone.utc)
    k6.log_path = tmp_path / "k6.log"
    k6.log_path.write_text(LINEA + "\n")
    k6.iteraciones = [parsear_linea(LINEA)]
    k6.diff = "-a\n+b\n"
    r = c.get("/api/descargas/zip")
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"]
    nombres = zipfile.ZipFile(io.BytesIO(r.content)).namelist()
    assert sorted(n.rsplit("-", 1)[-1] for n in nombres) == ["diff.txt", "k6.log", "minutos.csv", "resumen.json", "servidor.jsonl"]
    resumen = json.loads(c.get("/api/descargas/resumen").content)
    assert resumen["secuencia"] == [1] and "coherencia_cliente_servidor" in resumen


def test_no_cambia_de_entorno_con_k6_corriendo(cliente):
    c, k6, _ = cliente
    k6.estado = "corriendo"
    assert c.post("/api/entorno", json={"entorno": "aws"}).status_code == 409


def test_aws_rechaza_el_perfil_default(tmp_path):
    from panel import entornos as ent
    for perfil in (None, "", "default"):
        with pytest.raises(ent.EntornoNoDisponible):
            ent.aws(tmp_path, perfil)
