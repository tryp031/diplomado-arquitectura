"""Dominio: eventos de vehículos y alertas de emergencia.

No depende de ningún framework: la ingesta y el notificador lo usan igual.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

EMERGENCY = "Emergency"


class InvalidEvent(ValueError):
    """El payload no trae lo mínimo para procesarlo."""


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise InvalidEvent(f"falta '{key}' o no es texto")
    return value.strip()


@dataclass(frozen=True)
class VehicleEvent:
    type: str
    vehicle_plate: str
    status: str | None = None

    @classmethod
    def from_payload(cls, payload: Any) -> VehicleEvent:
        """Validación tolerante: exige `type` y `vehicle_plate`; ignora el resto.

        Ser estrictos contra un k6 que no conocemos arriesga el «100 % procesado».
        """
        if not isinstance(payload, dict):
            raise InvalidEvent("el payload debe ser un objeto JSON")
        status = payload.get("status")
        return cls(
            type=_required_text(payload, "type"),
            vehicle_plate=_required_text(payload, "vehicle_plate"),
            status=status if isinstance(status, str) else None,
        )

    def is_emergency(self) -> bool:
        # Sin distinguir mayúsculas: perder una emergencia es el peor fallo del sistema.
        return self.type.casefold() == EMERGENCY.casefold()


@dataclass(frozen=True)
class EmergencyAlert:
    """Lo que viaja por la cola. Solo texto, para que cualquier broker lo transporte."""

    event_id: str
    vehicle_plate: str
    status: str
    received_at: str  # ISO-8601 con offset, p. ej. 2026-10-12T23:04:11.482-05:00

    def to_fields(self) -> dict[str, str]:
        return {
            "event_id": self.event_id,
            "vehicle_plate": self.vehicle_plate,
            "status": self.status,
            "received_at": self.received_at,
        }

    @classmethod
    def from_fields(cls, fields: Mapping[str, str]) -> EmergencyAlert:
        return cls(
            event_id=fields["event_id"],
            vehicle_plate=fields["vehicle_plate"],
            status=fields.get("status", ""),
            received_at=fields["received_at"],
        )
