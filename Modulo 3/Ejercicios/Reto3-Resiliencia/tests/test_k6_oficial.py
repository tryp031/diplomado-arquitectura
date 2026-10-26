"""Reproduce las 140 iteraciones del k6 oficial contra el Router con reloj falso.

Cada iteración dura 3 s (sleep) + la latencia de la petición. El k6 arranca en el segundo 00.
"""
import json

import pytest

from conftest import RelojFalso, RepositorioMemoria, k6_error
import niveles
from router import Router


def correr_k6(paso: float):
    repo, reloj = RepositorioMemoria(), RelojFalso()
    r = Router(repo, lambda n, c: niveles.atender(n, c, escribir=lambda _: None), reloj=reloj, escribir=lambda _: None)
    mensajes = []
    for i in range(140):
        resp = r.atender({"body": json.dumps({"error": k6_error(i)})}, f"it{i + 1}")
        mensajes.append(json.loads(resp["body"])["message"])
        reloj.t += paso
    nivel = [int(m.split(":")[0].split()[1]) for m in mensajes]
    secuencia = [nivel[0]] + [b for a, b in zip(nivel, nivel[1:]) if a != b]
    return secuencia, mensajes


@pytest.mark.parametrize("paso", [3.05, 3.1, 3.2, 3.3, 3.5, 4.0])
def test_recorre_los_3_niveles_y_termina_en_n1(paso):
    secuencia, mensajes = correr_k6(paso)
    assert {1, 2, 3} <= set(secuencia)
    assert mensajes[-1] == "Nivel 1: OK"
    # Ni se recupera saltando niveles ni salta de 1 a 3 (docente, 18/09/2026: «si te salta es problema del sistema»).
    assert all(abs(a - b) == 1 for a, b in zip(secuencia, secuencia[1:]))


def test_secuencia_con_latencia_tipica_de_aws():
    # Lo que el docente dice que se debe ver: sube a N3, se sostiene y baja de a uno.
    secuencia, _ = correr_k6(3.2)
    assert secuencia == [1, 2, 3, 2, 1]


def test_riesgo_r1_latencia_cero_termina_en_n2():
    """Documenta el riesgo R1 de la spec: 140 × 3,00 s = 420 s, justo el borde del minuto 7."""
    _, mensajes = correr_k6(3.0)
    assert mensajes[-1] == "Nivel 2: OK"
