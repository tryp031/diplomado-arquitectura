import pytest

from estado import RegistroMinuto
from reglas import N1, N2, N3, Umbrales, nivel_para, objetivo, siguiente_nivel

U = Umbrales()


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


def test_sin_historia_es_n1():
    assert nivel_para(100, {}, U) == N1


def test_usa_el_minuto_anterior():
    regs = {99: RegistroMinuto(nivel=N1, errores=10)}
    assert nivel_para(100, regs, U) == N3


def test_minutos_sin_trafico_cuentan_como_cero_errores():
    # 97 en N3 con 12 errores → 98: N3 → 99 (sin tráfico): N2 → 100: N1
    regs = {97: RegistroMinuto(nivel=N3, errores=12)}
    assert nivel_para(98, regs, U) == N3
    assert nivel_para(99, regs, U) == N2
    assert nivel_para(100, regs, U) == N1


def test_historia_mas_vieja_que_la_memoria_se_ignora():
    regs = {90: RegistroMinuto(nivel=N3, errores=20)}
    assert nivel_para(100, regs, U) == N1


def test_registro_sin_nivel_se_salta():
    regs = {99: RegistroMinuto(nivel=None, errores=0), 98: RegistroMinuto(nivel=N3, errores=0)}
    assert nivel_para(100, regs, U) == N1  # 98:N3 → 99:N2 → 100:N1


def test_diagrama_de_la_sesion():
    # Discord-Aclaraciones-Docente.md §5: 0/5/10/5/0 errores → N1, N1, N2, N3, N2, N1
    errores = [0, 5, 10, 5, 0, 0]
    regs: dict[int, RegistroMinuto] = {}
    niveles = []
    for m, e in enumerate(errores):
        n = nivel_para(m, regs, U)
        regs[m] = RegistroMinuto(nivel=n, errores=e)
        niveles.append(n)
    assert niveles == [N1, N1, N2, N3, N2, N1]


def test_umbrales_invalidos():
    with pytest.raises(ValueError):
        Umbrales(degradado=10, minimo=5)
