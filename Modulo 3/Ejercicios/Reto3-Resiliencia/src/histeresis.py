"""v3: degradación con la regla del docente y recuperación con histéresis. Funciones puras.

Degradar (docente, Discord 17-18/09/2026): los errores del «minuto» anterior deciden el nivel del
actual, y se salta de inmediato. El «minuto» es el del k6 (`floor(iteración / 20) + 1`): un bloque
de `tamano` peticiones numeradas, no el reloj. Así la latencia no corre las ventanas (riesgo R1).

Recuperar (enunciado): de N3 a N2 «cuando los indicadores vuelven a estar saludables», de N2 a N1
«cuando están completamente estables». Los dos criterios son rachas de peticiones seguidas sin error
(`racha_n2` < `racha_n1`), de a un nivel por vez. Ver docs/ADR/ADR-002-histeresis-v3.md.
"""
from dataclasses import dataclass, replace

from reglas import N1, N2, N3


@dataclass(frozen=True)
class ParamsHisteresis:
    tamano: int = 20          # peticiones por «minuto» del k6
    degradado: int = 5        # errores del bloque anterior para N2
    minimo: int = 10          # errores del bloque anterior para N3
    racha_n2: int = 30        # éxitos seguidos para pasar de N3 a N2 (≈ 90 s con el k6)
    racha_n1: int = 40        # éxitos seguidos para pasar de N2 a N1 (≈ 120 s con el k6)
    inactividad_s: float = 15.0  # sin tráfico este tiempo, la siguiente petición abre una corrida nueva

    def __post_init__(self):
        if not (0 < self.degradado < self.minimo and 0 < self.racha_n2 < self.racha_n1
                and self.tamano > 0 and self.inactividad_s > 0):
            raise ValueError(f"parámetros inválidos: {self}")


@dataclass(frozen=True)
class EstadoHisteresis:
    seq: int = 0              # peticiones de la corrida (la siguiente es seq + 1)
    nivel: int = N1
    errores_bloque: int = 0   # errores del bloque en curso
    racha: int = 0            # peticiones seguidas sin error
    ultimo: float | None = None  # instante de la última petición


@dataclass(frozen=True)
class Transicion:
    de: int
    a: int
    motivo: str               # degradacion | recuperacion
    errores_bloque_anterior: int | None
    racha: int


def objetivo(errores: int, p: ParamsHisteresis) -> int:
    if errores >= p.minimo:
        return N3
    if errores >= p.degradado:
        return N2
    return N1


def entrar(e: EstadoHisteresis, ahora: float, p: ParamsHisteresis) -> tuple[EstadoHisteresis, Transicion | None]:
    """Numera la petición que llega y decide su nivel ANTES de atenderla."""
    if e.ultimo is None or ahora - e.ultimo > p.inactividad_s:
        e = EstadoHisteresis()
    n = e.seq + 1
    nivel, bloque, transicion = e.nivel, e.errores_bloque, None
    if n > 1 and (n - 1) % p.tamano == 0:  # primera petición de un bloque: se evalúa el que se cerró
        meta = objetivo(bloque, p)
        if meta > nivel:
            transicion = Transicion(nivel, meta, "degradacion", bloque, e.racha)
            nivel = meta
        bloque = 0
    if transicion is None:
        umbral = {N3: p.racha_n2, N2: p.racha_n1}.get(nivel)
        if umbral is not None and e.racha >= umbral:
            transicion = Transicion(nivel, nivel - 1, "recuperacion", None, e.racha)
            nivel -= 1
    return replace(e, seq=n, nivel=nivel, errores_bloque=bloque, ultimo=ahora), transicion


def registrar(e: EstadoHisteresis, es_error: bool) -> EstadoHisteresis:
    """Cuenta el resultado de la petición en el bloque en curso y en la racha."""
    if es_error:
        return replace(e, errores_bloque=e.errores_bloque + 1, racha=0)
    return replace(e, racha=e.racha + 1)
