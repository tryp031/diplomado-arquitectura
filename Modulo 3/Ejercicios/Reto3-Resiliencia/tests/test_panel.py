"""Panel de control: lógica de evidencia y API con entornos falsos (sin red, sin k6)."""
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from panel.evidencia import coherencia, como_csv, corrida_servidor, guion, resumen_coherencia, simular
from panel.k6 import URL_PROFESOR, EjecutorK6, Iteracion, ScriptAlterado, parsear_linea, preparar_script, secuencia

OFICIAL = Path(__file__).resolve().parents[3] / "Material-Clase" / "k6-script-profesor-reto3.js"
EVIDENCIA_CAMILO = (Path(__file__).resolve().parents[3] / "Aportes" / "camilo" / "evidencia-corrida-oficial-v3-20261102")
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


def _it(i, n, status=200):
    return Iteracion(ts="2026-11-02T12:33:00-05:00", minuto_logico=(i - 1) // 20 + 1, iteracion=i,
                     error=status >= 500, status=status, mensaje=f"Nivel {n}: x", nivel=n)


def _pet(i, n, status=200):
    return {"evento": "PETICION", "peticion": i, "minuto_k6": (i - 1) // 20 + 1, "nivel": n, "status": status}


def _corrida_k6():
    """Las 140 iteraciones del k6 oficial respondidas como predice la regla (la corrida perfecta)."""
    from panel.k6 import error_del_script
    errores = [error_del_script(i) for i in range(140)]
    return [_it(i + 1, n, 500 if e else 200) for i, (n, e) in enumerate(zip(simular(errores), errores))]


def test_simular_el_script_oficial_da_1_2_3_2_1():
    from panel.k6 import error_del_script
    niveles = simular([error_del_script(i) for i in range(140)])
    cambios = [i + 1 for i in range(1, 140) if niveles[i] != niveles[i - 1]]
    assert secuencia(niveles) == [1, 2, 3, 2, 1] and cambios == [21, 61, 126, 136]


def test_coherencia_por_minuto_del_k6():
    its = _corrida_k6()
    srv = {i.iteracion: _pet(i.iteracion, i.nivel, i.status) for i in its}
    srv[130] = _pet(130, 3)  # el servidor dice otra cosa en una petición del minuto 7
    filas = coherencia(its, srv)
    assert [f["minuto"] for f in filas] == list(range(1, 8))
    assert filas[6]["niveles_cliente"] == filas[6]["niveles_regla"] == [3, 2, 1]
    assert [f["coincide"] for f in filas] == [True] * 6 + [False]
    assert resumen_coherencia(filas) == {"minutos": 7, "coinciden": 6, "todo_coincide": False,
                                         "minutos_regla": 7, "coinciden_regla": 7, "regla_se_cumple": True}
    assert como_csv(filas).splitlines()[1:3] == ["1,1-20,5,5,1,1,1,si,si", "2,21-40,0,0,2,2,2,si,si"]
    assert como_csv(filas).splitlines()[7] == "7,121-140,0,0,3-2-1,3-2-3-2-1,3-2-1,NO,si"


def test_la_regla_se_verifica_solo_con_el_cliente():
    filas = coherencia(_corrida_k6(), {})
    r = resumen_coherencia(filas)
    assert r["regla_se_cumple"] and r["minutos_regla"] == 7 and r["minutos"] == 0


def test_la_regla_detecta_una_recuperacion_temprana():
    # Si el sistema hubiera vuelto a N1 apenas terminó el bloque sin errores, el minuto 2 no cumple.
    its = [_it(i, 1, 500 if i <= 5 else 200) for i in range(1, 21)] + [_it(i, 1) for i in range(21, 41)]
    assert [f["coincide_regla"] for f in coherencia(its, {})] == [True, False]


def test_corrida_servidor_separa_corridas():
    vieja = [dict(_pet(i, 3), ts=1000 + i) for i in range(1, 50)]
    nueva = [{"evento": "CORRIDA_NUEVA", "ts": 5000}] + [dict(_pet(i, 1), ts=5000 + i) for i in range(1, 4)]
    manual = [dict(_pet(1, 1), ts=9000)]
    assert sorted(corrida_servidor(vieja + nueva)) == [1, 2, 3]
    assert len(corrida_servidor(vieja + nueva + manual, desde_ms=4000)) == 3
    assert corrida_servidor([]) == {}


def test_coherencia_con_la_corrida_oficial_de_camilo():
    """Evidencia real (AWS, 02/11/2026): log del k6 + servidor.jsonl. Cliente = servidor = regla en los 7 minutos."""
    from panel.k6 import parsear_linea
    log = next(EVIDENCIA_CAMILO.glob("*-k6.log")).read_text(encoding="utf-8")
    its = [it for it in map(parsear_linea, log.splitlines()) if it]
    eventos = [json.loads(l) for l in next(EVIDENCIA_CAMILO.glob("*-servidor.jsonl")).read_text().splitlines() if l]
    filas = coherencia(its, corrida_servidor(eventos))
    assert len(its) == 140 and [f["minuto"] for f in filas] == list(range(1, 8))
    assert resumen_coherencia(filas) == {"minutos": 7, "coinciden": 7, "todo_coincide": True,
                                         "minutos_regla": 7, "coinciden_regla": 7, "regla_se_cumple": True}
    assert [f["errores_servidor"] for f in filas] == [5, 0, 15, 0, 15, 0, 0]
    assert filas[6]["niveles_servidor"] == [3, 2, 1]


def test_veredicto_de_secuencia():
    k6 = EjecutorK6(OFICIAL, Path("/tmp"), Path("/tmp"))
    k6.iteraciones = [_it(i + 1, n) for i, n in enumerate([1] * 20 + [2] * 40 + [3] * 60 + [2] * 18 + [1] * 2)]
    v = k6.resumen()["veredicto"]
    assert v["sin_saltos"] and v["secuencia_esperada"] and v["termino_en_n1"]
    k6.iteraciones = [_it(i + 1, n) for i, n in enumerate([1] * 20 + [2] * 20 + [1] * 20 + [3] * 80)]
    v = k6.resumen()["veredicto"]
    assert not v["sin_saltos"] and not v["secuencia_esperada"]


class EntornoFalso:
    def __init__(self, nombre="local", url="http://api/x", permite_reinicio=True):
        self.nombre, self.url, self.permite_reinicio = nombre, url, permite_reinicio
        self.reiniciado = False

    def estado_v3(self):
        import time
        return {"pk": "V3", "seq": 47, "nivel": 3, "errores_bloque": 4, "racha": 17, "ultimo": time.time(),
                "version": 47, "ttl": None}

    def eventos_router(self, desde_ms, hasta_ms=None):
        return [{"ts": 1, "evento": "CAMBIO_NIVEL", "de": 1, "a": 2, "motivo": "degradacion", "peticion": 21,
                 "errores_minuto_anterior": 5, "racha_sin_error": 15,
                 "umbrales": {"degradado": 5, "minimo": 10, "racha_n2": 30, "racha_n1": 40}},
                {"ts": 2, **_pet(1, 1)}]

    def peticiones(self, desde_ms, hasta_ms=None):
        return [e for e in self.eventos_router(desde_ms) if e["evento"] == "PETICION"]

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
    assert s["nivel"] == {**s["nivel"], "actual": 3, "peticion": 47, "minuto_k6": 3, "errores_bloque": 4,
                          "racha": 17, "meta_racha": 30, "corrida_cerrada": False}
    assert s["coherencia"]["filas"][0]["niveles_servidor"] == [1]
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
            e.estado_v3()


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
        s.add_client_error("get_item", service_error_code="AccessDeniedException")
        with pytest.raises(ent.SinLectura):
            e.estado_v3()


def test_estado_en_modo_solo_cliente(tmp_path):
    from panel import entornos as ent
    from panel.app import crear_app

    class SoloCliente(EntornoFalso):
        def estado_v3(self):
            raise ent.SinLectura("sin permiso")

    k6 = EjecutorK6(OFICIAL, tmp_path / ".build", tmp_path / "logs")
    c = TestClient(crear_app(entornos={"local": SoloCliente()}, k6=k6))
    s = c.get("/api/estado").json()
    assert s["servidor"]["lectura"] is False and s["servidor"]["error"] is None
    assert s["regla"] == {"tamano": 20, "degradado": 5, "minimo": 10, "racha_n2": 30, "racha_n1": 40,
                          "inactividad_s": 15.0}


def test_guion_del_k6_oficial():
    from histeresis import ParamsHisteresis
    g = guion(ParamsHisteresis(), [])
    assert [x["errores"] for x in g] == [5, 0, 15, 0, 15, 0, 0]
    assert [x["niveles_esperados"] for x in g] == [[1], [2], [2], [3], [3], [3], [3, 2, 1]]


def test_guion_coincide_con_el_script(tmp_path):
    # El guion no puede divergir del script del profesor: se recalcula con su misma fórmula.
    from conftest import k6_error
    from panel.k6 import ERRORES_DEL_GUION, error_del_script
    assert tuple(sum(k6_error(m * 20 + i) for i in range(20)) for m in range(7)) == ERRORES_DEL_GUION
    assert all(error_del_script(i) == k6_error(i) for i in range(140))
