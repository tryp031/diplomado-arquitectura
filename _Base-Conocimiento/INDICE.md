# Índice maestro y estado del diplomado

> Actualizado: 2026-09-15

## Estado por módulo

| Módulo | Título | Material | Estudio | Salida procesada |
|---|---|---|---|---|
| 0 | Inducción / Aula Virtual | ✅ completo | ✅ analizado | `Modulo 0/Consolidado/RESUMEN-MODULO-0.md` |
| 1 | **Fundamentos de la Arquitectura de Software** | 🟡 parcial (faltan Genially + video) | 🟡 en curso | **`Modulo 1/Consolidado/m1-consolidado.md`**, `Modulo 1/Temario/TEMARIO-M1.md`, `Modulo 1/Consolidado/ANALISIS-APERTURA-M1.md` |
| 2 | *(pendiente de publicar)* | ⬜ | ⬜ | — |
| 3 | *(pendiente)* | ⬜ | ⬜ | — |
| 4 | *(pendiente)* | ⬜ | ⬜ | — |
| Final | *(por confirmar si existe)* | ⬜ | ⬜ | — |

## Entregas pendientes

| Entrega | Módulo | Límite | Estado |
|---|---|---|---|
| Autoevaluación M1 (cuestionario, **1 solo intento**, tiempo ilimitado) | 1 | 29/09/2026 | ⬜ |
| Actividad M1 — Reto de Latencia Mínima (ZIP + PDF + logs + informe + video/demo) | 1 | 29/09/2026 | 🟡 2 de 4 variantes medidas · diseño y ADR hechos · falta informe y video |
| Encuesta de valoración del programa (requisito de certificación) | — | fin del diplomado | ⬜ |

## Material disponible

### Módulo 0 — Inducción
4 páginas HTML (acerca del módulo, cronograma, equipo, foro de bienvenida) + PDF de lineamientos (10 artículos).

### Módulo 1 — Fundamentos de la Arquitectura de Software
Página completa de Brightspace en `.md` y `.html`. **Faltan** los 4 Genially y el video de YouTube (embebidos externos).

## Reestructuración a base colaborativa — 15/09/2026

El proyecto pasó de individual a **base compartida de Group 2**. Cambios:

| Cambio | Detalle |
|---|---|
| `README.md` y `CONTRIBUIR.md` en la raíz | Puerta de entrada y convenciones para el equipo |
| `Modulo N/Aportes/<autor>/` | Trabajo individual firmado, con ficha en `FUENTES.md` |
| `Resumen/` → `Consolidado/` | El nombre ahora dice lo que es: fusión de varias fuentes, no resumen de una |
| `Modulo N/Entregables/` | Lo que se sube a Brightspace, separado del trabajo en curso |
| `Modulo N/README.md` | Puerta de entrada por módulo |
| `_Plantillas/` | Aporte · consolidado · entregable |
| `_Base-Conocimiento/Aprendizajes/` | Lo transversal que sale de cada módulo cerrado |
| `.claude/skills/consolidar-conocimiento/` | Primera skill compartida |
| `.gitignore` | Listo para cuando se decida el medio. Excluye ~220 MB de CSV crudos |

**Aportes recibidos el 15/09:** 2 documentos de Camilo (cuadernillo M1 y guía del reto), ambos
generados con IA a partir del material oficial → clasificados como `investigacion`, no como material
oficial. 4 contradicciones detectadas contra lo ya medido, registradas en
`Modulo 1/Aportes/camilo/FUENTES.md` y pendientes de resolver en el consolidado.

**Aportes de Danny normalizados:** los dos artifacts (notas de estudio M1 y guía del clasificador de
hosts) bajaron a `Modulo 1/Aportes/danny/` como HTML. Se eliminó un duplicado exacto que vivía en
`Consolidado/`.

---

## Artefactos transversales

- `CRONOGRAMA.md` — fechas y análisis de riesgos del calendario.
- `MAPA-CONCEPTUAL.md` — grafo acumulativo de conceptos.
- `GLOSARIO.md` — términos con definición contextual.
- `ADR/` — **solo la plantilla y las decisiones transversales al diplomado.**
  Los ADR de un ejercicio viven con el ejercicio: no se duplican aquí.
  - `ADR-000-plantilla.md` — la plantilla. Se copia, no se edita.
  - `LEEME.md` — qué ADR va dónde.

  Los siete del Reto de Latencia Mínima (M1) están en
  `Modulo 1/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/docs/ADR/`:
  - `ADR-001` frontera de medición (F1) · `ADR-002` variante D, memoria compartida
  - `ADR-003` resolución del reloj · `ADR-004` dominio, listas de hosts
  - `ADR-005` comparabilidad entre máquinas · `ADR-006` concurrencia y hilos
  - `ADR-007` reducción de alcance a B y D

## Preguntas abiertas del diplomado

1. ¿Cuáles son los títulos y temarios de los módulos 2–4? *(no publicados)*
2. ¿Existe proyecto final y cuál es su alcance? *(no confirmado en el material)*
3. ¿Qué peso tiene cada evidencia en la calificación? *(no declarado)*
4. Nube de referencia: los complementarios del M1 son **casi todos AWS** → hipótesis confirmada parcialmente.
5. ⚠️ **¿Cuál es la taxonomía de atributos de calidad según el docente?** Los aportes de Danny y
   Camilo la clasifican distinto (rendimiento, usabilidad, portabilidad, fiabilidad) y el material
   oficial no la desarrolla: vive en el Genially M1P5, no descargado. **Bloquea la autoevaluación,
   que tiene un solo intento.** Detalle en `Modulo 1/Consolidado/m1-consolidado.md` §4 C1.
6. ¿Cuál es la formulación exacta de las «leyes de la arquitectura»? Misma causa (Genially 2).

---

## Próximos pasos — última sesión: 10/09/2026

### Hecho el 10/09

- `Modulo 1/Ejercicios/Reto-Latencia-Minima/DISENO-ARQUITECTURA.md` — drivers, atributos de
  calidad con escenarios medibles, restricciones, trade-offs de transporte, trazabilidad.
- **ADR-001** (frontera de medición F1), **ADR-002** (variante D), **ADR-003** (reloj).
- **Variante D implementada en C11 y medida**: 3 rondas × 1 000 000. p50 83 ns · p99.9 167 ns ·
  máx 34,8 µs · integridad 3 000 000/3 000 000. **Ninguna muestra supera 1 ms.**
- Harness adaptado a variantes compiladas (`run.sh` compila si hay `Makefile`).
- Borradores de comunicación listos para enviar en `.../Reto-Latencia-Minima/comunicaciones/`.

### También hecho el 10/09 (segunda tanda)

- **Control Bc** (TCP en C) + B re-medida a 1 M: cierra el sesgo lenguaje/transporte.
  Lenguaje 1,1× (9,2 %) · transporte 144,6× (90,8 %).
- `harness/graficas.py` — figuras SVG del informe, **sin dependencias externas**
  (`graficas/percentiles.svg`, `graficas/histograma.svg`).
- **`INFORME.md`** — entregables 2 y 4 fusionados. Borrador completo con tres puntos medidos;
  secciones marcadas ⬜ esperan A y C.
- **`GUION-VIDEO.md`** — entregable 5: guion cronometrado de 4:40 + guion de demo en vivo con
  las preguntas previsibles y sus respuestas.
- **`comunicaciones/GRUPO-WHATSAPP.md`** — kit del grupo listo para copiar y pegar.

### ⭐ Documento maestro del reto

**`Modulo 1/Ejercicios/Reto-Latencia-Minima/PLAN-DE-TRABAJO.md`** — 30 tareas derivadas del
enunciado, con responsable, dependencia y fecha; ruta crítica; contingencias; reglas de equipo.
Si algo no está ahí, no está planificado.

### Pendiente — requiere acción de Danny

1. **Enviar** `comunicaciones/MENSAJE-EQUIPO.md` a Group 2 (respuesta pedida para el 11/09).
2. **Enviar** `comunicaciones/EMAIL-FACILITADORA.md` — ¿entrega grupal o individual?
3. Congelar `ESPEC-MEDICION.md` con las enmiendas de ADR-001 y ADR-003 · asignar A y C ·
   definir máquina final y repo Git.
4. Conseguir los 4 Genially y el video del aula (faltan las leyes exactas y la taxonomía completa).
5. Autoevaluación M1 — **un solo intento**, hacerla después del punto 4.
6. Opcional, si hay tiempo: variante B en C, para separar el efecto del lenguaje del transporte.

### Hallazgos técnicos que van al informe

- **La variante B incumple el objetivo en el máximo** (2,2 ms > 1 ms) aunque su mediana sea
  13 µs. La D no lo supera nunca. La diferencia entre cumplir y no cumplir está en la cola.
- **`CLOCK_MONOTONIC` avanza a saltos de 1 µs en macOS** (medido). El reloj que la ESPEC
  exigía no podía medir la variante D. Piso físico de la máquina: 41,67 ns (contador 24 MHz).
- **macOS/arm64 no permite fijar hilos a núcleos**: `thread_policy_set` devuelve
  `KERN_NOT_SUPPORTED` (verificado). El sistema operativo es una restricción arquitectónica.

**Notas de estudio del M1 (artifact):** https://claude.ai/code/artifact/44a8f63c-ff8e-4c7f-a2c2-ca4cb0652769

### Fechas que gobiernan

- **15/09 18:00** — encuentro sincrónico. Llevar resultados de B y D; preguntar al docente por
  la frontera de medición esperada y por el alcance grupal.
- **27/09** — entrega objetivo · **29/09** — cierre del módulo, después no se califica.
