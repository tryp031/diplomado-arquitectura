import json

import pytest

import niveles
from reglas import N1, N2, N3


@pytest.mark.parametrize("nivel,falla,status,mensaje", [
    (N1, False, 200, "Nivel 1: OK"),
    (N1, True, 500, "Nivel 1: Operación Full con Error"),
    (N2, False, 200, "Nivel 2: OK"),
    (N2, True, 500, "Nivel 2: Operación Limitada"),
    (N3, False, 200, "Nivel 3: Operación al mínimo"),
    (N3, True, 503, "Nivel 3: Sistema bajo mantenimiento, intente más tarde"),
])
def test_mensajes_exactos(nivel, falla, status, mensaje):
    r = niveles.atender(nivel, {"error": falla}, escribir=lambda _: None)
    assert r["statusCode"] == status
    assert json.loads(r["body"]) == {"message": mensaje}
    assert mensaje in r["body"]  # sin escapes ó: k6 imprime el body tal cual


def test_solo_true_booleano_es_falla():
    r = niveles.atender(N1, {"error": "true"}, escribir=lambda _: None)
    assert r["statusCode"] == 200


def test_capacidades_se_registran():
    lineas = []
    niveles.atender(N2, {"error": False}, escribir=lineas.append)
    d = json.loads(lineas[0])
    assert d["capacidades"] == ["validar", "registrar"]
    assert d["diferidas"] == ["analisis_riesgo", "notificar"]


def test_handlers_por_nivel():
    assert json.loads(niveles.handler_nivel3({"error": False}, None)["body"])["message"] == "Nivel 3: Operación al mínimo"
