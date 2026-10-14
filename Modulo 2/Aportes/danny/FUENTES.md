# Aportes de Danny — Módulo 2

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `m2-analisis-apertura-danny.md`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-30 (reescrito esa tarde con el enunciado y los Genially) |
| **Módulo** | 2 — Tácticas de arquitectura y atributos de calidad |
| **Tema** | Visión del módulo, errores/ambigüedades del material, conexión con M1 y plan preliminar de la actividad |
| **Tipo** | `apunte` — elaborado con IA; **no es material oficial** |
| **Fuentes** | Material oficial M2 (Brightspace): 5 decks de tácticas como texto · `Actividad-Reto2.pdf` (enunciado) · 4 Genially (transcripción) · «Rúbrica M2» de Brightspace (criterios y niveles; descriptores vacíos) · Bass, Clements, Kazman, *Software Architecture in Practice* 4ª ed. (citado por los decks) · resultados del Reto M1 |
| **Estado** | vigente · ⬜ sin consolidar |

**Límites:** la autoevaluación M2 **no se abrió** (a propósito), el **video de Seguridad** no se capturó
(YouTube bloqueó la transcripción) y el **script de k6** no está disponible. El análisis de servicios
AWS del §5 es conocimiento general **sin probar en la cuenta** (Probable). Las críticas del §3 y el §5 son
conocimiento complementario o recomendación, no del curso. Los Genially se leyeron como transcripción
plana: pierden el orden de las láminas, los pop-ups y las imágenes.

---

## `m2-cuaderno-estudio-danny.md` (+ `.html` generado)

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-30 |
| **Módulo** | 2 — Requerimientos y Tácticas de Arquitectura de Software |
| **Tema** | Cuaderno de estudio: ASR y ADD, escenario de calidad, tácticas por atributo, matriz de trade-offs, Reto 2 como laboratorio, autoevaluación y glosario |
| **Tipo** | `apunte` — notas de estudio propias, elaboradas con IA; **no es material oficial** |
| **Fuentes** | Material oficial M2: 5 decks de tácticas, 4 Genially y enunciado del Reto 2 · Bass, Clements, Kazman, *Software Architecture in Practice* 4ª ed. (citado por los decks) |
| **Estado** | vigente · ⬜ sin consolidar |

**Qué contiene:** método de tres pasadas · la cadena ASR → escenario → táctica → patrón → trade-off ·
regla de priorización del curso y método ADD · escenario de calidad con plantilla · disponibilidad,
desempeño, seguridad e interoperabilidad · matriz de trade-offs · ejercicios del Reto 2 · enlace a la
autoevaluación interactiva · dos gráficas de cálculo (ley de Little y token bucket del API Gateway) · glosario.

**Actualización 2026-10-04:** la autoevaluación salió a `m2-autoevaluacion-danny.html`; gráficas generadas con
`graficas/generar_graficas.py` (stdlib). Son **modelos de cálculo con los números del enunciado**, no
mediciones; el valor por defecto del *burst* en la cuenta AWS sigue sin verificar.

**Límites:** falta el video de Seguridad; la autoevaluación oficial no se abrió. Cada afirmación lleva
etiqueta `Curso` / `Complementario` / `Recomendación` / `Hipótesis`. El `.md` es la fuente de verdad; el
`.html` se regenera con `.claude/skills/consolidar-conocimiento/consolidar_html.py`.

---

## `m2-autoevaluacion-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-10-04 |
| **Módulo** | 2 — Requerimientos y Tácticas de Arquitectura de Software |
| **Tema** | Autoevaluación interactiva de estudio: 29 preguntas en 4 niveles (recordar, comprender, aplicar, decidir) |
| **Tipo** | `apunte` — banco de preguntas propio, elaborado con IA; **no es material oficial ni la autoevaluación de Brightspace** |
| **Fuentes** | Las mismas del cuaderno de estudio · las dos gráficas de `graficas/` (modelos de cálculo) |
| **Estado** | vigente · ⬜ sin consolidar |

**Límites:** la autoevaluación oficial sigue sin abrirse; no sabemos su formato, así que estas preguntas no
pretenden imitarla. El HTML es la fuente (mismo diseño que `m1-autoevaluacion-danny.html`); las gráficas van
insertadas en línea en los `<template>` `svg-ll` y `svg-tb`: si se regeneran, hay que reemplazarlas ahí.

---

## `m2-preguntas-encuentro-0610-danny.md` (+ `.html` generado)

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) · §10–12: Freddy Aparicio (PR #30, excepción a la convención autorizada por Danny) |
| **Fecha** | 2026-10-04 · §10–12: 2026-10-09 |
| **Módulo** | 2 — Reto 2 |
| **Tema** | 9 preguntas para el profesor en el encuentro del 06/10, cada una con su fundamento y qué decisión cambia · §10 indicaciones del docente reportadas por Freddy · §11 decisión pendiente del `200 OK` · §12 guía para la exposición |
| **Tipo** | `apunte` — elaborado con IA; **no es material oficial** · §10 `apunte` (reporte de Freddy, no transcripción) · §11–12 `investigacion` |
| **Fuentes** | `Material-Clase/Actividad-Reto2.md` · cuaderno de estudio §11 · notas de Freddy del encuentro 06/10 |
| **Estado** | vigente · preguntas 1–9 sin respuesta escrita · §10.4 reporta < 16 s frente a < 15 s de la rúbrica: **contradicción abierta**, se resuelve en el consolidado |

---

## `m2-panel-v2-propuesta-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-10-07 |
| **Módulo** | 2 — Reto 2 |
| **Tema** | Maqueta estática de una v2 del panel del Reto 2 (tarea de la reunión del 06/10): qué cambia, por qué y a qué costo |
| **Tipo** | `propuesta` — elaborada con IA; **no es material oficial** ni decisión del equipo |
| **Fuentes** | Panel actual (`Ejercicios/Reto2-Alerta-Flota/panel/`), captura del 07/10 · feedback del profesor sobre M1 (hilo conductor) |
| **Estado** | vigente · para discutir el 09/10 |

**Límites:** los datos son de ejemplo (la fila 16,4 s está inspirada en el 06/10, no es un registro).
No hay código detrás: el costo de cada cambio es una estimación.

**Cambio del 11/10/2026 (Danny):** se retira la sección 6 «Inyectar fallas» y en su lugar entra la
gráfica «Peticiones por segundo · últimos 60 s» del panel actual (dibujo replicado de `pintarGrafica`
en `panel/static/app.js`, con datos de ejemplo de la corrida #3). Se ajustan la tabla «Qué cambia y por qué»
y la nota de la línea de tiempo, que ya no reemplaza esa gráfica sino que la complementa.

---

## `m2-revision-aws-opcion-b-danny.md`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-10-09 |
| **Módulo** | 2 — Reto 2 |
| **Tema** | Revisión técnica de la opción B en AWS de Camilo: bloqueantes, ajustes propuestos, pedidos a Camilo y agenda del domingo 11/10 |
| **Tipo** | `investigacion` — elaborada con IA; **no es material oficial** ni decisión del equipo |
| **Fuentes** | `../camilo/m2-aws-opcion-b-camilo/` · `Material-Clase/Actividad-Reto2.md` · `Ejercicios/Reto2-Alerta-Flota/alerta/{domain,ports}.py` |
| **Estado** | borrador · para discutir el 11/10 |

**Límites:** revisión **estática**: no se ejecutó nada contra la cuenta AWS de Camilo. Lo marcado
«✓ validado» en su diagrama se toma como reporte suyo. Los ajustes son propuestas: el aporte de Camilo
no se modificó.

---

## `m2-presentacion-reto2-danny.html` (+ `m2-presentacion-reto2-guion-danny.md`)

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny), con asistencia de IA |
| **Fecha** | 2026-10-12 |
| **Módulo** | 2 — Reto 2 |
| **Tema** | Presentación del Reto 2 (16 láminas con notas del orador) y su guion: las dos implementaciones (local en Docker y opción B en AWS), decisiones, tácticas, evidencias, riesgos y el switch Local/AWS del panel |
| **Tipo** | `investigacion` — elaborada con IA; **no es material oficial** ni versión aprobada por el equipo |
| **Fuentes** | `Material-Clase/Actividad-Reto2.md` · `Ejercicios/Reto2-Alerta-Flota/README.md` y `docs/2026-10-04-reto2-local-design.md` · `../camilo/m2-aws-opcion-b-camilo/arquitectura-aws-opcion-b.md` · `../camilo/m2-respuestas-exposicion-12.1-12.2.md` · `m2-preguntas-encuentro-0610-danny.md` §10–12 (aporte de Freddy) · `m2-revision-aws-opcion-b-danny.md` · `Material-Clase/Tacticas-Desempeno.md` y `Tacticas-Disponibilidad.md` |
| **Estado** | borrador · para revisar en equipo antes de la exposición |

**Límites:**
- Los números de AWS los reporta Camilo y nadie más los ha verificado. Los locales salen del README y de la revisión del 09/10.
- Quedan marcados como **pendiente**: el p95, la duración y la recepción → envío de la corrida local, y la llegada real a Gmail en los dos entornos.
- **Contradicción registrada, sin resolver:** el atributo priorizado. El diseño local dice desempeño y el aporte de Camilo dice disponibilidad/confiabilidad. El deck asume desempeño y lo señala en la lámina 3.
- El reparto de concurrencia en AWS (10 + 2 = 12) se presenta como **decisión abierta** frente al límite de 10, con tres opciones. No se presenta como cumplimiento.
- La lámina del panel describe el switch Local/AWS, que se estaba implementando en paralelo. Hay que revisarla cuando se mergee.
- Usa el mismo sistema visual y el mismo script de navegación que `Modulo 1/Aportes/danny/m1-presentacion-reto-latencia-v2-danny.html`. Solo depende de Google Fonts.

## `m2-respaldo-corrida7-aws/` — Logs de la corrida #7 en AWS (respaldo)

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny), exportación desde el panel |
| **Fecha** | 2026-10-14 (corrida ejecutada el 13/10, 19:45 hora Colombia, durante el encuentro) |
| **Módulo** | 2 — Reto 2 |
| **Tema** | Logs de CloudWatch de la corrida #7 contra AWS: k6 del profesor, 2 `Emergency`, 2 correos, 0 DLQ, 1,256 s según el panel |
| **Tipo** | `dato-medido` — exportado del sistema, sin editar |
| **Fuentes** | `GET /api/corridas/7/logs` del panel (lee CloudWatch Logs de `reto2-ingesta` y `reto2-notifier`) |
| **Estado** | respaldo · la corrida oficial es la #2 (`Entregables/logs/`) |

**Por qué existe:** CloudWatch tiene retención corta. Si los logs vencen, el panel ya no puede
volver a exportarlos. Se guardaron antes de que eso pase.
