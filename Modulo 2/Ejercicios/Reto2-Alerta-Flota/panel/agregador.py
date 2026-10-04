"""Agregación, para el panel, de lo que el sistema ya registra (logs JSON y log de nginx).

El panel es plano de CONTROL: solo lee lo que el plano de datos deja escrito. No toca la
ingesta ni el notifier, así que observar no altera la latencia que se mide.
"""
from __future__ import annotations

import json
import math
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENTOS_FEED = {
    "EMERGENCY_RECEIVED", "EMERGENCY_ENQUEUE_FAILED", "EMAIL_SENT", "EMAIL_RETRY", "EMAIL_DLQ",
    "CONSUMER_ERROR", "WORKER_ERROR", "NOTIFIER_STARTED", "PENDING_CLAIMED",
}
SEGUNDOS_SERIE = 60
# Cortes de la rúbrica del enunciado: < 15 s → 2.5 · 15-45 s → 1.5 · > 45 s → 0.5
CORTES_RUBRICA = ((15, "good", 2.5), (45, "warning", 1.5), (math.inf, "critical", 0.5))


def calificar(segundos: float | None) -> dict[str, Any]:
    if segundos is None:
        return {"segundos": None, "nivel": None, "puntos": None}
    efectivo = max(segundos, 0.0)  # negativo: el correo salió antes de la última petición
    nivel, puntos = next((n, p) for corte, n, p in CORTES_RUBRICA if efectivo < corte)
    return {"segundos": segundos, "nivel": nivel, "puntos": puntos}


class LectorIncremental:
    """Lee solo las líneas nuevas de cada archivo. Tolera truncado y líneas a medio escribir."""

    def __init__(self, directorio: Path, patrones: tuple[str, ...]) -> None:
        self._directorio = directorio
        self._patrones = patrones
        self._posiciones: dict[Path, int] = {}
        self._restos: dict[Path, bytes] = {}

    def leer(self) -> list[tuple[str, dict]]:
        nuevos: list[tuple[str, dict]] = []
        for patron in self._patrones:
            for path in sorted(self._directorio.glob(patron)):
                nuevos += [(path.stem, registro) for registro in self._leer_archivo(path)]
        return nuevos

    def _leer_archivo(self, path: Path) -> list[dict]:
        tamano = path.stat().st_size
        posicion = self._posiciones.get(path, 0)
        if tamano < posicion:  # el archivo se truncó o se recreó
            posicion = 0
            self._restos.pop(path, None)
        if tamano == posicion:
            return []
        with path.open("rb") as archivo:
            archivo.seek(posicion)
            datos = self._restos.pop(path, b"") + archivo.read(tamano - posicion)
        self._posiciones[path] = tamano
        *lineas, resto = datos.split(b"\n")
        if resto:
            self._restos[path] = resto  # línea a medio escribir: se completa en la próxima lectura
        registros = []
        for linea in lineas:
            if not linea.strip():
                continue
            try:
                registros.append(json.loads(linea))
            except json.JSONDecodeError:
                continue
        return registros


@dataclass
class Emergencia:
    event_id: str
    placa: str
    recibida: datetime
    encolada: datetime | None = None
    enviada: datetime | None = None
    intentos: int = 0
    estado: str = "recibida"  # recibida | encolada | reintentando | enviada | dlq | fallida

    def como_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "placa": self.placa,
            "recibida": self.recibida.isoformat(timespec="milliseconds"),
            "ms_encolada": _ms(self.recibida, self.encolada),
            "ms_envio": _ms(self.recibida, self.enviada),
            "intentos": self.intentos,
            "estado": self.estado,
        }


class Agregador:
    def __init__(self) -> None:
        self.reiniciar(None)

    def reiniciar(self, desde: datetime | None) -> None:
        """Abre una ventana nueva: lo anterior a `desde` deja de contarse."""
        self.desde = desde
        self._http: Counter[int] = Counter()
        self._por_segundo: dict[int, Counter[str]] = {}
        self._ultima_peticion: datetime | None = None
        self._eventos: Counter[str] = Counter()
        self._por_replica: Counter[str] = Counter()
        self._ultimo_visto: dict[str, datetime] = {}
        self._emergencias: dict[str, Emergencia] = {}
        self._feed: deque[dict[str, Any]] = deque(maxlen=60)

    def ingerir_nginx(self, registros: list[dict]) -> None:
        for registro in registros:
            if str(registro.get("uri", "")).split("?")[0] != "/events":
                continue  # los health checks no son tráfico del reto
            momento = datetime.fromtimestamp(registro["msec"], tz=timezone.utc)
            if self.desde and momento < self.desde:
                continue
            status = int(registro["status"])
            self._http[status] += 1
            clase = "aceptadas" if status < 400 else "rechazadas"
            self._por_segundo.setdefault(int(registro["msec"]), Counter())[clase] += 1
            self._ultima_peticion = max(filter(None, (self._ultima_peticion, momento)))
            self._ultimo_visto["gateway"] = self._ultima_peticion

    def ingerir_servicio(self, registros: list[tuple[str, dict]]) -> None:
        for archivo, registro in registros:
            momento = _fecha(registro["ts"])
            if self.desde and momento < self.desde:
                continue
            evento, servicio = registro["event"], registro.get("service", "?")
            self._eventos[evento] += 1
            self._ultimo_visto[servicio] = momento
            if evento in ("EVENT_RECEIVED", "EMERGENCY_RECEIVED"):
                self._por_replica[archivo] += 1
            self._seguir_emergencia(evento, registro, momento)
            if evento in EVENTOS_FEED:
                self._feed.appendleft({
                    "ts": momento.isoformat(timespec="milliseconds"),
                    "servicio": servicio,
                    "evento": evento,
                    "event_id": registro.get("event_id"),
                    "placa": registro.get("plate"),
                    "detalle": registro.get("error") or _detalle(registro),
                })

    def _seguir_emergencia(self, evento: str, registro: dict, momento: datetime) -> None:
        event_id = registro.get("event_id")
        if evento == "EMERGENCY_RECEIVED":
            self._emergencias[event_id] = Emergencia(event_id, registro.get("plate", ""), momento)
            return
        emergencia = self._emergencias.get(event_id) if event_id else None
        if emergencia is None:
            return  # de una ventana anterior
        if evento == "EMERGENCY_ENQUEUED":
            emergencia.encolada, emergencia.estado = momento, "encolada"
        elif evento == "EMERGENCY_ENQUEUE_FAILED":
            emergencia.estado = "fallida"
        elif evento == "EMAIL_RETRY":
            emergencia.intentos, emergencia.estado = registro.get("attempt", 0), "reintentando"
        elif evento == "EMAIL_SENT":
            emergencia.enviada, emergencia.estado = momento, "enviada"
            emergencia.intentos = registro.get("attempt", emergencia.intentos)
        elif evento == "EMAIL_DLQ":
            emergencia.intentos, emergencia.estado = registro.get("attempts", 0), "dlq"

    def resumen(self, ahora: datetime) -> dict[str, Any]:
        emergencias = sorted(self._emergencias.values(), key=lambda e: e.recibida, reverse=True)
        ultimo_correo = max((e.enviada for e in emergencias if e.enviada), default=None)
        medida = None
        if ultimo_correo and self._ultima_peticion:
            medida = round((ultimo_correo - self._ultima_peticion).total_seconds(), 3)
        estados = Counter(e.estado for e in emergencias)
        return {
            "ventana_desde": self.desde.isoformat() if self.desde else None,
            "http": {
                "total": sum(self._http.values()),
                "aceptadas": sum(n for s, n in self._http.items() if s < 400),
                "rechazadas_429": self._http[429],
                "otros_errores": sum(n for s, n in self._http.items() if s >= 400 and s != 429),
            },
            "eventos": {
                "recibidos": self._eventos["EVENT_RECEIVED"] + self._eventos["EMERGENCY_RECEIVED"],
                "emergencias": len(emergencias),
                "encoladas": sum(1 for e in emergencias if e.encolada),
                "enviadas": estados["enviada"],
                "dlq": estados["dlq"],
                "fallidas": estados["fallida"],
                "reintentos": self._eventos["EMAIL_RETRY"],
            },
            "por_replica": dict(self._por_replica),
            "medida_rubrica": calificar(medida),
            "serie": self._serie(ahora),
            "emergencias": [e.como_dict() for e in emergencias[:25]],
            "feed": sorted(self._feed, key=lambda f: _fecha(f["ts"]), reverse=True)[:40],
            "ultimo_visto": {k: v.isoformat(timespec="milliseconds") for k, v in self._ultimo_visto.items()},
        }

    def _serie(self, ahora: datetime) -> list[dict[str, int]]:
        fin = int(ahora.timestamp())
        serie = []
        for t in range(fin - SEGUNDOS_SERIE + 1, fin + 1):
            conteo = self._por_segundo.get(t, Counter())
            serie.append({"t": t, "aceptadas": conteo["aceptadas"], "rechazadas": conteo["rechazadas"]})
        return serie


def _fecha(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def _ms(desde: datetime, hasta: datetime | None) -> int | None:
    return None if hasta is None else round((hasta - desde).total_seconds() * 1000)


def _detalle(registro: dict) -> str | None:
    if "ms_since_received" in registro:
        return f"{registro['ms_since_received']} ms desde la recepción"
    if "count" in registro:
        return f"{registro['count']} pendientes"
    return None
