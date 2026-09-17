# Módulo 1 — Fundamentos de la Arquitectura de Software

**Ventana:** 07/09/2026 → 29/09/2026 (23 días — el módulo más largo) · **15 horas estimadas**
**Encuentros sincrónicos:** martes 15/09 y martes 29/09, 6:00 pm

## Objetivos del módulo

Entender qué es la arquitectura de software, por qué importa, qué la distingue del diseño, y cómo
se expresa un requisito no funcional de forma medible. El hilo conductor: **toda decisión
arquitectónica es un trade-off, y el «por qué» importa más que el «cómo»**.

## Temas principales

Fundamentos y definición · leyes de la arquitectura · las tres dimensiones de su importancia ·
restricciones (negocio, tecnología, equipo) y decisiones · atributos de calidad: operacionales,
estructurales y transversales · ISO/IEC 25010 · rendimiento vs. escalabilidad · observabilidad ·
trade-offs.

## Estado

| Sección | Estado |
|---|---|
| Contenidos obligatorios | ✅ visitado |
| **Autoevaluación M1** (cuestionario, **1 solo intento**) | ⬜ **pendiente** |
| **Actividad M1** — Reto de Latencia Mínima | 🟡 en curso |
| Conclusiones · Recursos complementarios | ✅ visitado |
| **Consolidado del módulo** | ✅ `Consolidado/m1-consolidado.md` (15/09) — 8 contradicciones registradas |

## Material oficial

`Material-Clase/Modulo1-ArquitecturaSoftware.{md,html}` — página completa de Brightspace.
`Temario/TEMARIO-M1.md` — temario procesado, recursos y bibliografía.

> **Falta conseguir:** los 4 recursos Genially y el video de YouTube son embebidos externos y no
> quedaron descargados. Ahí vive el detalle fino: la lista exacta de las «leyes de la arquitectura»,
> la taxonomía completa de atributos y las tres dimensiones desarrolladas. **Hacer la autoevaluación
> sin esto es arriesgado: solo hay un intento.**

## Aportes

| Autor | Archivo | Tipo | Estado |
|---|---|---|---|
| **Danny** | `m1-fundamentos-arquitectura-danny.html` | apunte (con IA) | vigente |
| **Danny** | `m1-clasificador-hosts-danny.html` | apunte / guía de reunión | vigente |
| **Camilo** | `m1-cuadernillo-estudio-camilo.html` | investigación (con IA) | ✅ consolidado |
| **Camilo** | `m1-guia-reto-latencia-camilo.html` | investigación (con IA) | ✅ consolidado |
| **Freddy** | — | — | sin aportes aún |

Fichas de origen y contradicciones detectadas: `Aportes/*/FUENTES.md`.

## Retos

`Ejercicios/Reto-Latencia-Minima/` — **Reto de Latencia Mínima**. Documento maestro:
`PLAN-DE-TRABAJO.md` (30 tareas con responsable, dependencia y fecha).

Estado: variantes **B, Bc, D y E medidas** · **A** (Freddy) y **C** (Camilo) pendientes para el 21/09 ·
informe y guion de video en borrador · falta grabar.

Para entender el sistema sin leer código: abre `Aportes/danny/m1-clasificador-hosts-danny.html`
en el navegador.

## Decisiones importantes

| ADR | Tema | Estado |
|---|---|---|
| `ADR-001` | Frontera de medición (dónde empiezan y terminan las sondas) | propuesta |
| `ADR-002` | Variante D — memoria compartida: mecanismo, lenguaje, planificación | propuesta |
| `ADR-003` | Resolución del reloj — granularidad ≠ unidades | propuesta |
| `ADR-004` | Dominio del reto: listas de hosts en vez de eco puro | propuesta |
| `ADR-005` | Comparabilidad entre máquinas — no mezclar corridas de equipos distintos | propuesta |
| `ADR-006` | Concurrencia: un hilo por conexión, y por qué D no puede tenerla | propuesta |
| `ADR-007` | Reducción de alcance a las variantes B y D | propuesta |

Todas en [`Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/docs/ADR/`](Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/docs/ADR/),
que es donde viven: **un ADR viaja con el ejercicio que lo produjo.**

## Entregables

`Entregables/` — vacío. Lo que se sube a Brightspace: ZIP del código · PDF técnico · logs ·
informe con comparación explícita contra 1 ms · video ≤ 5 min o demo en vivo.
**Objetivo 27/09 · cierre 29/09.**

## Conocimiento consolidado

**⭐ `Consolidado/m1-consolidado.html`** — ábrelo en el navegador: la fusión de las 5 fuentes. Documento único de estudio
del módulo: conceptos marcados `[Curso]` / `[Complementario]` / `[Recomendación]` / `[Hipótesis]`,
**8 contradicciones registradas** (2 sin resolver por falta de material oficial), hechos vs.
opiniones vs. hipótesis, 13 posibles preguntas de evaluación y próximos pasos con responsable.

Para corregirlo se edita `m1-consolidado.md` y se regenera el HTML con
`.claude/skills/consolidar-conocimiento/consolidar_html.py`.

`Consolidado/ANALISIS-APERTURA-M1.md` — análisis de apertura del módulo.

> ⚠️ **Hallazgo del consolidado:** la taxonomía de atributos de calidad **difiere entre los aportes
> de Danny y de Camilo** (rendimiento, usabilidad, portabilidad, fiabilidad), y el material oficial
> no la desarrolla — vive en el Genially M1P5, no descargado. Con **un solo intento** en la
> autoevaluación, conseguir ese recurso es la tarea de mayor prioridad del módulo.

## Preguntas abiertas

1. ¿La entrega del reto es **una por grupo o una por persona**? El enunciado está en singular y el
   material no menciona entrega grupal. → preguntar el 15/09.
2. ¿Qué **frontera de medición** espera el docente? Decide cómo se redacta el informe entero.
3. Mediana de 13 µs con un máximo que varía entre 130 µs y 44 ms según el día: **¿cumple 1 ms?**
4. ¿Espera **red física** entre dos máquinas o acepta loopback?
5. ¿Cuál es la formulación exacta de las «leyes de la arquitectura» según el docente? (vive en los
   Genially no descargados)
