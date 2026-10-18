"""Fábricas compartidas por las pruebas.

src/ no es un paquete: en Lambda cada módulo se importa en el primer nivel
(Handler: router.handler), y aquí se replica eso agregando src/ al path.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# 1_800_000_000 redondeado al minuto: el k6 arranca en el segundo 00.
T0 = 1_800_000_000 - (1_800_000_000 % 60)


class RelojFalso:
    def __init__(self, t: float = T0):
        self.t = t

    def __call__(self) -> float:
        return self.t


class RepositorioMemoria:
    """Mismo contrato que RepositorioDynamo, en memoria."""

    def __init__(self):
        self.minutos: dict[int, dict] = {}
        self.fallar = False

    def _revisar(self):
        if self.fallar:
            from estado import EstadoNoDisponible
            raise EstadoNoDisponible("falla inyectada")

    def leer_minutos(self, minutos):
        from estado import RegistroMinuto
        self._revisar()
        return {
            m: RegistroMinuto(nivel=d.get("nivel"), errores=d.get("errores", 0))
            for m, d in self.minutos.items() if m in minutos
        }

    def fijar_nivel(self, minuto, nivel):
        self._revisar()
        item = self.minutos.setdefault(minuto, {})
        if "nivel" in item:
            return item["nivel"], False
        item["nivel"] = nivel
        return nivel, True

    def registrar_resultado(self, minuto, es_error):
        self._revisar()
        item = self.minutos.setdefault(minuto, {})
        item["peticiones"] = item.get("peticiones", 0) + 1
        item["errores"] = item.get("errores", 0) + (1 if es_error else 0)


def k6_error(i: int) -> bool:
    """Réplica exacta del patrón de k6-script-profesor-reto3.js (i = currentIteration, base 0)."""
    minuto = i // 20 + 1
    if minuto == 1:
        return i % 20 < 5
    if minuto in (3, 5):
        return i % 20 < 15
    return False
