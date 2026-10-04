# Reto 2 — Diseño de la solución local (alerta de flota vehicular)

> **Tipo:** `investigacion` / diseño propio (Danny + IA, 04/10/2026). **No** es material oficial.
> **Enunciado:** `Modulo 2/Material-Clase/Actividad-Reto2.md`. **Análisis previo:** `Modulo 2/Aportes/danny/m2-analisis-apertura-danny.md` §5.
> **Estado:** diseño aprobado por Danny el 04/10/2026. Pendiente que el profesor acepte una solución **local, no AWS** (pregunta del encuentro 06/10).

## 1. Decisiones tomadas

| # | Decisión | Por qué | A costa de |
|---|---|---|---|
| D1 | **Local con Docker Compose, no AWS** | La demo será desde nuestras máquinas; sin costo, sin cuenta AWS personal, sin sandbox SES | Hay que demostrar el equivalente de cada restricción AWS (ADR-001). Riesgo: el profesor no lo acepte |
| D2 | **Opción C** del análisis: la ingesta responde 200 de inmediato; solo los `Emergency` pasan por cola al notificador | El envío de correo no consume la concurrencia de la ingesta (ley de Little, §5.3b del análisis) | Una pieza más (cola) y entrega al-menos-una-vez |
| D3 | **Python + FastAPI** | Mismo stack del reto M1; el equipo lo corre en Mac y Windows | No es el stack diario de Danny (Java) |
| D4 | **Redis Streams** con consumer group | Mensaje pendiente hasta `XACK` ≈ visibilidad de SQS: permite reintento y no pérdida, con latencia de ms | Hay que explicar XACK/pendientes |
| D5 | **Puertos y adaptadores** (`EventQueue`, `Notifier`) | Portabilidad a SQS/SES = cambiar un adaptador; permite probar el worker sin red | Una capa de indirección pequeña |
| D6 | **LocalStack fuera del camino crítico** | No aplica throttling de API GW ni envía correo real; mediríamos el emulador | Se pierde la "foto AWS"; queda como extra opcional (adaptador SQS) |
| D7 | Atributo priorizado (propuesta): **desempeño — latencia de la alerta**, con no pérdida de eventos como restricción dura | Es lo que la rúbrica gradúa (2.5 / 1.5 / 0.5) | Costo y simplicidad; correos duplicados posibles |

## 2. Arquitectura

```text
k6 (1000 req / 30 s, 10 VUs)
  │
  ▼
nginx :8080  ── equivalente local de API Gateway
  │  limit_req  rate=15r/s  burst=2000  nodelay   → 429 si se agota el cubo
  ▼
ingest  (FastAPI, 2 réplicas)            POST /events · GET /health
  │  1. valida el payload (tolerante)            → 400 si inválido
  │  2. asigna event_id (UUID) = correlation id
  │  3. Position  → log EVENT_RECEIVED → 200
  │  4. Emergency → log EMERGENCY_RECEIVED → XADD "emergencies" → log EMERGENCY_ENQUEUED → 200
  │                 (si Redis falla → 503, nunca 200)
  ▼
Redis  (stream "emergencies", consumer group "notifiers")
  │
  ▼
notifier  (1 réplica, worker asyncio)
     XREADGROUP BLOCK → envío SMTP con concurrencia acotada (NOTIFIER_CONCURRENCY)
     → log EMAIL_SENT (ms_since_received) → XACK
     falla → EMAIL_RETRY (1 s, 2 s, 4 s) → stream "emergencies-dlq" + log EMAIL_DLQ → XACK
     al arrancar → XAUTOCLAIM de pendientes de consumidores caídos
```

**Equivalencias con el enunciado AWS (base del ADR-001):**

| Enunciado | Local | Cómo se demuestra |
|---|---|---|
| API Gateway rate 15, burst 2000 | nginx `limit_req` (token bucket: rate = recarga, burst = cubo) | Prueba negativa: burst 100 → aparecen 429 |
| ≤ 10 instancias de procesadores | 2 ingest + 1 notifier = 3 (5 contando nginx y Redis) | `docker compose ps` durante la carga |
| SQS | Redis Streams | — |
| SES / correo | SMTP de Gmail (587, STARTTLS, App Password) | Correo recibido + log `EMAIL_SENT` |

## 3. Componentes

Un solo paquete Python (`alerta/`), una imagen, dos comandos (ingest y notifier).

| Módulo | Responsabilidad | Depende de |
|---|---|---|
| `domain.py` | Modelo `VehicleEvent`; validación **tolerante**: obligatorios `type` y `vehicle_plate`, el resto opcional, campos extra ignorados; `is_emergency()` (`type == "Emergency"`, comparación exacta) | nada |
| `ports.py` | `EventQueue` y `Notifier` como `typing.Protocol` | `domain` |
| `adapters/redis_queue.py` | `XADD`, `XREADGROUP`, `XACK`, `XAUTOCLAIM`, DLQ | `redis` (asyncio) |
| `adapters/smtp_notifier.py` | Construye el correo (formato del enunciado) y lo envía | `aiosmtplib` |
| `ingest_app.py` | FastAPI: `POST /events`, `GET /health` | `domain`, `ports` |
| `notifier_worker.py` | Bucle de consumo, semáforo de concurrencia, reintentos con backoff, DLQ | `ports` |
| `logjson.py` | Una línea JSON por evento, hora local `-05:00` con milisegundos | — |
| `config.py` | Variables de entorno con valores por defecto | — |

**Correo:** asunto `🚨 Alerta de Emergencia 🚨`; cuerpo con título «Alerta de Emergencia», `Placa`, `Estado`, `Evento: Emergency`, `event_id` y hora de recepción.

**Configuración (`.env`, nunca versionado; `.env.example` sí):** `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_STARTTLS`, `MAIL_FROM`, `MAIL_TO`, `NOTIFIER_CONCURRENCY` (def. 5), `REDIS_URL`.

**Mailpit** (perfil `dev` de compose) es el SMTP de desarrollo: no gasta cuota de Gmail. Gmail solo en mediciones y demo.

## 4. Logs

JSON por línea a stdout y a `logs/<servicio>.log` (volumen). Campos: `ts`, `service`, `event`, `event_id`, `plate`, y según el evento `ms_since_received`, `attempt`, `error`.

Eventos: `EVENT_RECEIVED`, `EMERGENCY_RECEIVED`, `EMERGENCY_ENQUEUED`, `EMAIL_SENT`, `EMAIL_RETRY`, `EMAIL_DLQ`.

Riesgo: reloj de la VM de Docker Desktop desfasado tras suspender el Mac → comparar `docker run --rm alpine date` con `date` antes de medir.

## 5. Manejo de errores

| Fallo | Respuesta | Táctica |
|---|---|---|
| Payload inválido | 400 | Validación tolerante para no perder el «100 %» |
| Redis caído con un `Emergency` | 503 (`Position` siguen con 200) | Fallar visible antes que confirmar una alerta perdida |
| SMTP falla | 3 reintentos (1/2/4 s) → DLQ | Reintento + cola de mensajes fallidos |
| Notifier cae a mitad de un envío | Mensaje queda pendiente → `XAUTOCLAIM` al reiniciar | No pérdida; costo: duplicados |
| Duplicados | **Tolerados y documentados** | Sin idempotencia: ningún ASR la exige |
| Límite de Gmail (~500/día, Probable) | Vigilar en días de muchas corridas | — |

## 6. Medición

- `k6/carga.js` provisional: `shared-iterations`, 1000 iteraciones, 10 VUs, `maxDuration 30s`, `EMERGENCY_RATIO` configurable; al final escribe la hora del último envío. Se reemplaza por el k6 oficial.
- `scripts/medir.py`: por corrida reporta recibidos, 429 de nginx, p95 de ingesta (de k6), recepción → `EMAIL_SENT`, y **último envío de k6 → `EMAIL_SENT`** (medida de la rúbrica). La hora de llegada a Gmail se toma a mano («Mostrar original»).
- Plan: ≥ 5 corridas contra Gmail + prueba negativa del limitador. Resultados en `docs/resultados/`.

## 7. Pruebas

| Prueba | Riesgo cubierto |
|---|---|
| Unitarias `domain` (payload mínimo, extras, `type` desconocido, sin placa) | Validación demasiado estricta tumba el 100 % |
| Unitarias del worker con puertos falsos (éxito, falla → reintentos → DLQ, concurrencia acotada) | Perder un `Emergency` en silencio |
| Unitaria de `ingest_app` con cola falsa (Position 200, Emergency encola, cola caída → 503) | Contrato HTTP |
| Integración compose + Mailpit: 1 `Emergency` → `EMAIL_SENT` y correo en Mailpit | Cableado |
| k6 burst 2000 → 0 % fallos · burst 100 → 429 | Restricciones A2 y de tasa |

TDD en `domain`, `ingest_app` y worker.

## 8. Documentación del entregable (rúbrica del PDF)

ADR-001 local vs AWS · ADR-002 atributo priorizado («priorizamos X, por Y, a costa de Z») · ADR-003 Redis Streams y puertos · diagrama C4 (contexto y contenedores, Mermaid) · tabla de tácticas citando `Modulo 2/Material-Clase/Tacticas-*.md` (vale 1.0) · resultados de medición con análisis.

## 9. Fuera de alcance

Autenticación, HTTPS, persistencia de `Position`, dashboard, IMAP, idempotencia, Kubernetes, LocalStack (extra opcional).

## 10. Preguntas abiertas (encuentro 06/10)

1. ¿Se acepta la solución local en lugar de AWS?
2. ¿Cuántos `Emergency` trae el k6 oficial y es un correo por evento? (Si son muchos, evaluar modo «agrupar».)
3. ¿Cuándo y cómo se entrega el k6 oficial?

## 11. Cronograma

04–05/10 núcleo con Mailpit · 06/10 encuentro · 07–11/10 Gmail, k6 oficial, ADRs · 12/10 medición formal · 13/10 encuentro 2 · 14–18/10 documento y presentación · 19/10 entrega.
