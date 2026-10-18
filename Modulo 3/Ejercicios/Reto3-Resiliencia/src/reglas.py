"""Regla de niveles del Reto 3. Funciones puras: sin I/O ni reloj.

Fuente: el docente (Discord, 17/09/2026) dice que los errores del minuto que ya pasó
deciden el nivel del minuto actual. La recuperación de un nivel por minuto es una
decisión nuestra (ver la spec, §3).
"""
from dataclasses import dataclass
from typing import Mapping

N1, N2, N3 = 1, 2, 3

# Con recuperación de un nivel por minuto, desde N3 se llega a N1 en 3 pasos.
# Más atrás de eso la historia ya no influye.
MEMORIA_MINUTOS = N3


@dataclass(frozen=True)
class Umbrales:
    degradado: int = 5
    minimo: int = 10

    def __post_init__(self):
        if not 0 < self.degradado < self.minimo:
            raise ValueError(f"umbrales inválidos: {self}")


def objetivo(errores: int, u: Umbrales) -> int:
    if errores >= u.minimo:
        return N3
    if errores >= u.degradado:
        return N2
    return N1


def siguiente_nivel(nivel_anterior: int, errores_minuto_anterior: int, u: Umbrales) -> int:
    """Degrada de inmediato y recupera como máximo un nivel por minuto."""
    return max(objetivo(errores_minuto_anterior, u), nivel_anterior - 1, N1)


def nivel_para(minuto: int, registros: Mapping[int, "RegistroMinuto"], u: Umbrales) -> int:
    """Nivel de `minuto` a partir del último minuto con nivel decidido.

    Los minutos sin registro no tuvieron tráfico y cuentan como 0 errores.
    """
    for atras in range(1, MEMORIA_MINUTOS + 1):
        registro = registros.get(minuto - atras)
        if registro is not None and registro.nivel is not None:
            nivel, errores = registro.nivel, registro.errores
            for _ in range(atras):
                nivel = siguiente_nivel(nivel, errores, u)
                errores = 0
            return nivel
    return N1
