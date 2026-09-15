# Aportes de Camilo — Módulo 1

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `m1-cuadernillo-estudio-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-15 |
| **Módulo** | 1 — Fundamentos de la Arquitectura de Software |
| **Tema** | Cuadernillo de estudio completo del M1 |
| **Tipo** | `investigacion` — **documento derivado, generado con IA** |
| **Fuente primaria** | Material oficial del M1 en Brightspace |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | `~/Downloads/Diplomado_Arquitectura_Software_Cloud_Computing_Cuadernillo_Modulo_I.html` (no se modifica) |

**Qué contiene:** 14 secciones plegables — fundamentos, leyes y alcance, estilos y patrones,
responsabilidades del arquitecto, restricciones y decisiones, atributos de calidad, ISO/IEC 25010,
trade-offs, ejercicios con respuesta oculta y casos prácticos.

**Por qué NO va en `Material-Clase/`:** no es fuente primaria. Es una reelaboración del material
oficial. Si mañana afirma algo que el material de Brightspace no dice, hay que poder distinguirlo.

---

## `m1-guia-reto-latencia-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-15 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Guía de diseño y entrega del reto |
| **Tipo** | `investigacion` — **documento derivado, generado con IA** |
| **Fuente primaria** | Enunciado de la Actividad M1 + material del M1 |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | `~/Downloads/Reto_Latencia_Minima_Guia.html` (no se modifica) |

**Qué contiene:** 11 secciones — lectura del reto, mapa reto↔Módulo I, restricciones vs. decisiones,
estrategia en escalera, la medición como entregable real, optimizaciones por impacto, elección de
lenguaje, estructura de entregables y plan de trabajo.

### ⚠️ Contradicciones detectadas — pendientes de resolver en el consolidado

| # | El documento de Camilo dice | Lo que ya está decidido y medido | Estado |
|---|---|---|---|
| 1 | «Un socket TCP crudo en loopback entrega 30–60 µs» | Medido: **p50 = 13,4 µs** en Python, **11,5 µs** en C (3 rondas × 1 M) | La estimación es conservadora; nuestro dato manda |
| 2 | «Un socket de dominio Unix baja a 10 µs» | Variante C **aún no implementada** (asignada a Camilo) | Sin verificar — es justamente lo que él debe medir |
| 3 | Propone una estrategia «en escalera» de niveles | Ya existe `ESPEC-MEDICION.md` + `PLAN-DE-TRABAJO.md` con 5 variantes y contrato de harness | Convergen, pero la nomenclatura difiere → unificar |
| 4 | Sugiere una estructura de entregables propia | Ya existe la estructura del ZIP `reto-latencia-group2/` | Decidir cuál se usa; no pueden coexistir |

> Estas contradicciones **no se borran**: se resuelven en `Consolidado/` dejando registro de cuál
> se eligió y por qué. Es la diferencia entre consolidar y sobrescribir.
