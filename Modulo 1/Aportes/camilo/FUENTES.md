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

---

## `m1-arquitectura-memoria-compartida-c-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-23 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Memoria compartida C: arquitectura, justificación de las decisiones y criterios de cuándo usarla |
| **Tipo** | `investigacion` — **documento derivado, generado con IA, validado por el autor** |
| **Fuente primaria** | Código de `sistema/memoria-compartida-c/` (`common.h`, `server.c`, `client.c`, `Makefile`) y `sistema/` (`reloj.h`, `clasificador.h`) + ADR-002/005/006/007 (consultados para verificar, no citados en el cuerpo) |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | Creado directamente en esta carpeta |

**Qué contiene:** 1 resumen · 2 arquitectura (componentes, datos, protocolo, ciclo de vida,
portabilidad) · 3 justificación de las decisiones (trade-offs por atributo de calidad) ·
4 cuándo usar memoria compartida y cuándo no. **No incluye mediciones ni resultados** — es
arquitectura y justificación, a propósito, para no depender de una corrida concreta.

**Reemplaza a** `m1-arquitectura-variante-d-camilo.html` (PR #8, cerrada): ese documento usaba
la nomenclatura anterior al rename de ADR-008 («variante D») e incluía una sección de medición
con cifras de una corrida ya superada. Este es una reescritura completa, no una actualización.

**Decisión editorial:** no cita ADR en el cuerpo del texto (a diferencia de la versión anterior).
El equipo decidió que esas referencias son documentación interna, no parte de la entrega — mismo
criterio que se aplicó a `app/index.html` y `app/servidor.py` (PR #15).

---

## `m1-codigo-memoria-compartida-c-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-22 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Guía del código de Memoria compartida C: qué hace cada archivo y cada bloque |
| **Tipo** | `investigacion` — **documento derivado, generado con IA, validado por el autor** |
| **Fuente primaria** | Código de `sistema/memoria-compartida-c/` (`common.h`, `server.c`, `client.c`, `Makefile`) y `sistema/` (`reloj.h`, `clasificador.h`, `run.sh`) |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | Creado directamente en esta carpeta |

**Qué contiene:** visión general y tabla de archivos; explicación por bloques de cada archivo con
sus rangos de líneas; la macro `INTERCAMBIO` completa comentada; el modo de estímulo suelto
`--clasificar` (`client.c:178-215`); cómo se ejecuta; glosario.

**Reemplaza a** `m1-codigo-variante-d-camilo.html` (PR #8, cerrada). Los rangos de línea
corresponden al código a fecha 2026-09-22 (`server.c` 155, `client.c` 324, `common.h` 64,
`clasificador.h` 216, `reloj.h` 109, `Makefile` 25). Si esos archivos cambian, hay que
actualizar los rangos citados — se comprobó mecánicamente que las líneas citadas contienen lo
que el texto dice, pero eso no se revalida solo.

**No menciona** el rename de ADR-008 ni el estado anterior del código: describe únicamente el
estado actual, por pedido explícito del autor durante la revisión.

---

## `m1-manual-instalacion-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-23 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Manual de instalación del proyecto completo: interfaz web, TCP Python y Memoria compartida C |
| **Tipo** | `investigacion` — **documento derivado, generado con IA, validado por el autor** |
| **Fuente primaria** | `README.md` del reto, `doctor.py`, `iniciar.sh`, `iniciar.ps1`, `iniciar.cmd`, `app/servidor.py` |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | Creado directamente en esta carpeta |

**Qué contiene:** requisitos por pieza, los tres caminos (macOS/Linux, WSL2, Windows nativo),
instalación por plataforma, arranque, puertos, verificación con `doctor` y tabla de problemas
frecuentes. No trata mediciones ni resultados.

**Reemplaza a** `m1-manual-instalacion-camilo.html` de la PR #8 (cerrada, mismo nombre de
archivo). Actualizado contra el estado actual: nomenclatura de ADR-008 (TCP Python / Memoria
compartida C), el mensaje de compilación que ahora imprime `memoria-compartida-c ok` (y de
paso `control-dominio ok`, una herramienta aparte que también compila en el mismo paso), y el
fix de `-D_GNU_SOURCE` del Makefile (PR #14) documentado como si ya estuviera en el árbol,
porque para cuando esta PR se mergee, lo estará.

---

## `m1-manual-uso-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-22 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Manual de uso de la interfaz web: qué hace cada botón, qué significa cada número |
| **Tipo** | `investigacion` — **documento derivado, generado con IA, validado por el autor** |
| **Fuente primaria** | `app/index.html` y `app/servidor.py`, verificados en vivo (WSL2/Ubuntu: servidor arrancado, `curl` contra la API, captura de pantalla de la interfaz) |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | Creado directamente en esta carpeta |

**Qué contiene:** alcance, mapa de la interfaz, encender/apagar variantes, probar clasificación,
medir rendimiento, historial y CSV, qué es normal ver, problemas frecuentes. Es un manual para
usuario final: no remite al manual de arquitectura ni a la documentación por variante — a
pedido explícito del autor, para que sea autocontenido.

**Documento nuevo, sin equivalente en la PR #8** (esa PR nunca llegó a producir un manual de
uso). Refleja cambios que ocurrieron después de esa PR: se retiró el editor de la tabla de
hosts (ADR-009/011), se agregó el estímulo suelto `--clasificar` para Memoria compartida C, el
historial perdió la columna de veredicto, y la interfaz ya no cita ADR-001/006 (PR #15).
