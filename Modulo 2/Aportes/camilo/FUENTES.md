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
| **Fuentes** | Diseño propio de Camilo en `arquitectura-aws-opcion-b.md` · lógica de recepción del sistema local `Ejercicios/Reto2-Alerta-Flota/` · cuenta AWS de Camilo, región us-east-2 |
| **Estado** | recibido · ⬜ sin consolidar · **los 5 pasos del despliegue completados (actualización del 12/10, ver abajo)** |

**Contenido original (09/10), sin modificar** (verificado con SHA-256 contra los archivos recibidos):

| Archivo | Qué es | SHA-256 (primeros 12) |
|---|---|---|
| `ingesta.py` | Lambda `reto2-ingesta`: valida, responde 200 y encola los Emergency en SQS | `e64c20d1a819` |
| `notifier.py` | Lambda `reto2-notifier`: consume SQS, envía por SES con 2 intentos y manda a la DLQ si agota los intentos | `e22c6d16039e` |

Los nombres originales se conservan dentro de la carpeta (en vez de seguir la regla `m2-<tema>-camilo`)
porque el *handler* de cada Lambda depende del nombre del archivo (`ingesta.lambda_handler`,
`notifier.lambda_handler`). La carpeta sí sigue la convención.

**Mensaje con el que llegó (09/10):** «Les comparto el diagrama de contenedores y el código para la
opción de AWS, en las lambdas va el código, el resto es configuración en AWS. Está un comparativo con
el local desplegado en docker».

**Actualización del 12/10/2026 — subida directa por Camilo (no por WhatsApp/Danny esta vez):**
- `diagrama-contenedores-opcion-b.html` **reemplazado** por la versión actualizada: incluye una vista
  general nueva (panel de control + k6 → AWS colapsado → Gmail) antes del detalle, y el detalle con los
  datos ya corregidos — SES verificado y enviando correo real (`grupo2arquitecturasoftware@gmail.com`,
  cae en spam por desalineación DMARC, documentado como límite conocido), concurrencia reservada 10 en
  `reto2-ingesta` (igualando los VUs del k6 oficial) y 2 + trigger máx. 2 en `reto2-notifier`, y los
  pasos 4 y 5 marcados como completados con el resultado real: 1000/1000, 0% fallos, avg 119.65 ms.
- `arquitectura-aws-opcion-b.md` **agregado** — el diseño completo que hasta ahora no se había
  compartido (quedaba pendiente desde la revisión de Danny, pedido #2). Es la fuente de verdad detrás
  del diagrama: flujo, componentes, presupuesto de reintentos, decisión de región con su evidencia, y
  la sección 9 con el estado de cada paso del despliegue.

**Límites:**
- **Lo que no está en el repo:** la configuración de API Gateway (rate 15 / burst 2000), las colas, el
  redrive, la concurrencia, el IAM y el EventBridge Scheduler se hicieron **en la consola de AWS**. La
  opción B sigue sin poder reproducirse solo desde el repo (sigue abierto el pedido de Danny de
  exportarla o pasarla a IaC, §2.2 de su revisión).
- Las marcas «✓ validado» y los números del diagrama los reporta Camilo; **nadie más del equipo los ha
  verificado de forma independiente**.
- El diagrama publica la URL del endpoint, que acepta POST sin autenticación. El repo es privado:
  **no subir este HTML a ningún sitio público.**
- La medición automática de la sección 12 de `m2-respuestas-exposicion-12.1-12.2.md` (ver abajo) mide
  "recepción en ingesta → envío por SES", no literalmente "envío de k6 → correo recibido en Gmail" que
  es la redacción exacta de la rúbrica — declarado así a propósito, no es un error.
- Revisión técnica de Danny: `../danny/m2-revision-aws-opcion-b-danny.md` (todavía no releída contra
  esta actualización).

---

## `m2-respuestas-exposicion-12.1-12.2.{md,html}` — Preparación para la exposición

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA |
| **Fecha de recepción** | 2026-10-12, subido directamente por Camilo |
| **Módulo** | 2 — Reto 2: alerta de flota vehicular |
| **Tema** | Respuesta a los puntos 12.1 (tabla de temas de teoría) y 12.2 (16 posibles preguntas de la exposición) del documento de Danny `m2-preguntas-encuentro-0610-danny.md`, con argumentos técnicos y mediciones reales del camino AWS |
| **Tipo** | `investigacion` — elaborado con IA, apoyado en mediciones reales de la cuenta de AWS de Camilo; **no es material oficial** ni respuesta confirmada por el docente |
| **Fuentes** | `m2-aws-opcion-b-camilo/arquitectura-aws-opcion-b.md` · `m2-preguntas-encuentro-0610-danny.md` · sistema local `Ejercicios/Reto2-Alerta-Flota/` (comparación) |
| **Estado** | borrador, para repasar en equipo antes de la exposición |

**Límites:**
- Cada respuesta trae etiquetas de origen (Curso/Complementario/Recomendación) y de confianza
  (Seguro/Probable/Suposición) — las marcadas *Probable* o *Suposición* son razonamiento propio, no
  verificación directa.
- La pregunta 12 queda explícitamente incompleta: mide el tramo bajo control propio, no el tramo exacto
  que pide la rúbrica (envío de k6 → correo recibido en Gmail) — el documento mismo dice qué falta para
  cerrarla (el "Mostrar original" de un correo real en Gmail).
- No se ha revisado en equipo; conviene que Danny y Freddy la lean antes de usarla en la exposición real.

---

## `m2-cuadernillo-estudio-camilo.html` — Cuadernillo de estudio del Módulo 2

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA |
| **Fecha de recepción** | 2026-10-19 |
| **Módulo** | 2 — Requerimientos de calidad, ASR y tácticas de arquitectura |
| **Tema** | Cuadernillo interactivo de estudio del M2, mismo formato del cuadernillo del M1 |
| **Tipo** | `investigacion` — documento derivado, elaborado con IA; **no es material oficial** |
| **Fuentes** | Material oficial del M2 en `Material-Clase/`: los 4 Genially, el video de Seguridad, los 5 decks de tácticas y el enunciado del Reto 2 · Bass, Clements, Kazman, *Software Architecture in Practice* 4ª ed. (citado por los decks) |
| **Estado** | recibido · ⬜ sin consolidar |

**Qué contiene:** 17 secciones plegables: ASR y escenario de calidad, ADD, tácticas y patrones de
disponibilidad, desempeño, seguridad e interoperabilidad, usabilidad y desplegabilidad (complementarios),
confusiones frecuentes, costo de cada táctica, el Reto 2 leído con las tácticas, 10 casos con respuesta
oculta, un emparejamiento de 10 tácticas con su familia y un quiz de 20 preguntas.

**Límites:**
- Las secciones 10 (confusiones), 11 (costos) y 12 (Reto 2) son aporte propio, no del curso; el texto lo dice.
- Las cifras de la sección 12 son las de la ejecución oficial del 13/10/2026 en AWS (us-east-2).
- El deck de Interoperabilidad solo llega como transcripción plana: «descubrir servicios» no tiene detalle.
- Convive con `../danny/m2-cuaderno-estudio-danny.md` (notas en prosa); este es la versión interactiva.
- Las preguntas del quiz son propias; no reproducen la autoevaluación oficial de Brightspace.
