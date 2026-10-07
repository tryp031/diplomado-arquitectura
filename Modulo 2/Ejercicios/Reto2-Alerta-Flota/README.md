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

## Panel de control (respaldo visual y demo)

```bash
docker compose --profile dev --profile panel up -d --build
```

Abrir http://localhost:8090. Muestra la arquitectura en vivo, la medida de la rúbrica con semáforo
(< 15 s / 15–45 s / > 45 s), peticiones por segundo contra la línea de 15 r/s, el recorrido de cada
emergencia y los eventos del sistema. Desde la página se puede enviar una Emergency, lanzar la carga
k6 (ráfaga o ritmo de referencia) e inyectar fallas (apagar SMTP, Redis o el notifier).

- Es **plano de control**: solo lee los logs, Redis y Docker. No escribe en el camino de los eventos,
  así que observar no altera la latencia medida. Va en un perfil aparte y no cuenta como procesador.
- Para apagar contenedores monta el **socket de Docker** (equivale a root sobre Docker). Por eso
  publica el puerto solo en `127.0.0.1` y limita las acciones a `mailpit`, `redis` y `notifier`.
- Lanzar una carga reinicia la «ventana»: los contadores muestran solo esa corrida.
- El k6 lanzado desde el panel corre en su contenedor contra `http://gateway/events` (red interna).
  Para mediciones formales sigue valiendo correr k6 desde el equipo + `scripts/medir.py`.

## Requisitos

Docker Desktop corriendo · [k6](https://k6.io) (`brew install k6` / `winget install k6`) · Python 3.12+ solo para tests y `medir.py`.

## Correr en desarrollo (Mailpit, sin Gmail)

```bash
cp .env.example .env                       # Windows: copy .env.example .env
docker compose --profile dev up -d --build
k6 run k6/carga.js                         # 1000 eventos, 1 Emergency (la última iteración)
python3 scripts/medir.py                   # reporte de la corrida
```

Correos: http://localhost:8025 · Logs: `logs/` (JSON, hora Colombia, un archivo por réplica).

### Dos modos de carga

| Modo | Comando | Qué simula |
|---|---|---|
| Ráfaga | `k6 run k6/carga.js` | El k6 sin pausas. En local cada petición tarda ~2 ms, así que las 1000 llegan en < 1 s y solo pasan porque el burst (2000) es mayor que 1000 |
| Ritmo de referencia | `k6 run -e SLEEP_S=0.28 k6/carga.js` | La salida de referencia del enunciado: ~35 req/s durante ~28 s (en AWS el ritmo lo impone la latencia de ~176 ms) |

`-e EMERGENCIES=N` cambia cuántos `Emergency` se envían (por defecto 1: el enunciado pide un correo; el último siempre es la iteración final, el peor caso).

## k6 del profesor (oficial)

`k6/profesor.js` es el script que entregó el profesor el 06/10/2026 (original intacto en
`Modulo 2/Material-Clase/k6-script-profesor.js`). Solo cambian la URL (apuntaba a su API Gateway en
AWS) y el `handleSummary` que necesitan `medir.py` y el panel. Se lanza con `k6 run k6/profesor.js`
o con el botón **«Lanzar k6 del profesor»** del panel.

Ojo: el script calcula el índice como `(__VU - 1) * 100 + __ITER`, pero k6 reparte las 1000
iteraciones entre los VUs sin garantizar 100 por VU. El Emergency sale cuando el VU 10 pasa de
99 iteraciones, así que hay **0, 1 o varios** Emergency por corrida (medido el 06/10: 1, 2 y 1 en
tres corridas), y no necesariamente es la última petición.

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

Comparar el reloj del contenedor y el del equipo: `docker run --rm alpine date` vs `date`.
Si difieren, reiniciar Docker Desktop.

## Apagar

```bash
docker compose --profile dev down
```
