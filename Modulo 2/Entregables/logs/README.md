# Logs de ejecución — corrida oficial del Reto 2 (AWS)

Entregable 3 del enunciado: evidencia de la **recepción del `Emergency`** y del **envío exitoso del
correo**.

| Dato | Valor |
|---|---|
| Fecha | 13/10/2026, 19:01:33 → 19:01:55 (hora de Colombia, UTC−5) |
| Entorno | Solución oficial en AWS (us-east-2): API Gateway → Lambda ingesta → SQS → Lambda notifier → SES |
| Carga | Script k6 oficial del profesor (10 VUs, 1000 iteraciones), solo con la URL apuntando a nuestro API Gateway |
| Peticiones | 1000 aceptadas · 0 rechazadas (429) |
| Eventos | 999 `Position` + 1 `Emergency` (petición 992 de 1000) |
| Correos | 1 enviado en el primer intento · 0 reintentos · 0 en la DLQ |
| Origen | CloudWatch Logs de las dos Lambdas, exportados desde el panel de control (corrida #2) |

## Archivos

- `corrida-oficial-aws-2026-10-13.log`: una línea JSON por evento, ordenadas por hora.
- `corrida-oficial-aws-2026-10-13.csv`: lo mismo en columnas (`ts, service, replica, event, event_id, plate, detalle`), para abrir en una hoja de cálculo.

## Las tres líneas que prueban el flujo

```json
{"ts": "2026-10-13T19:01:54.543-05:00", "service": "ingest",   "event": "EMERGENCY_RECEIVED", "event_id": "ecf23272-82e4-4b40-96cc-0d627c9974bc", "plate": "RJJ-055"}
{"ts": "2026-10-13T19:01:54.807-05:00", "service": "ingest",   "event": "EMERGENCY_ENQUEUED", "event_id": "ecf23272-82e4-4b40-96cc-0d627c9974bc", "plate": "RJJ-055"}
{"ts": "2026-10-13T19:01:55.298-05:00", "service": "notifier", "event": "EMAIL_SENT",         "event_id": "ecf23272-82e4-4b40-96cc-0d627c9974bc", "plate": "RJJ-055", "attempt": 1, "ms_since_received": 756}
```

El mismo `event_id` une la recepción con el envío.

## Tiempo medido

| Tramo | Desde → hasta | Valor |
|---|---|---|
| Rúbrica: último envío de k6 → envío del correo | última petición recibida (19:01:54.654) → `EMAIL_SENT` | **0,644 s** |
| Emergency → correo | `EMERGENCY_RECEIVED` → `EMAIL_SENT` | **0,756 s** |
| Indicador del panel | última respuesta de la ingesta (19:01:54.807) → `EMAIL_SENT` | 0,491 s |

El panel fecha cada petición cuando la ingesta **responde** (igual que nginx en la versión local). En
el `Emergency`, eso ocurre después de encolarlo, así que su cifra es la más corta de las tres. Las tres
cumplen con amplitud el criterio de 15 s.

## Límites de esta evidencia

- `EMAIL_SENT` es la hora en que **SES aceptó** el mensaje, no la de llegada al buzón de Gmail. Esa
  la pone Gmail y no aparece en estos logs.
- No es la única corrida: la #7 del mismo día (2 `Emergency`, 1,256 s según el panel) también
  cumplió. Se eligió la #2 porque generó exactamente un `Emergency`, que es lo que describe el
  enunciado. El script del profesor no lo garantiza: a veces envía 0 o 2.
