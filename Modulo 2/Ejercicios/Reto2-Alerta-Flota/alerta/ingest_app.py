"""Ingesta HTTP. Responde en milisegundos: nunca espera al envío del correo (opción C del análisis)."""
from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alerta.domain import EmergencyAlert, InvalidEvent, VehicleEvent
from alerta.logjson import JsonLogger, format_ts, now_local
from alerta.ports import AlertPublisher


def create_app(publisher: AlertPublisher, log: JsonLogger) -> FastAPI:
    app = FastAPI(title="Reto 2 — ingesta de eventos de flota")

    @app.post("/events")
    async def receive(request: Request):
        received_at = now_local()
        try:
            event = VehicleEvent.from_payload(await request.json())
        except ValueError as exc:  # JSON mal formado o InvalidEvent
            message = str(exc) if isinstance(exc, InvalidEvent) else "el cuerpo no es JSON válido"
            return JSONResponse({"error": message}, status_code=400)

        event_id = str(uuid4())
        ids = {"event_id": event_id, "plate": event.vehicle_plate}
        if not event.is_emergency():
            log.log("EVENT_RECEIVED", **ids, type=event.type)
            return {"event_id": event_id, "status": "accepted"}

        log.log("EMERGENCY_RECEIVED", **ids)
        alert = EmergencyAlert(event_id, event.vehicle_plate, event.status or "", format_ts(received_at))
        try:
            await publisher.publish(alert)
        except Exception as exc:  # preferimos un error visible a confirmar una alerta perdida
            log.log("EMERGENCY_ENQUEUE_FAILED", **ids, error=f"{type(exc).__name__}: {exc}")
            return JSONResponse({"error": "no se pudo registrar la emergencia"}, status_code=503)
        log.log("EMERGENCY_ENQUEUED", **ids)
        return {"event_id": event_id, "status": "accepted"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
