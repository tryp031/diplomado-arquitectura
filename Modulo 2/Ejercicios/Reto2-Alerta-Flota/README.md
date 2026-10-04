# Reto 2 — Alerta temprana para flota vehicular (versión local)

Diseño: [`docs/2026-10-04-reto2-local-design.md`](docs/2026-10-04-reto2-local-design.md) ·
Plan: [`docs/2026-10-04-reto2-plan.md`](docs/2026-10-04-reto2-plan.md) ·
Enunciado oficial: `Modulo 2/Material-Clase/Actividad-Reto2.md`.

```
k6 → nginx :8080 (15 r/s, burst 2000) → ingest ×2 → Redis Streams → notifier ×1 → SMTP (Mailpit | Gmail)
```

| Enunciado (AWS) | Aquí (local) |
|---|---|
| API Gateway, rate 15, burst 2000 | nginx `limit_req` (token bucket con la misma semántica) |
| SQS | Redis Streams (consumer group, XACK, DLQ) |
| SES / correo | SMTP: Mailpit en desarrollo, Gmail en la demo |
| ≤ 10 instancias (Lambda/ECS) | 3 procesadores: 2 ingest + 1 notifier |

## Requisitos

Docker Desktop corriendo · [k6](https://k6.io) (`brew install k6` / `winget install k6`) · Python 3.12+ solo para tests y `medir.py`.

## Correr en desarrollo (Mailpit, sin Gmail)

```bash
cp .env.example .env                       # Windows: copy .env.example .env
docker compose --profile dev up -d --build
k6 run k6/carga.js                         # 1000 eventos, 5 Emergency
python3 scripts/medir.py                   # reporte de la corrida
```

Correos: http://localhost:8025 · Logs: `logs/` (JSON, hora Colombia, un archivo por réplica).

### Dos modos de carga

| Modo | Comando | Qué simula |
|---|---|---|
| Ráfaga | `k6 run k6/carga.js` | El k6 sin pausas. En local cada petición tarda ~2 ms, así que las 1000 llegan en < 1 s y solo pasan porque el burst (2000) es mayor que 1000 |
| Ritmo de referencia | `k6 run -e SLEEP_S=0.28 k6/carga.js` | La salida de referencia del enunciado: ~35 req/s durante ~28 s (en AWS el ritmo lo impone la latencia de ~176 ms) |

`-e EMERGENCIES=N` cambia cuántos `Emergency` se envían (por defecto 5; el último siempre es la iteración final, el peor caso).

## Correr contra Gmail (demo / mediciones)

1. En la cuenta Gmail: verificación en 2 pasos → *Contraseñas de aplicación* → crear una.
2. En `.env`, usar el bloque Gmail de `.env.example` (App Password sin espacios).
3. `docker compose up -d --build` (sin `--profile dev`).
4. `k6 run k6/carga.js && python3 scripts/medir.py --csv docs/resultados/corridas.csv`
5. Anotar la hora de llegada desde Gmail → «Mostrar original».

**Nunca subas `.env`**: el repo es público.

## Qué mide `medir.py`

La medida de la rúbrica es `ultima_peticion_a_ultimo_correo_s`: desde la última petición que vio
nginx hasta el último `EMAIL_SENT`. Se toma de nginx y no del fin de k6 porque (a) el fin de k6
incluye la pausa final del modo ritmo y (b) nginx usa el mismo reloj que los servicios. La llegada
a Gmail no la controlamos: se anota a mano.

## Prueba del limitador (evidencia de la restricción de 15 r/s)

```bash
RATE_BURST=100 docker compose up -d gateway
k6 run k6/carga.js                        # ráfaga
k6 run -e SLEEP_S=0.28 k6/carga.js        # ritmo de referencia
docker compose up -d gateway              # vuelve a 2000
```

Resultado medido el 04/10/2026 con burst 100:

| Modo | 200 | 429 | Esperado por token bucket |
|---|---|---|---|
| Ráfaga | 102 | 898 | ≈ 100 (cubo) + lo recargado en < 1 s |
| Ritmo de referencia | 522 | 478 | 100 + 15 r/s × 28 s = 520 |

Con burst 2000 ambos modos dan 1000/1000.

## Tests

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest                     # unitarios (sin Docker)
.venv/bin/pytest -m integration      # con el sistema arriba en modo dev
```

## Antes de medir

nginx resuelve las IP de `ingest` al arrancar. Si se recrea `ingest` (por ejemplo, con
`docker compose up -d --build`), reiniciar también el gateway: `docker compose restart gateway`.

Comparar el reloj del contenedor y el del equipo: `docker run --rm alpine date` vs `date`.
Si difieren, reiniciar Docker Desktop.

## Apagar

```bash
docker compose --profile dev down
```
