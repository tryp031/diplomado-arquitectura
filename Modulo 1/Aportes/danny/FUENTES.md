# Aportes de Danny — Módulo 1

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `m1-fundamentos-arquitectura-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-11 (v2 vigente) |
| **Módulo** | 1 — Fundamentos de la Arquitectura de Software |
| **Tema** | Notas de estudio del M1, ancladas al reto de latencia |
| **Tipo** | `apunte` — notas de estudio propias, elaboradas con IA |
| **Fuentes** | Material oficial M1 · Richards & Ford (bibliografía del módulo) · ISO/IEC 25010:2011 · mediciones propias del reto |
| **Estado** | vigente · ⬜ sin consolidar |
| **Origen** | Artifact `44a8f63c-ff8e-4c7f-a2c2-ca4cb0652769` |

**Qué contiene:** método de estudio en 4 pasadas · qué es la arquitectura y la prueba de
reversibilidad · las tres dimensiones · las leyes · restricciones en 3 frentes · taxonomía de
atributos · ISO/IEC 25010 con la advertencia de la revisión 2023 · tabla de trade-offs ·
el reto como ancla, con percentiles medidos · tarjetas de autoevaluación · glosario.

**Valor diferencial frente al cuadernillo de Camilo:** cada concepto abstracto está anclado a un
número medido en el reto, y marca explícitamente qué es del curso (`Curso`), qué es
complementario (`Complementario`) y qué es recomendación propia (`Recomendación`).

---

## `m1-fundamentos-arquitectura-danny-v1-superada.html`

Versión del 08/09 del documento anterior. **Superada** — se conserva solo por trazabilidad.
No usar para estudiar.

---

## `m1-clasificador-hosts-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-14 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Qué construimos, cómo funciona y dónde encaja en el reto |
| **Tipo** | `apunte` / material de reunión de equipo |
| **Fuentes** | Enunciado de la Actividad M1 · mediciones propias (9,15 M de muestras) · `ESPEC-MEDICION.md` · `PLAN-DE-TRABAJO.md` |
| **Estado** | vigente · es el documento base de la reunión del 15/09 |
| **Origen** | Artifact `d558fee7-5645-4565-ab2c-6ce362a18e5a` |

**Qué contiene:** por qué las listas blancas/negras no resuelven la latencia (y por qué aun así
van) · el sistema visto en un intercambio completo · la tabla que cabe en una línea de caché ·
comparación de las 5 variantes por capas atravesadas · plano de control vs. plano de datos ·
formas de medir descartadas y por qué · cobertura del reto punto por punto · tablero de la reunión
con decisiones, preguntas al docente y trabajo de la semana.

> **Este es el documento para compartir con Freddy y Camilo.** Explica el sistema sin asumir que
> ya conocen el harness, y contiene el reparto de tareas con fechas.

---

## `m1-presentacion-reto-latencia-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-16 |
| **Módulo** | 1 — Fundamentos de la Arquitectura de Software |
| **Tema** | Draft de presentación del Reto de Latencia Mínima |
| **Tipo** | `borrador` — presentación en elaboración, no aprobada por el equipo |
| **Fuentes** | `INFORME.md` · `GUION-VIDEO.md` · `docs/archivo/control-Bc-tcp-c.md` · ADR-001, 004 y 007 · mediciones propias del reto |
| **Estado** | **DRAFT** · ⬜ sin revisar por Freddy ni Camilo · pendiente de la reunión del 21/09 |
| **Origen** | Elaborado con Claude Code sobre el material del repositorio. Ninguna cifra es inventada: todas salen del informe o de `analyze.py` |

**Qué contiene:** 13 láminas de presentación + 1 lámina interna de control. El arco es
anticlímax (el objetivo ya estaba cumplido) → reformulación de la pregunta → diseño del
experimento → la frontera de medición F1 → el dominio → cuatro resultados → trade-offs →
cierre. Notas del orador en cada lámina, con tiempos.

**Cómo se usa:** se abre en cualquier navegador, sin servidor. `←/→` o espacio para navegar,
`N` muestra las notas del orador, `T` alterna claro/oscuro. Imprimir a PDF da una lámina por
página con las notas incluidas.

**Decisiones abiertas que afectan al contenido** (lámina 14, no se presenta):

- Si se usan o no las cifras archivadas de `Bc` — de ellas depende el titular del 9 % / 91 %.
- Qué corrida es la oficial, la del 10/09 o la del 14/09: cambia la tabla de la lámina 8.
- Duración: hoy suma ~7 min y el video son 5 como máximo.

**Advertencia de trazabilidad:** la lámina 7 usa datos de un experimento cuyo código ya no
está en el árbol (ADR-007). Está marcado como «archivada» en la propia lámina y explicado en
las notas del orador. **No presentarlo como reproducible en vivo.**

---

## `m1-presentacion-reto-latencia-v2-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-28 (revisada el mismo día con las notas de Danny) |
| **Módulo** | 1 — Fundamentos de la Arquitectura de Software |
| **Tema** | Versión 2 de la presentación del Reto de Latencia Mínima |
| **Tipo** | `entregable` — presentación de la sustentación del 29/09 |
| **Fuentes** | `m1-presentacion-reto-latencia-danny.html` (estilos, portada y lámina del reto) · diagramas de Danny del 28/09 · trade-offs redactados por Danny · ejecución propia del 28/09, ronda 4 (`sistema/resultados/*-4.csv` + `.log`) · `resultados/LEEME.md` (14/09, 17/09 y 24/09) · código y ZIP entregable revisados el 28/09 (`hacer-zip.sh`) |
| **Estado** | `vigente` · **versión oficial** por decisión de Danny del 28/09 · sin revisión registrada de Freddy ni Camilo |
| **Origen** | Elaborado con Claude Code. Los cuatro diagramas se redibujaron como SVG a partir de las imágenes de Danny; en el de medición se quitó el paso «clasifica el host». Las cifras salen de `analyze.py` sobre la ronda 4. Se midió en la ronda 4 y no en la 1 para no archivar la oficial del 24/09 ni mezclar días en las rondas 1-3 |

**Qué contiene:** 9 láminas: portada · la solución que entregamos · arquitectura · dos
caminos para el mismo mensaje · dónde para el cronómetro · demostración · resultados ·
atributos de calidad · ¿bajamos del milisegundo? No trae apéndice: la gráfica de percentiles, el C4 y los límites del
experimento siguen en el draft v1.

**Contradicción registrada:** la cifra principal de la v2 es la de la **ejecución del 28/09**
(1 × 1 M). El informe y el draft v1 usan la del **24/09** (3 × 1 M), que es la oficial. No se
contradicen en el veredicto por mediana, pero sí en las cifras: 15,3 µs frente a 14,9 µs de p50
en TCP Python, y 0 frente a 164 muestras sobre 1 ms. La v2 muestra junto a la del 28/09 solo la
oficial del 24/09 (decisión de Danny del 28/09: se retiraron el 14/09 y el 17/09 de la lámina). Queda por decidir en equipo cuál se cita en la sustentación.

**Cambio de término:** la lámina de atributos usa «flexibilidad» en lugar de «portabilidad»,
siguiendo ISO/IEC 25010:2023 (conocimiento complementario, no material del diplomado).

---

## `m1-autoevaluacion-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-21 |
| **Módulo** | 1 — Fundamentos de la Arquitectura de Software |
| **Tema** | Las 10 preguntas de la autoevaluación M1, resueltas y analizadas |
| **Tipo** | `apunte` — notas de estudio propias, elaboradas con IA |
| **Fuentes** | **Autoevaluación oficial del M1** (Brightspace, 10 preguntas — enunciados y opciones transcritos) · Richards & Ford (bibliografía del módulo) · conocimiento complementario marcado como tal en el propio documento |
| **Estado** | vigente · ⬜ sin consolidar |
| **Origen** | `M1-arquitectura-software-autoevaluacion.md`, redactado por Danny con Claude tras presentar la autoevaluación el 21/09/2026. El `.md` no se versiona: este HTML lo reemplaza |

**Qué contiene:** marco conceptual en 4 pilares (qué es una decisión significativa · la arquitectura
como abstracción · las dos leyes · tabla de atributos de calidad) · las 10 preguntas en formato
interactivo (se responden antes de ver el análisis) · para cada una: por qué la correcta es correcta,
**por qué falla cada distractora** y el concepto clave · clave de respuestas plegada · 5 patrones para
resolver preguntas de este tipo · 6 prompts para seguir estudiando · resumen de 6 puntos.

**Cómo se usa:** se abre en cualquier navegador, sin servidor. Clic en una opción la califica y abre
el análisis. `T` alterna claro/oscuro, `R` reinicia el cuestionario, «Abrir análisis» despliega todo
(útil antes de imprimir a PDF). El marcador del margen lleva la cuenta de aciertos.

**Trazabilidad del contenido:** los enunciados y las cuatro opciones de cada pregunta son del material
oficial. Todo lo demás es elaboración propia. Lo que no sale del diplomado va marcado
`Complementario` dentro del documento (patrón Saga, fecha y maniobra inversa de la Ley de Conway,
WCAG) y las observaciones propias van marcadas `Criterio` — incluye un reparo al enunciado de las
preguntas 9 y 1.

## `m1-guion-sustentacion-y-preguntas-danny.md` + `.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny) |
| **Fecha** | 2026-09-29 |
| **Módulo** | 1 — Fundamentos de la Arquitectura de Software |
| **Tema** | Guion de la sustentación del Reto de Latencia Mínima + 20 preguntas probables del docente |
| **Tipo** | `investigacion` — elaborado con IA a partir del deck v2 y del informe |
| **Fuentes** | `m1-presentacion-reto-latencia-v2-danny.html` (cifras ronda 4, 28/09) · `INFORME.md` (24/09) · `ESPEC-MEDICION.md` · ADR-001, 003, 012 · conocimiento complementario marcado como tal |
| **Estado** | vigente · ⬜ sin consolidar |

**Qué contiene:** tres advertencias previas (dos juegos de cifras, warmup retirado, frases prohibidas) ·
guion lámina por lámina con tiempos · 20 preguntas con respuesta (percentiles, resultados, metodología, diseño).

**Versión HTML:** mismo contenido que el `.md`, pensado para estudiar. Las respuestas vienen plegadas, se
puede filtrar por tema (percentiles · resultados · metodología · diseño) y con `T` se cambia entre tema
claro y oscuro. Si cambia una cifra, se actualizan los dos archivos.
