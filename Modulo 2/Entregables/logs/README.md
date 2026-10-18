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
| **Hasta la llegada a Gmail** | última petición recibida (19:01:54.654) → llegada al buzón (19:01:55) | **entre 0,64 y 1,35 s** |

El panel fecha cada petición cuando la ingesta **responde** (igual que nginx en la versión local). En
el `Emergency`, eso ocurre después de encolarlo, así que su cifra es la más corta. Todas
cumplen con amplitud el criterio de 15 s.

## Llegada del correo a Gmail

### Captura del correo recibido

`correo-recibido-gmail.png`, tomada el 18/10/2026 del buzón del grupo (`grupo2arquitecturasoftware@gmail.com`).
Muestra el remitente «a través de amazonses.com» (enviado por SES), la hora de llegada (mar, 13 oct, 7:01 p. m.,
hora Colombia), la placa `RJJ-055` y el mismo `event_id` `ecf23272-82e4-4b40-96cc-0d627c9974bc` de los logs.
El resaltado amarillo de la placa es de la búsqueda en Gmail, no del correo.

### Cabeceras

Se tomó de las cabeceras del correo recibido (Gmail → «Mostrar original»), mismo `event_id`
`ecf23272-82e4-4b40-96cc-0d627c9974bc`:

```
Received: from e226-3.smtp-out.us-east-2.amazonaws.com ... by mx.google.com ...; Tue, 13 Oct 2026 17:01:55 -0700 (PDT)
Received: by 2002:a05:6f02:...  with SMTP id ...;                              Tue, 13 Oct 2026 17:01:55 -0700 (PDT)
ARC-Seal: i=1; ... t=1791936115                                               (= 19:01:55 hora Colombia)
Date: Wed, 14 Oct 2026 00:01:55 +0000                                         (puesto por SES al enviar)
```

17:01:55 PDT = **19:01:55 hora Colombia**. Gmail informa «Entregado tras 0 segundos». Como Gmail
registra con resolución de **segundos**, la llegada ocurrió entre 19:01:55.298 (`EMAIL_SENT`) y
19:01:55.999:

- `EMAIL_SENT` → buzón: **menos de 0,7 s**.
- Última petición de k6 → buzón: **entre 0,64 y 1,35 s**. Es el tramo completo que pide el criterio
  del profesor («del envío en k6 a la llegada del correo»), y queda muy por debajo de 15 s.

## Límites de esta evidencia

- Los relojes de AWS y de Gmail son distintos (ambos sincronizados por NTP). Su desfase es de
  milisegundos, menor que la resolución de un segundo de las cabeceras de Gmail.
- La cabecera de autenticación muestra `dmarc=fail (p=NONE)`: el remitente es una dirección
  `@gmail.com` enviada a través de SES. Esta vez el correo llegó a «Recibidos», pero con otro
  destinatario podría ir a spam. Es una brecha declarada: se corrige con un dominio propio verificado
  en SES.
- No es la única corrida: la #7 del mismo día (2 `Emergency`, 1,256 s según el panel) también
  cumplió. Se eligió la #2 porque generó exactamente un `Emergency`, que es lo que describe el
  enunciado. El script del profesor no lo garantiza: a veces envía 0 o 2.
