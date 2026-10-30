"""v3: el Router en modo histéresis, con repositorio en memoria y las 140 iteraciones del k6."""
import json

import pytest

from conftest import RelojFalso, RepositorioHisteresisMemoria, k6_error
from estado import EstadoNoDisponible
from histeresis import ParamsHisteresis
import niveles
from router import Router


def armar():
    repo, reloj, lineas = RepositorioHisteresisMemoria(), RelojFalso(), []
    r = Router(repo, lambda n, c: niveles.atender(n, c, escribir=lambda _: None), reloj=reloj,
               escribir=lineas.append, params_histeresis=ParamsHisteresis())
    return r, repo, reloj, lineas


def correr_k6(r, reloj, paso=3.0):
    mensajes = []
    for i in range(140):
        resp = r.atender({"body": json.dumps({"error": k6_error(i)})}, f"it{i + 1}")
        mensajes.append((resp["statusCode"], json.loads(resp["body"])["message"]))
        reloj.t += paso
    return mensajes


def eventos(lineas, tipo):
    return [d for d in map(json.loads, lineas) if d["evento"] == tipo]


@pytest.mark.parametrize("paso", [3.0, 3.02, 3.2])
def test_k6_oficial_extremo_a_extremo(paso):
    r, _, reloj, lineas = armar()
    mensajes = correr_k6(r, reloj, paso)
    cambios = eventos(lineas, "CAMBIO_NIVEL")
    assert [(c["peticion"], c["de"], c["a"], c["motivo"]) for c in cambios] == [
        (21, 1, 2, "degradacion"), (61, 2, 3, "degradacion"),
        (126, 3, 2, "recuperacion"), (136, 2, 1, "recuperacion")]
    assert mensajes[-1] == (200, "Nivel 1: OK")
    # Los mensajes del enunciado para N3 aparecen los dos (errores del minuto 5 y éxitos del 6).
    assert (503, "Nivel 3: Sistema bajo mantenimiento, intente más tarde") in mensajes
    assert (200, "Nivel 3: Operación al mínimo") in mensajes


def test_dos_corridas_seguidas_arrancan_en_n1():
    r, _, reloj, lineas = armar()
    correr_k6(r, reloj)
    reloj.t += 60  # el k6 espera al segundo 00
    assert correr_k6(r, reloj)[0] == (500, "Nivel 1: Operación Full con Error")  # it. 1 trae error
    assert len(eventos(lineas, "CORRIDA_NUEVA")) == 1


def test_conflicto_de_version_se_reintenta_sin_perder_la_peticion():
    r, repo, reloj, _ = armar()
    r.atender({"body": json.dumps({"error": False})}, "a")
    repo.conflictos = 2
    r.atender({"body": json.dumps({"error": True})}, "b")
    assert (repo.v3.seq, repo.v3.errores_bloque) == (2, 1)


def test_sin_estado_falla_segura_hacia_n3():
    r, repo, *_ = armar()
    repo.fallar = True
    resp = r.atender({"body": json.dumps({"error": False})}, "x")
    assert resp["statusCode"] == 503


def test_peticion_lleva_numero_y_minuto_del_k6():
    r, _, reloj, lineas = armar()
    correr_k6(r, reloj)
    p = eventos(lineas, "PETICION")
    assert (p[0]["peticion"], p[0]["minuto_k6"], p[-1]["peticion"], p[-1]["minuto_k6"]) == (1, 1, 140, 7)


@pytest.fixture
def entorno_lambda(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-2")
    monkeypatch.setenv("TABLA", "reto3-estado")
    for n in (1, 2, 3):
        monkeypatch.setenv(f"NIVEL{n}_FN", f"reto3-nivel{n}")
    monkeypatch.delenv("MODO", raising=False)
    return monkeypatch


def test_sin_modo_despliega_la_v3(entorno_lambda):
    from router import _desde_entorno
    r = _desde_entorno()
    assert r.histeresis == ParamsHisteresis()


def test_modo_reloj_despliega_la_v1(entorno_lambda):
    from router import _desde_entorno
    entorno_lambda.setenv("MODO", "reloj")
    assert _desde_entorno().histeresis is None


def test_modo_desconocido_falla_al_arrancar(entorno_lambda):
    from router import _desde_entorno
    entorno_lambda.setenv("MODO", "histéresis")  # con tilde: error de tipeo típico en la consola
    with pytest.raises(ValueError):
        _desde_entorno()
