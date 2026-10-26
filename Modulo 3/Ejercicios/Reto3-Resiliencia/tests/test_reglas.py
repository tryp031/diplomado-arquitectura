import pytest

from estado import RegistroMinuto
from reglas import N1, N2, N3, Decision, Umbrales, decision_para, memoria_minutos, nivel_para, objetivo, siguiente

U = Umbrales()
SIN_PERMANENCIA = Umbrales(permanencia=1)  # la regla anterior: recupera al minuto siguiente


def siguiente_nivel(nivel, errores, u, minuto=100, degradado_en=None):
    return siguiente(Decision(nivel, degradado_en), minuto, errores, u).nivel


@pytest.mark.parametrize("errores,esperado", [(0, N1), (4, N1), (5, N2), (9, N2), (10, N3), (15, N3)])
def test_objetivo_por_umbrales(errores, esperado):
    assert objetivo(errores, U) == esperado


def test_degradacion_inmediata_salta_de_1_a_3():
    # Docente 18/09/2026: «se pasa de inmediato».
    assert siguiente_nivel(N1, 15, U) == N3


def test_recuperacion_baja_un_nivel_por_minuto():
    assert siguiente_nivel(N3, 0, U) == N2
    assert siguiente_nivel(N2, 0, U) == N1
    assert siguiente_nivel(N1, 0, U) == N1


def test_recuperacion_parcial_respeta_el_objetivo():
    # Desde N3 con 5 errores el objetivo es N2: coincide con bajar un nivel.
    assert siguiente_nivel(N3, 5, U) == N2


def test_degradar_registra_el_minuto():
    assert siguiente(Decision(N1), 100, 15, U) == Decision(N3, degradado_en=100)


def test_permanencia_sostiene_el_nivel_aunque_el_minuto_anterior_este_limpio():
    # Degradó en el minuto 100: en el 101 sigue en N3 aunque el 100 tuvo 0 errores.
    assert siguiente_nivel(N3, 0, U, minuto=101, degradado_en=100) == N3
    assert siguiente_nivel(N3, 0, U, minuto=102, degradado_en=100) == N2


def test_permanencia_1_es_la_regla_anterior():
    assert siguiente_nivel(N3, 0, SIN_PERMANENCIA, minuto=101, degradado_en=100) == N2


def test_errores_sostenidos_no_reinician_la_permanencia():
    # Seguir sobre el umbral mantiene el nivel, pero la permanencia se cuenta desde que se entró.
    assert siguiente(Decision(N3, 100), 102, 15, U) == Decision(N3, 100)


def test_la_recuperacion_no_espera_otra_permanencia():
    # Ya cumplida la permanencia, se baja de a un nivel por minuto, sin volver a esperar en N2.
    assert siguiente(Decision(N2, 100), 103, 0, U) == Decision(N1, None)


def test_memoria_cubre_permanencia_y_escalones():
    assert memoria_minutos(SIN_PERMANENCIA) == 3
    assert memoria_minutos(U) == 4


def test_sin_historia_es_n1():
    assert nivel_para(100, {}, U) == N1


def test_usa_el_minuto_anterior():
    regs = {99: RegistroMinuto(nivel=N1, errores=10)}
    assert nivel_para(100, regs, U) == N3


def test_minutos_sin_trafico_cuentan_como_cero_errores():
    # Entró a N3 en el 96; el 97 tuvo 12 errores → 98: N3 → 99 (sin tráfico, permanencia cumplida): N2 → 100: N1
    regs = {97: RegistroMinuto(nivel=N3, errores=12, degradado_en=96)}
    assert nivel_para(98, regs, U) == N3
    assert nivel_para(99, regs, U) == N2
    assert nivel_para(100, regs, U) == N1
    regs = {97: RegistroMinuto(nivel=N3, errores=0, degradado_en=97)}
    assert [nivel_para(m, regs, U) for m in (98, 99, 100)] == [N3, N2, N1]


def test_decision_para_conserva_el_minuto_de_degradacion():
    regs = {99: RegistroMinuto(nivel=N1, errores=10)}
    assert decision_para(100, regs, U) == Decision(N3, degradado_en=100)


def test_historia_mas_vieja_que_la_memoria_se_ignora():
    regs = {90: RegistroMinuto(nivel=N3, errores=20)}
    assert nivel_para(100, regs, U) == N1


def test_registro_sin_nivel_se_salta():
    regs = {99: RegistroMinuto(nivel=None, errores=0), 98: RegistroMinuto(nivel=N3, errores=0, degradado_en=97)}
    assert nivel_para(100, regs, U) == N1  # 98:N3 → 99:N2 → 100:N1


def simular(errores, u):
    regs: dict[int, RegistroMinuto] = {}
    niveles = []
    for m, e in enumerate(errores):
        d = decision_para(m, regs, u)
        regs[m] = RegistroMinuto(nivel=d.nivel, errores=e, degradado_en=d.degradado_en)
        niveles.append(d.nivel)
    return niveles


def test_diagrama_de_la_sesion_sin_permanencia():
    # Discord-Aclaraciones-Docente.md §5: 0/5/10/5/0 errores → N1, N1, N2, N3, N2, N1
    assert simular([0, 5, 10, 5, 0, 0], SIN_PERMANENCIA) == [N1, N1, N2, N3, N2, N1]


def test_diagrama_de_la_sesion_con_permanencia_se_desvia_en_la_ventana_4_5():
    # Desviación aceptada (ADR de permanencia): N3 se sostiene un minuto más.
    assert simular([0, 5, 10, 5, 0, 0, 0], U) == [N1, N1, N2, N3, N3, N2, N1]


def test_patron_del_k6_oficial_por_minuto():
    # 5/0/15/0/15/0/0 errores: el docente espera ver 1-2-3-3-2-1 (Discord, 18/09/2026).
    assert simular([5, 0, 15, 0, 15, 0, 0, 0], U) == [N1, N2, N2, N3, N3, N3, N2, N1]
    assert simular([5, 0, 15, 0, 15, 0, 0, 0], SIN_PERMANENCIA) == [N1, N2, N1, N3, N2, N3, N2, N1]


def test_permanencia_invalida():
    with pytest.raises(ValueError):
        Umbrales(permanencia=0)


def test_umbrales_invalidos():
    with pytest.raises(ValueError):
        Umbrales(degradado=10, minimo=5)
