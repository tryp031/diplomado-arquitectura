# Revisión de la opción B del Reto 2 (AWS) — aporte de Camilo

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-10-09 |
| **Módulo** | 2 — Reto 2: alerta de flota vehicular |
| **Tema** | Revisión técnica del despliegue en AWS de Camilo, ajustes propuestos y agenda para la reunión del domingo 11/10 |
| **Tipo** | `investigacion` — elaborada con IA; **no es material oficial** ni decisión del equipo |
| **Fuentes** | `../camilo/m2-aws-opcion-b-camilo/` (código y diagrama) · `Material-Clase/Actividad-Reto2.md` · `Ejercicios/Reto2-Alerta-Flota/alerta/{domain,ports}.py` · notas de Freddy del 06/10 (§10 de `m2-preguntas-encuentro-0610-danny.md`) |
| **Estado** | borrador · para discutir el 11/10 |

> **Lo que esta revisión NO cambia:** el aporte de Camilo queda intacto (regla del equipo). Los
> ajustes son **propuestas**: Camilo decide qué aplica en su código y el equipo decide en el consolidado.
>
> Etiquetas: **Curso** = lo dice el material · **Complementario** = conocimiento externo ·
> **Recomendación** = criterio de arquitecto. Confianza: **Seguro** / **Probable** / **Suposición**.

---

## 1. Veredicto

**Sirve, y probablemente es la mejor candidata para la demo medida.** Pero hoy **no se puede entregar
tal como está**: lo que el reto evalúa (límite de 15 r/s con burst 2000, DLQ, concurrencia ≤ 10)
vive en clics de consola dentro de una sola cuenta, no en el repo.

| Tema | Opción A (local, Docker) | Opción B (AWS, Camilo) |
|---|---|---|
| Parecido con el enunciado | Imita API Gateway con nginx `limit_req` | **Es lo que nombra el enunciado**. «rate / burst» son términos de API Gateway (*Curso*) |
| HTTPS (brecha del 06/10) | Sin TLS | **Viene incluido** con API Gateway (*Seguro*) |
| ≤ 10 instancias | Lo controlamos con las réplicas | Lo impone la cuota de la cuenta (§3.4) |
| `200 OK` en las 1.000 peticiones | Responde `429` por encima del límite | **Igual**: API Gateway también responde `429` (*Seguro*). Sigue abierta |
| Reproducible desde el repo | Sí (`docker compose up`) | **No** (§2.2) |
| Medido con el k6 del profesor | Sí (06/10, 1,33 s) | **No todavía** (paso 5) |

**El valor académico está en tener las dos.** Es la misma arquitectura (ingesta → cola → notifier →
DLQ) desplegada de dos formas. Eso demuestra que las decisiones salen de los atributos de calidad y no
de la tecnología, que es el hilo conductor que el profesor echó de menos en M1 (*Recomendación*).

---

## 2. Bloqueantes para entregar la opción B

### 2.1 SES sin verificar → no sale ningún correo
Lo único que falta para cerrar el camino. **Acción de Camilo:** hacer clic en el enlace de
verificación que SES envió a `notificadoremergenciaflotas@gmail.com`. En el sandbox de SES hay que
verificar también el destinatario, pero aquí remitente y destinatario son la misma dirección (*Seguro*).

### 2.2 La configuración no está en el repo
El enunciado pide como entregable «toda la implementación» (*Curso*). En la opción B la implementación
**es** la configuración: el throttling del stage, la visibilidad de 90 s, el redrive a los 3 intentos,
la concurrencia máxima del trigger, los permisos IAM y el scheduler. Opciones, de menor a mayor costo:

| Opción | Esfuerzo | Qué gana | Qué no resuelve |
|---|---|---|---|
| **a. Exportar la configuración real** a JSON y versionarla | ~30 min | Evidencia verificable de lo que se configuró | No permite volver a crear el entorno |
| **b. Template SAM/CloudFormation** (recomendada) | 2–4 h | Reproducible, revisable en un PR, se borra con un comando | Hay que probarlo en una cuenta limpia |
| c. Runbook con capturas | ~1 h | Lo entiende cualquiera | Se desactualiza en silencio |

Comandos para la opción **a** (*Seguro*: son de la AWS CLI v2. Los nombres salen del diagrama):

```bash
aws apigateway get-stage --rest-api-id ofuhehmw59 --stage-name prod        # throttling del stage
aws lambda get-function-configuration --function-name reto2-ingesta
aws lambda get-function-configuration --function-name reto2-notifier
aws lambda list-event-source-mappings --function-name reto2-notifier       # batch size y concurrencia máxima
aws lambda get-account-settings                                            # cuota real de concurrencia
aws sqs get-queue-attributes --attribute-names All --queue-url "$(aws sqs get-queue-url --queue-name reto2-emergencias --query QueueUrl --output text)"
aws sqs get-queue-attributes --attribute-names All --queue-url "$(aws sqs get-queue-url --queue-name reto2-emergencias-dlq --query QueueUrl --output text)"
aws scheduler get-schedule --name reto2-calentador-notifier
```

Antes de versionar las salidas hay que revisarlas: pueden traer ARNs con el ID de la cuenta.

### 2.3 Falta la medición de punta a punta
El diagrama marca el paso 5 (k6 completo) como pendiente. Sin esa corrida no sabemos si la opción B
cumple el corte de 15 s. Para sacar la cifra de los logs, una consulta de CloudWatch Logs Insights
sobre el grupo de la notifier (*Probable*: Insights detecta solo los campos de los logs que son JSON):

```text
fields @timestamp, event_id, plate, attempt, ms_since_received
| filter event = "EMAIL_SENT"
| stats count() as correos, avg(ms_since_received) as prom_ms, max(ms_since_received) as max_ms
```

Ojo: `ms_since_received` mide **recepción → envío por SES**. La rúbrica mide **último envío de k6 →
correo recibido** (*Curso*). La diferencia (tiempo de Gmail y lo que quede de k6) hay que medirla
aparte, igual que en la opción local.

---

## 3. Importantes

### 3.1 El presupuesto de reintentos se come la rúbrica (*Seguro*, es aritmética)
Peor caso con éxito en el segundo intento: 5 s (el primero agota el timeout) + 1 s de espera + hasta
5 s del segundo = **~11 s dentro de la Lambda**, más la espera de SQS hasta la Lambda, un posible
arranque en frío y la entrega de Gmail. Frente a 15 s queda muy poco margen.

**Ajuste propuesto (Camilo decide):** como SES suele responder en menos de un segundo (*Probable*),
bajar a `connect_timeout=1, read_timeout=2` deja el peor caso cerca de 7 s y conserva los dos intentos.
**Trade-off:** un timeout más corto corta con más frecuencia un envío que era solo lento, y eso manda
más alertas a la DLQ. Hay que decidirlo con datos de la corrida del §2.3, no a ojo.

### 3.2 Remitente `@gmail.com` enviado por SES → riesgo de spam o rechazo (*Probable*)
SES firma con su propio dominio, así que el `From: @gmail.com` no pasa la alineación DMARC de
gmail.com. Gmail puede mandar el correo a spam o rechazarlo, y eso arruina la demo aunque el sistema
funcione. **Prueba:** enviar uno y revisar en Gmail «Mostrar original» qué dicen SPF, DKIM y DMARC.
**Alternativa:** si alguien tiene un dominio propio, verificarlo en SES con DKIM y usarlo como remitente.

### 3.3 La lógica de dominio ya está duplicada y diverge
`ingesta.py` vuelve a escribir lo que hace `alerta/domain.py`, y ya hay diferencias:

| Entrada | Local (`domain.py`) | AWS (`ingesta.py`) |
|---|---|---|
| `"vehicle_plate": 123` | `"123"` | `"DESCONOCIDA"` |
| `"vehicle_plate": " ABC123 "` | `"ABC123"` (aplica `strip`) | `" ABC123 "` |
| `"status": 5` | `None`, y el correo dice `—` | `5`, y el correo dice `5` |

Con el k6 del profesor probablemente no se note (*Suposición*), pero si se presentan como «la misma
lógica en dos despliegues», hoy no lo son.

**Ajuste propuesto:** `domain.py` solo usa la librería estándar, así que puede ir dentro del zip de
las dos Lambdas tal cual. Así `ingesta.py` llamaría a `VehicleEvent.from_payload(...)` y
`EmergencyAlert.to_fields()`. `ports.py` ya lo anticipaba: *«Redis/SMTP hoy, SQS/SES mañana»*.
Es el argumento más fuerte de la arquitectura hexagonal en la exposición. Si no se hace, queda como
**deuda media**: cada cambio de regla hay que hacerlo dos veces.

### 3.4 «Concurrencia reservada 8 bloqueada» es cumplimiento, no un problema
Las cuentas nuevas traen una cuota baja de ejecuciones concurrentes, y Lambda exige dejar un mínimo
sin reservar. Por eso no se puede reservar nada (*Probable*. Confirmar con `get-account-settings`).
Si la cuota es 10, la cuenta **impone** el «máximo 10 instancias activas» del enunciado entre todas las
Lambdas. Hay que presentarlo como cumplimiento de la restricción. Detalles:
- la concurrencia máxima 2 del trigger de SQS es el mínimo que AWS permite (*Seguro*);
- el calentador ocupa un espacio de concurrencia cada 5 min.

### 3.5 `200` vs `429`: sigue abierta en las dos opciones
Por encima de 15 r/s y con el burst agotado, API Gateway responde `429` igual que nginx. La decisión
que dejó abierta la reunión del 06/10 aplica a las dos opciones, no se resuelve cambiando de opción.

---

## 4. Mejoras recomendadas y nitpicks

- **Mejora — duplicados.** SQS estándar entrega al menos una vez. Si la notifier envía el correo y
  muere antes de terminar, el mensaje vuelve y sale un correo duplicado. Con un timeout de 15 s y un
  presupuesto de 12 s es poco probable, y un duplicado es mejor que una alerta perdida. **Documentarlo
  como decisión** (*Recomendación*).
- **Mejora — endpoint público.** Acepta POST sin autenticación y su URL está en el diagrama.
  Recomendado: alarma de presupuesto en AWS, apagar el calentador fuera de las mediciones y borrar los
  recursos después de la entrega.
- **Mejora — evidencia.** Las dos Lambdas registran `event_id`, así que se puede cruzar recepción con
  envío. Hay que guardar la salida de la consulta del §2.3 como evidencia de la entrega.
- **Nitpick.** `return {"batchItemFailures": []}` solo tiene efecto si el trigger tiene activado
  `ReportBatchItemFailures`. Con batch size 1 no cambia nada.
- **Nitpick.** Verificar que el runtime Python 3.14 está disponible en us-east-2 (*Suposición*: no lo
  comprobé).
- **Bien hecho.** Responde `503` si no pudo encolar y nunca confirma una alerta perdida. Los reintentos
  los controla el código y no botocore (`max_attempts=1`). Manda a la DLQ de forma explícita sin esperar
  al redrive, y el calentador no rompe nada porque `event.get("Records", [])` queda vacío.

---

## 5. Pedidos a Camilo antes del domingo

1. Verificar la identidad de SES (§2.1).
2. Compartir `arquitectura-aws-opcion-b.md`: el diagrama dice que sale de ahí y tiene las decisiones
   (la región, el presupuesto de reintentos).
3. Si alcanza: una corrida con `k6/profesor.js` contra el endpoint + la consulta del §2.3 + revisar
   si el correo llegó a la bandeja o a spam (§3.2).
4. Exportar la configuración (§2.2 opción a). Es lo mínimo para que el repo refleje lo que existe.

## 6. Agenda propuesta para el domingo 11/10

| # | Decisión | Opciones | Mi recomendación |
|---|---|---|---|
| 1 | ¿Cuál opción se mide en la demo? | A · B · las dos | **B como demo, A como entorno de desarrollo y plan B**, y la comparación como argumento en el documento |
| 2 | ¿Cómo se vuelve reproducible B? | exportar · SAM · runbook | Exportar ya, SAM si alcanza el tiempo |
| 3 | ¿Dominio compartido? | reutilizar `domain.py` · aceptar la divergencia | Reutilizar: cuesta poco y refuerza la exposición |
| 4 | ¿`200` o `429`? | mantener 429 · subir el límite | Preguntar al profesor antes de tocar el limitador |
| 5 | ¿Timeouts de SES? | 2+3 s · 1+2 s | Decidir con los datos de la primera corrida |
| 6 | ¿Quién entrega qué? | — | El envío es **individual** (*Curso*): acordar que los tres suban el mismo consolidado |
| 7 | ¿Se acepta la opción local? | — | Confirmar con el profesor: el enunciado da por hecho AWS (*Curso*) y no dice nada sobre otras opciones |
