# Foro M4 — comentario de Danny a un compañero

> PUBLICADO en Brightspace el 09/11/2026 por Danny (versión propia, más corta que el borrador).
> Responde al post de un compañero sobre la oscilación de niveles (15 transiciones en 13 s).
> Cubre el criterio «Interacción con compañeros» de la rúbrica.

## Texto publicado

Me pareció muy interesante tu hallazgo de las 15 transiciones en 13 segundos. Es un buen ejemplo de cómo la
observabilidad permite detectar problemas que las pruebas manuales no evidencian.

Como complemento, podrías aprovechar **AWS X-Ray** para incorporar trazas distribuidas y **CloudWatch con EMF y
SNS** para convertir los cambios de nivel en métricas y alertas. También sería útil definir un **SLO** que mida el
tiempo en degradación.

¿Consideraste ajustar la histéresis o establecer un tiempo mínimo por nivel para evitar esas oscilaciones? Creo
que sería una buena mejora para la estabilidad del sistema.
