"""Historial de corridas del panel: un resumen por carga k6, persistido en un JSON.

Antes, cada carga borraba la anterior y las corridas del 06/10 hubo que anotarlas a mano. El
archivo vive en `logs/` (ya ignorado por git) y es del PANEL: no lo lee ni escribe el plano de datos.
Escritura atómica (archivo temporal + rename) para que un corte no deje el JSON a medias.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


class Historial:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._corridas: list[dict[str, Any]] = self._cargar()

    def _cargar(self) -> list[dict[str, Any]]:
        try:
            datos = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []  # sin archivo o corrupto: el panel sigue funcionando con un historial vacío
        return datos if isinstance(datos, list) else []

    def _guardar(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporal = self._path.with_suffix(".tmp")
        temporal.write_text(json.dumps(self._corridas, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(temporal, self._path)

    def abrir(self, inicio: datetime, modo: str, smtp: str) -> dict[str, Any]:
        corrida = {"n": (self._corridas[-1]["n"] + 1) if self._corridas else 1,
                   "inicio": inicio.isoformat(), "fin": None, "modo": modo, "smtp": smtp}
        self._corridas.append(corrida)
        self._guardar()
        return corrida

    def actualizar(self, n: int, **campos: Any) -> bool:
        """Mezcla `campos` en la corrida `n`. Devuelve si cambió algo (y solo entonces escribe)."""
        corrida = self.buscar(n)
        if corrida is None or all(corrida.get(k) == v for k, v in campos.items()):
            return False
        corrida.update(campos)
        self._guardar()
        return True

    def buscar(self, n: int) -> dict[str, Any] | None:
        return next((c for c in self._corridas if c["n"] == n), None)

    def ultima(self) -> dict[str, Any] | None:
        return self._corridas[-1] if self._corridas else None

    def listar(self, limite: int = 20) -> list[dict[str, Any]]:
        return list(reversed(self._corridas[-limite:]))
