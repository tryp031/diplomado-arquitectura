# Aportes de Camilo — Módulo 2

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `m2-aws-opcion-b-camilo/` — Reto 2 desplegado en AWS (camino B)

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-10-09 (WhatsApp del grupo, 11:16) · subido al repo por Danny el mismo día |
| **Módulo** | 2 — Reto 2: alerta de flota vehicular |
| **Tema** | Opción B del Reto 2 en AWS: API Gateway → Lambda → SQS → Lambda → SES, con su diagrama de contenedores y la equivalencia con la opción local en Docker |
| **Tipo** | `reto` (código de las dos Lambdas) + `investigacion` (diagrama). El diagrama se declara a sí mismo como «documento de trabajo, no material oficial» |
| **Fuentes** | Diseño propio de Camilo en `arquitectura-aws-opcion-b.md` (**no compartido todavía**) · lógica de recepción del sistema local `Ejercicios/Reto2-Alerta-Flota/` · cuenta AWS de Camilo, región us-east-2 |
| **Estado** | recibido · ⬜ sin consolidar · paso 4 de 5 (SES sin verificar, k6 completo pendiente) |

**Contenido, sin modificar** (verificado con SHA-256 contra los archivos recibidos):

| Archivo | Qué es | SHA-256 (primeros 12) |
|---|---|---|
| `ingesta.py` | Lambda `reto2-ingesta`: valida, responde 200 y encola los Emergency en SQS | `e64c20d1a819` |
| `notifier.py` | Lambda `reto2-notifier`: consume SQS, envía por SES con 2 intentos y manda a la DLQ si agota los intentos | `e22c6d16039e` |
| `diagrama-contenedores-opcion-b.html` | C4 nivel 2, estado de construcción al 09/10 y tabla de equivalencias AWS ↔ Docker Compose | `52d886775ec1` |

Los nombres originales se conservan dentro de la carpeta (en vez de seguir la regla `m2-<tema>-camilo`)
porque el *handler* de cada Lambda depende del nombre del archivo (`ingesta.lambda_handler`,
`notifier.lambda_handler`). La carpeta sí sigue la convención.

**Mensaje con el que llegó:** «Les comparto el diagrama de contenedores y el código para la opción de
AWS, en las lambdas va el código, el resto es configuración en AWS. Está un comparativo con el local
desplegado en docker».

**Límites:**
- **Lo que no está en el repo:** la configuración de API Gateway (rate 15 / burst 2000), las colas,
  el redrive, la concurrencia, el IAM y el EventBridge Scheduler se hicieron **en la consola de AWS**.
  Hoy la opción B no se puede reproducir desde el repo.
- Las marcas «✓ validado» del diagrama las reporta Camilo; **nadie más las ha verificado**.
- El diagrama publica la URL del endpoint, que acepta POST sin autenticación. El repo es privado:
  **no subir este HTML a ningún sitio público.**
- Revisión técnica de Danny: `../danny/m2-revision-aws-opcion-b-danny.md`.
