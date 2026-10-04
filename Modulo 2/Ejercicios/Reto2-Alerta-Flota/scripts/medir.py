"""Reporte de una corrida del Reto 2 a partir de los logs.

Uso:  python3 scripts/medir.py [--logs logs] [--csv docs/resultados/corridas.csv]

Mide hasta el ENVÍO del correo (EMAIL_SENT). La llegada a Gmail se anota a mano
desde «Mostrar original»: la entrega de Gmail no está bajo nuestro control.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

MARGEN_DESPUES_DEL_FIN = timedelta(minutes=2)


@dataclass(frozen=True)
class Reporte:
    k6_inicio: str
    k6_fin: str
    k6_peticiones: int
    k6_fallidas_pct: float
    k6_p95_ms: float
    nginx_total: int
    nginx_429: int
    nginx_otros_errores: int
    eventos_recibidos: int
    emergencias_recibidas: int
    emergencias_encoladas: int
    correos_enviados: int
    correos_dlq: int
    recepcion_a_envio_max_ms: int | None
    fin_k6_a_ultimo_correo_s: float | None  # reloj del equipo; incluye la pausa final de k6 (SLEEP_S)
    # La medida de la rúbrica («último envío de k6 → correo»), hasta el envío: última petición
    # vista por nginx. Mismo reloj que los servicios (la VM de Docker): sin desfase con el equipo.
    ultima_peticion_a_ultimo_correo_s: float | None


def _fecha(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def analizar(servicio: list[dict], nginx: list[dict], k6: dict) -> Reporte:
    inicio, fin = _fecha(k6["started_at"]), _fecha(k6["ended_at"])
    limite = fin + MARGEN_DESPUES_DEL_FIN
    regs = [r for r in servicio if inicio <= _fecha(r["ts"]) <= limite]

    def eventos(nombre: str) -> list[dict]:
        return [r for r in regs if r["event"] == nombre]

    emergencias = {r["event_id"] for r in eventos("EMERGENCY_RECEIVED")}
    enviados = [r for r in eventos("EMAIL_SENT") if r["event_id"] in emergencias]
    peticiones = [n for n in nginx
                  if inicio <= datetime.fromtimestamp(n["msec"], tz=timezone.utc) <= limite]
    metricas = k6["metrics"]
    ultimo_correo = max((_fecha(r["ts"]) for r in enviados), default=None)
    ultima_peticion = max((datetime.fromtimestamp(n["msec"], tz=timezone.utc) for n in peticiones), default=None)
    return Reporte(
        k6_inicio=k6["started_at"],
        k6_fin=k6["ended_at"],
        k6_peticiones=metricas["http_reqs"],
        k6_fallidas_pct=round(metricas["http_req_failed_rate"] * 100, 2),
        k6_p95_ms=round(metricas["http_req_duration_p95_ms"], 2),
        nginx_total=len(peticiones),
        nginx_429=sum(1 for n in peticiones if n["status"] == 429),
        nginx_otros_errores=sum(1 for n in peticiones if n["status"] >= 400 and n["status"] != 429),
        eventos_recibidos=len(eventos("EVENT_RECEIVED")) + len(emergencias),
        emergencias_recibidas=len(emergencias),
        emergencias_encoladas=len({r["event_id"] for r in eventos("EMERGENCY_ENQUEUED")} & emergencias),
        correos_enviados=len(enviados),
        correos_dlq=len([r for r in eventos("EMAIL_DLQ") if r["event_id"] in emergencias]),
        recepcion_a_envio_max_ms=max((r["ms_since_received"] for r in enviados), default=None),
        fin_k6_a_ultimo_correo_s=_segundos(fin, ultimo_correo),
        ultima_peticion_a_ultimo_correo_s=_segundos(ultima_peticion, ultimo_correo),
    )


def _segundos(desde: datetime | None, hasta: datetime | None) -> float | None:
    if desde is None or hasta is None:
        return None
    return round((hasta - desde).total_seconds(), 3)


def _leer_jsonl(paths: list[Path]) -> list[dict]:
    registros = []
    for path in paths:
        for linea in path.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                registros.append(json.loads(linea))
    return registros


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--logs", default="logs", type=Path)
    parser.add_argument("--csv", type=Path, help="agrega la corrida como fila a este CSV")
    args = parser.parse_args()

    servicio = _leer_jsonl(sorted(args.logs.glob("ingest-*.log")) + sorted(args.logs.glob("notifier-*.log")))
    nginx = _leer_jsonl([p for p in [args.logs / "nginx" / "gateway-access.log"] if p.exists()])
    k6 = json.loads((args.logs / "k6-summary.json").read_text(encoding="utf-8"))
    reporte = analizar(servicio, nginx, k6)

    for campo, valor in asdict(reporte).items():
        print(f"{campo:34} {valor}")
    if args.csv:
        nuevo = not args.csv.exists()
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("a", newline="", encoding="utf-8") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=list(asdict(reporte)))
            if nuevo:
                writer.writeheader()
            writer.writerow(asdict(reporte))


if __name__ == "__main__":
    main()
