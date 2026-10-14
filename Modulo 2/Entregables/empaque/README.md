# Reto 2 — Alerta temprana para flota vehicular · Código fuente

**Diplomado en Arquitectura de Software y Cloud Computing — PUJ Cali · Módulo 2 · Grupo 2**

Integrantes: Freddy Erney Aparicio Marín · Camilo Andrés Céspedes Leguizamón · Daniel Mazo Serna

## Qué contiene este paquete

```
reto2-codigo-grupo2/
├── aws/      Solución oficial: API Gateway → Lambda ingesta → SQS → Lambda notifier → SES
└── local/    La misma arquitectura en Docker (desarrollo, plan B y panel de control de la demo)
```

| Carpeta | Para qué sirve | Autoría principal |
|---|---|---|
| [`aws/`](aws/README.md) | Código de las dos Lambdas desplegadas en AWS (us-east-2) y su configuración | Camilo Céspedes |
| [`local/`](local/README.md) | Sistema completo en Docker con pruebas automatizadas, scripts de k6 y el panel de control usado en la demo en vivo | Daniel Mazo |

## Decisiones que sostienen el código

- **Atributo priorizado: desempeño y escalabilidad.** La recepción responde en milisegundos y nunca
  espera al envío del correo: el `Emergency` se encola y un proceso aparte lo notifica.
- **Restricción que no se negocia: no perder un `Emergency`.** Si la alerta no se puede encolar, la
  ingesta responde **503** en vez de confirmar algo que no quedó guardado. Si el correo falla, hay
  reintentos acotados y una cola de mensajes fallidos (DLQ).
- **Entrega al-menos-una-vez:** un reintento puede producir un correo duplicado. Es el compromiso
  aceptado a cambio de no perder alertas.
- **Límite de tasa de 15 r/s con burst de 2000** en la puerta de entrada (API Gateway en AWS,
  nginx `limit_req` en local, con la misma semántica de token bucket).

## Mapa de equivalencias

| Enunciado / AWS | Local (Docker) |
|---|---|
| API Gateway (rate 15, burst 2000) | nginx `limit_req` |
| Lambda de ingesta | `alerta/ingest_app.py` (×2 réplicas) |
| SQS + DLQ | Redis Streams (consumer group, XACK, DLQ) |
| Lambda notifier | `alerta/notifier_worker.py` (×1) |
| SES | SMTP (Mailpit en desarrollo, Gmail en la demo) |
| CloudWatch Logs | Logs JSON en `local/logs/` |

Las dos versiones escriben **las mismas líneas JSON** (`EVENT_RECEIVED`, `EMERGENCY_RECEIVED`,
`EMAIL_SENT`, `EMAIL_RETRY`, `EMAIL_DLQ`…), con hora de Colombia. Esa es la evidencia de las horas
de recepción y de envío que pide la rúbrica.

## Lo que este paquete **no** incluye

- **Secretos:** no hay credenciales, contraseñas ni URLs reales de la cuenta AWS. Se configuran con
  `local/.env` y `local/.env.aws` a partir de los archivos `.example`.
- **La configuración de AWS hecha en consola** (API Gateway, colas, SES, roles IAM, EventBridge):
  está descrita en `aws/README.md`, pero no hay infraestructura como código. Es una brecha declarada.
- **Logs de la corrida oficial y documentación técnica:** se entregan aparte.
