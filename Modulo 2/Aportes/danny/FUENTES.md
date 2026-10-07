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
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-10-04 |
| **Módulo** | 2 — Reto 2 |
| **Tema** | 9 preguntas para el profesor en el encuentro del 06/10, cada una con su fundamento y qué decisión cambia |
| **Tipo** | `apunte` — elaborado con IA; **no es material oficial** |
| **Fuentes** | `Material-Clase/Actividad-Reto2.md` · cuaderno de estudio §11 |
| **Estado** | vigente · respuestas pendientes (se llenan tras el encuentro) |

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
