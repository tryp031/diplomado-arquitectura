"""v3: la regla pura de histéresis contra las 140 iteraciones del k6 oficial."""
import pytest

from conftest import k6_error
from histeresis import EstadoHisteresis, ParamsHisteresis, entrar, registrar

P = ParamsHisteresis()


def correr(errores, paso=3.0, p=P):
    e, niveles, transiciones, t = EstadoHisteresis(), [], [], 0.0
    for i, es_error in enumerate(errores):
        e, tr = entrar(e, t, p)
        niveles.append(e.nivel)
        if tr:
            transiciones.append((i + 1, tr))
        e = registrar(e, es_error)
        t += paso
    return niveles, transiciones


def compacta(niveles):
    return [niveles[0]] + [b for a, b in zip(niveles, niveles[1:]) if a != b]


K6 = [k6_error(i) for i in range(140)]


def test_k6_oficial_da_1_2_3_2_1_y_termina_en_n1():
    niveles, transiciones = correr(K6)
    assert compacta(niveles) == [1, 2, 3, 2, 1]
    assert [i for i, _ in transiciones] == [21, 61, 126, 136]
    assert niveles[-1] == 1


def test_nivel_al_inicio_de_cada_minuto_del_k6():
    niveles, _ = correr(K6)
    assert [niveles[m * 20] for m in range(7)] == [1, 2, 2, 3, 3, 3, 3]


@pytest.mark.parametrize("paso", [3.0, 3.001, 3.05, 3.3, 3.9])
def test_la_latencia_no_cambia_el_resultado(paso):
    assert correr(K6, paso)[0] == correr(K6, 3.0)[0]


def test_margenes_de_5_peticiones():
    # Tras el minuto 1 hay 35 éxitos seguidos antes de los errores del minuto 3 (< 40: no vuelve a N1);
    # tras el minuto 3 hay 25 (< 30: no baja de N3); tras el minuto 5 hay 45 (≥ 40: llega a N1).
    racha_max = []
    racha = 0
    for es_error in K6 + [True]:
        if es_error:
            if racha:
                racha_max.append(racha)
            racha = 0
        else:
            racha += 1
    assert racha_max == [35, 25, 45]
    assert P.racha_n1 - 35 == 5 and P.racha_n2 - 25 == 5 and 45 - P.racha_n1 == 5


def test_salta_de_1_a_3_de_inmediato_con_10_errores():
    niveles, transiciones = correr([True] * 10 + [False] * 10 + [False])
    assert niveles[20] == 3
    assert transiciones[0][1].errores_bloque_anterior == 10


def test_errores_del_bloque_en_curso_no_cambian_su_nivel():
    niveles, _ = correr([True] * 20)
    assert set(niveles) == {1}


def test_recupera_de_a_un_nivel():
    niveles, _ = correr([True] * 10 + [False] * 90)
    assert compacta(niveles) == [1, 3, 2, 1]


def test_inactividad_abre_una_corrida_nueva_en_n1():
    e = EstadoHisteresis()
    for i in range(25):
        e, _ = entrar(e, i * 3.0, P)
        e = registrar(e, i < 10)
    assert e.nivel == 3
    e, _ = entrar(e, 25 * 3.0 + P.inactividad_s + 1, P)
    assert (e.seq, e.nivel, e.errores_bloque, e.racha) == (1, 1, 0, 0)


def test_parametros_invalidos():
    with pytest.raises(ValueError):
        ParamsHisteresis(racha_n2=40, racha_n1=30)
