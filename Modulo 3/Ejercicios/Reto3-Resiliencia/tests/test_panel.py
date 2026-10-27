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
    assert resumen_coherencia(filas) == {"minutos": 3, "coinciden": 2, "todo_coincide": False,
                                         # sin errores la regla predice N1 siempre: el N2 del cliente no la cumple
                                         "minutos_regla": 3, "coinciden_regla": 2, "regla_se_cumple": False}
    assert como_csv(filas).splitlines()[1] == "2026-10-18 23:09,1,5,1,1,1-1,si,0,1,si"


def _itk(minuto_utc, n, status=200, i=1):
    ts = datetime(2026, 10, 18, 23, minuto_utc, 5, tzinfo=timezone.utc).isoformat()
    return Iteracion(ts=ts, minuto_logico=1, iteracion=i, error=status >= 500, status=status,
                     mensaje=f"Nivel {n}: x", nivel=n)


def test_la_regla_se_verifica_solo_con_el_cliente():
    # Minuto 0: 5 errores en N1 → minuto 1: N2 → minuto 2 (permanencia): N2 → minuto 3: N1.
    its = [_itk(0, 1, 500)] * 5 + [_itk(0, 1)] + [_itk(1, 2)] + [_itk(2, 2)] + [_itk(3, 1)]
    filas = coherencia(its, [])
    assert [f["nivel_regla"] for f in filas] == [1, 2, 2, 1]
    assert [f["errores_cliente"] for f in filas] == [5, 0, 0, 0]
    r = resumen_coherencia(filas)
    assert r["regla_se_cumple"] and r["minutos_regla"] == 4 and r["minutos"] == 0


def test_la_regla_detecta_un_salto():
    # Si el sistema hubiera recuperado sin permanencia, el minuto 2 en N1 no cumple la regla.
    its = [_itk(0, 1, 500)] * 5 + [_itk(1, 2), _itk(2, 1)]
    filas = coherencia(its, [])
    assert [f["coincide_regla"] for f in filas] == [True, True, False]


def test_veredicto_de_secuencia():
    k6 = EjecutorK6(OFICIAL, Path("/tmp"), Path("/tmp"))
    k6.iteraciones = [_itk(0, n, i=i) for i, n in enumerate([1] * 20 + [2] * 40 + [3] * 60 + [2] * 18 + [1] * 2)]
    v = k6.resumen()["veredicto"]
    assert v["sin_saltos"] and v["secuencia_esperada"] and v["termino_en_n1"]
    k6.iteraciones = [_itk(0, n, i=i) for i, n in enumerate([1] * 20 + [2] * 20 + [1] * 20 + [3] * 80)]
    v = k6.resumen()["veredicto"]
    assert not v["sin_saltos"] and not v["secuencia_esperada"]


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
    z = zipfile.ZipFile(io.BytesIO(r.content))
    nombres = z.namelist()
    assert sorted(n.rsplit("-", 1)[-1] for n in nombres) == ["diff.txt", "k6.log", "minutos.csv", "resumen.json", "servidor.jsonl"]
    # El resumen ya no tiene botón propio: viaja solo dentro del ZIP.
    resumen = json.loads(z.read(next(n for n in nombres if n.endswith("resumen.json"))))
    assert resumen["secuencia"] == [1] and "coherencia_cliente_servidor" in resumen
    assert c.get("/api/descargas/resumen").status_code == 422


def test_estado_trae_todas_las_respuestas_del_k6(cliente):
    c, k6, _ = cliente
    k6.entorno, k6.estado = "local", "terminado"
    k6.iteraciones = [parsear_linea(LINEA)] * 140
    assert len(c.get("/api/estado").json()["k6"]["ultimas"]) == 140


def test_no_cambia_de_entorno_con_k6_corriendo(cliente):
    c, k6, _ = cliente
    k6.estado = "corriendo"
    assert c.post("/api/entorno", json={"entorno": "aws"}).status_code == 409


def test_aws_rechaza_el_perfil_default(tmp_path):
    from panel import entornos as ent
    with pytest.raises(ent.EntornoNoDisponible):
        ent.aws(tmp_path, "default")


def test_aws_sin_perfil_es_solo_cliente(tmp_path):
    from panel import entornos as ent
    (tmp_path / ".build").mkdir()
    (tmp_path / ".build" / "url-aws.txt").write_text("https://api/prod/service-api\n")
    for perfil in (None, ""):
        e = ent.aws(tmp_path, perfil)
        assert e.url == "https://api/prod/service-api" and not e.lectura
        with pytest.raises(ent.SinLectura):
            e.minutos(1, 2)


def test_aws_lee_credenciales_de_env_aws(tmp_path, monkeypatch):
    from panel import entornos as ent
    (tmp_path / ".build").mkdir()
    (tmp_path / ".build" / "url-aws.txt").write_text("https://api/prod/service-api\n")
    (tmp_path / ".env.aws").write_text("# comentario\nAWS_ACCESS_KEY_ID=AKIAPRUEBA\nAWS_SECRET_ACCESS_KEY='secreto'\n")
    creadas = []
    sesion_real = ent.boto3.Session
    monkeypatch.setattr(ent.boto3, "Session", lambda **kw: creadas.append(kw) or sesion_real(**kw))
    assert ent.aws(tmp_path, None).lectura
    assert creadas == [{"aws_access_key_id": "AKIAPRUEBA", "aws_secret_access_key": "secreto", "region_name": "us-east-2"}]


def test_aws_env_aws_incompleto_se_rechaza(tmp_path):
    from panel import entornos as ent
    (tmp_path / ".env.aws").write_text("AWS_ACCESS_KEY_ID=AKIAPRUEBA\n")
    with pytest.raises(ent.EntornoNoDisponible, match="incompleto"):
        ent.aws(tmp_path, None)


def test_aws_ignora_las_llaves_del_shell(tmp_path, monkeypatch):
    """Sin .env.aws ni perfil, una llave exportada en la terminal NO habilita la lectura."""
    from panel import entornos as ent
    (tmp_path / ".build").mkdir()
    (tmp_path / ".build" / "url-aws.txt").write_text("https://api/prod/service-api\n")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIACORPORATIVA")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "x")
    assert not ent.aws(tmp_path, None).lectura


def test_access_denied_es_sin_lectura(tmp_path):
    import boto3
    from botocore.stub import Stubber
    from panel import entornos as ent
    e = ent.Entorno("aws", boto3.Session(aws_access_key_id="x", aws_secret_access_key="x", region_name="us-east-2"),
                    tmp_path / "url.txt")
    with Stubber(e._db) as s:
        s.add_client_error("batch_get_item", service_error_code="AccessDeniedException")
        with pytest.raises(ent.SinLectura):
            e.minutos(1, 1)


def test_estado_en_modo_solo_cliente(tmp_path):
    from panel import entornos as ent
    from panel.app import crear_app

    class SoloCliente(EntornoFalso):
        def minutos(self, desde, hasta):
            raise ent.SinLectura("sin permiso")

    k6 = EjecutorK6(OFICIAL, tmp_path / ".build", tmp_path / "logs")
    c = TestClient(crear_app(entornos={"local": SoloCliente()}, k6=k6))
    s = c.get("/api/estado").json()
    assert s["servidor"]["lectura"] is False and s["servidor"]["error"] is None
    assert s["regla"] == {"degradado": 5, "minimo": 10, "permanencia": 2}


def test_guion_del_k6_oficial():
    from panel.k6 import guion
    from reglas import Umbrales
    g = guion(Umbrales(), [])
    assert [x["errores"] for x in g] == [5, 0, 15, 0, 15, 0, 0, 0]
    assert [x["nivel_esperado"] for x in g] == [1, 2, 2, 3, 3, 3, 2, 1]
    assert g[-1]["cola"] and not g[0]["cola"]


def test_guion_coincide_con_el_script(tmp_path):
    # El guion no puede divergir del script del profesor: se recalcula con su misma fórmula.
    from conftest import k6_error
    from panel.k6 import ERRORES_DEL_GUION
    assert tuple(sum(k6_error(m * 20 + i) for i in range(20)) for m in range(7)) == ERRORES_DEL_GUION
