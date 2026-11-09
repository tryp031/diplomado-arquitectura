# Aportes de Camilo — Módulo 4

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `m4-observabilidad-serverless-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA |
| **Fecha de recepción** | 2026-11-09 |
| **Módulo** | 4 — Observabilidad serverless (métricas, logs y trazas) |
| **Tema** | Qué despliega el Serverless Observability Workshop, cómo se ejecutó en AWS (us-east-2) y qué se verificó en métricas, logs y trazas |
| **Tipo** | `investigacion` — documento derivado, elaborado con IA; **no es material oficial** |
| **Fuentes** | `aws-samples/serverless-observability-workshop` (licencia MIT-0, clon local, consultado 2026-11-08) · videos del taller del Módulo 4 (2026-11-08) · ejecución propia en la cuenta de AWS de Camilo, us-east-2 (2026-11-08) · `Modulo 2/Aportes/camilo/` (`medir-aws.py`, `arquitectura-aws-opcion-b.md`) para la conexión con el Módulo 2 |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué contiene:** una página con 17 secciones. Describe la aplicación de ítems del taller (API Gateway, tres Lambdas y
DynamoDB, más SNS y una función de notificación en la app de trazas), los recursos que crea el despliegue con SAM, la
preparación del entorno, el despliegue paso a paso y las pruebas de la API. Después recorre las tres señales de
observabilidad: métricas propias en CloudWatch (síncronas y asíncronas), logs estructurados con Logs Insights y
trazas distribuidas con X-Ray. Cierra con los conceptos clave, la conexión con otros módulos, los hallazgos y
contradicciones, los problemas y lecciones, el alcance y los pendientes, las preguntas abiertas, la limpieza de
recursos y las fuentes.

**Límites:**
- **Origen mezclado.** La redacción y el código están escritos con Claude. Los despliegues, las pruebas y lo visto en
  CloudWatch y X-Ray son de la ejecución real. El documento marca cada afirmación con su origen (curso, complementario,
  recomendación) y su confianza (verificado, preparado).
- **Lo «preparado» no se probó.** El código marcado así está escrito, pero no se desplegó ni se ejecutó.
- **Guía web del taller sin consultar.** `serverless-observability.workshop.aws` solo aparece referenciada en el
  README del repo; el código de los handlers se escribió a partir del repo, no de la guía.
- **Sin material oficial contrastado.** El repo aún no tiene el temario ni la actividad del Módulo 4 en
  `Material-Clase/`. Los pasos y conceptos de los videos vienen de lo que Camilo anotó, no de una transcripción
  versionada.
- **Seguridad.** No incluye credenciales, identificadores de cuenta ni direcciones de la API desplegada. El taller se
  ejecutó con permisos amplios por simplicidad; el documento lo señala y recomienda mínimo privilegio.
- **Costos.** Los stacks siguen activos hasta ejecutar `sam delete` en las dos aplicaciones; lo creado a mano en la
  consola (alarmas, tópicos, dashboards) se borra aparte.
