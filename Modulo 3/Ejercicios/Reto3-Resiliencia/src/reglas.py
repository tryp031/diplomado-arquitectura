"""Regla de niveles del Reto 3. Funciones puras: sin I/O ni reloj.

Fuente: el docente (Discord, 17/09/2026) dice que los errores del minuto que ya pasó
deciden el nivel del minuto actual, y que se degrada de inmediato (18/09/2026). La
recuperación es decisión nuestra (spec §3 y ADR de permanencia, 22/10/2026): después de
degradar, el nivel se sostiene `permanencia` minutos y luego baja de a un nivel por minuto.
Con el k6 oficial eso da 1-2-3-2-1, que es lo que el docente dice que se debe ver.
"""
from dataclasses import dataclass
from typing import Mapping

N1, N2, N3 = 1, 2, 3


@dataclass(frozen=True)
class Umbrales:
    degradado: int = 5
    minimo: int = 10
    # Minutos que dura, como mínimo, un nivel al que se entró degradando. 1 = la regla
    # anterior (se recupera al minuto siguiente si el minuto anterior quedó limpio).
    permanencia: int = 2

    def __post_init__(self):
        if not 0 < self.degradado < self.minimo:
            raise ValueError(f"umbrales inválidos: {self}")
        if self.permanencia < 1:
            raise ValueError(f"la permanencia mínima es 1 minuto: {self}")


@dataclass(frozen=True)
class Decision:
    nivel: int
    degradado_en: int | None = None  # minuto en que se entró al nivel degradando; None en N1


def memoria_minutos(u: Umbrales) -> int:
    """Minutos hacia atrás que pueden influir: la permanencia más un escalón por nivel (N3 → N1)."""
    return u.permanencia + (N3 - N1)


def objetivo(errores: int, u: Umbrales) -> int:
    if errores >= u.minimo:
        return N3
    if errores >= u.degradado:
        return N2
    return N1


def siguiente(previa: Decision, minuto: int, errores_minuto_anterior: int, u: Umbrales) -> Decision:
    """Decisión de `minuto` a partir de la del minuto anterior y sus errores."""
    meta = objetivo(errores_minuto_anterior, u)
    if meta > previa.nivel:
        return Decision(meta, degradado_en=minuto)  # se degrada de inmediato, aunque salte niveles
    if meta == previa.nivel:
        return previa  # seguir sobre el umbral sostiene el nivel, pero no reinicia la permanencia
    if previa.degradado_en is not None and minuto - previa.degradado_en < u.permanencia:
        return previa
    nivel = max(meta, previa.nivel - 1, N1)
    return Decision(nivel, None if nivel == N1 else previa.degradado_en)


def decision_para(minuto: int, registros: Mapping[int, "RegistroMinuto"], u: Umbrales) -> Decision:
    """Decisión de `minuto` a partir del último minuto con nivel decidido.

    Los minutos sin registro no tuvieron tráfico y cuentan como 0 errores.
    """
    for atras in range(1, memoria_minutos(u) + 1):
        registro = registros.get(minuto - atras)
        if registro is not None and registro.nivel is not None:
            decision = Decision(registro.nivel, registro.degradado_en)
            errores = registro.errores
            for paso in range(atras, 0, -1):
                decision = siguiente(decision, minuto - paso + 1, errores, u)
                errores = 0
            return decision
    return Decision(N1)


def nivel_para(minuto: int, registros: Mapping[int, "RegistroMinuto"], u: Umbrales) -> int:
    return decision_para(minuto, registros, u).nivel
