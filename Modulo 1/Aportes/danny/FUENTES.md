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
