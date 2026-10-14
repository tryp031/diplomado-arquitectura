# Reto 2 en AWS — Lambdas (solución oficial)

```
k6 → API Gateway (REST, rate 15 · burst 2000) → Lambda reto2-ingesta → SQS reto2-emergencias
     → Lambda reto2-notifier → Amazon SES → Gmail
                              ↘ (2 intentos fallidos) SQS reto2-emergencias-dlq
```

Región: **us-east-2**. Todos los recursos están en la misma región: mezclar regiones solo agrega
latencia y complica la identidad de SES, que es por región.

## Archivos

| Archivo | Lambda | Handler | Variables de entorno |
|---|---|---|---|
| `ingesta.py` | `reto2-ingesta` | `ingesta.lambda_handler` | `QUEUE_URL` |
| `notifier.py` | `reto2-notifier` | `notifier.lambda_handler` | `MAIL_FROM`, `MAIL_TO`, `DLQ_URL` |

Runtime Python 3. Solo dependen de `boto3`, que ya viene en el runtime de Lambda.

## Configuración en la consola

| Recurso | Configuración | Por qué |
|---|---|---|
| API Gateway (REST) | `POST /event-notification`, integración proxy con `reto2-ingesta`, stage `prod`, throttling rate 15 y burst 2000 | El enunciado pide el límite en API Gateway |
| `reto2-ingesta` | Concurrencia reservada 10, timeout de pocos segundos | Responde sin esperar al correo |
| SQS `reto2-emergencias` | Cola estándar, trigger hacia `reto2-notifier` con batch size 1 | Desacopla recepción y envío |
| `reto2-notifier` | Concurrencia reservada 2, timeout 15 s | 2 intentos de ~5 s y 1 s de espera (≤ 12 s) caben en el timeout |
| SQS `reto2-emergencias-dlq` | Cola de mensajes fallidos | El notifier deja ahí lo que no pudo enviar |
| Amazon SES | Identidad de remitente verificada (en sandbox, también el destinatario) | Servicio de correo nativo |
| CloudWatch Logs | Un grupo por Lambda, retención corta | Evidencia de horas de recepción y envío |
| EventBridge | Regla cada 5 min que invoca `reto2-notifier` con un evento vacío, activa solo durante la medición o la demo | Evita el arranque en frío en la primera alerta real. El handler recibe un evento sin `Records` y no procesa nada |
| IAM | Ingesta: `sqs:SendMessage`. Notifier: `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:SendMessage` (DLQ), `ses:SendRawEmail`, escritura en logs | Mínimo privilegio |

## Presupuesto de reintentos del notifier

El SDK se configura con `max_attempts=1` y timeouts cortos (conexión 2 s, lectura 3 s): los
reintentos los controla el código, no botocore, para que no agreguen tiempo oculto. Son 2 intentos
con 1 s de espera. Si ambos fallan, la alerta se envía explícitamente a la DLQ en vez de esperar al
reintento por visibilidad de SQS, que llegaría después de los 15 s de la rúbrica.

## Panel de control contra AWS (opcional)

El panel de `local/` puede observar esta solución en modo solo lectura (switch **AWS · nube**). Para
eso necesita un usuario IAM con esta política, configurado en `local/.env.aws`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": "logs:FilterLogEvents",
     "Resource": ["arn:aws:logs:us-east-2:<cuenta>:log-group:/aws/lambda/reto2-ingesta:*",
                  "arn:aws:logs:us-east-2:<cuenta>:log-group:/aws/lambda/reto2-notifier:*"]},
    {"Effect": "Allow", "Action": "sqs:GetQueueAttributes",
     "Resource": ["arn:aws:sqs:us-east-2:<cuenta>:reto2-emergencias",
                  "arn:aws:sqs:us-east-2:<cuenta>:reto2-emergencias-dlq"]}
  ]
}
```

## Brechas conocidas

- **Instancias:** la concurrencia reservada es 10 (ingesta) + 2 (notifier) = 12, por encima del
  límite de ≤ 10 instancias del enunciado. Bajo la carga de k6 se usaron 8 (6 de ingesta + 2 del
  notifier), pero el cupo configurado permitiría 12. La corrección es bajar la ingesta a 8 (8 + 2 = 10). Se declara como
  brecha, no se oculta.
- **Configuración en consola, sin IaC:** recrear el entorno depende de seguir esta tabla a mano.
- **SES puede caer en spam** por la política DMARC del remitente.
