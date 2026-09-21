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

## `m1-arquitectura-variante-d-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-19 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Variante D (memoria compartida): arquitectura, justificación, criterios de uso y medición. Es la documentación de la variante D asignada en ADR-007 |
| **Tipo** | `investigacion` — **documento derivado, generado con IA, validado por el autor** |
| **Fuente primaria** | Código de `variante-D-shm/` y `sistema/` + ejecución del proyecto en Linux x86-64 (WSL2) + `README` de D, ADR-001/002/003/004/005/007, `DISENO-ARQUITECTURA.md`, `ENUNCIADO.md`, `docs/archivo/control-Bc-tcp-c.md`, `docs/archivo/OPCIONES-SISTEMA.md`, `docs/archivo/variante-E-icmp.md` + `Material-Clase/` y `Temario/` del M1 |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | Creado directamente en esta carpeta |

**Qué contiene:** documentación técnica de la variante D redactada como capítulo de la entrega:
1 resumen · 2 arquitectura · 3 justificación · 4 cuándo usar memoria compartida · 5 medición y resultados.
El documento no lleva etiquetas de fuente ni anexos; el registro de origen vive en esta ficha.

**Origen de cada tipo de dato:**
- Cifras del equipo de referencia (Apple M4): tomadas del README de D y de `DISENO-ARQUITECTURA.md`; **no se recalcularon** desde los CSV.
- Cifras de 5.6: **medidas en ejecución** en Linux x86-64 sobre WSL2 (Intel i5-8300H). Corrida propia según ADR-005; no se mezcla con la tabla de referencia.
- Gráfica de percentiles (5.4): `sistema/graficas/percentiles.svg`, generada por `graficas.py` con la corrida del 17/09 (commit `8c0b035`, sin cambios locales) e **incrustada sin modificar**. Se comprobó leyendo sus puntos que coincide con las cifras del README (D: p50 ≈ 83 ns, p99.9 ≈ 167 ns, máx ≈ 37 µs; B: p50 ≈ 13,4 µs, máx ≈ 13,5 ms). Su paleta (B azul, D violeta) no coincide con el resaltado de 3.2 (B azul, D dorado), y su subtítulo cita ADR-001.
- Resumen «en una mirada» (5): 83 ns, 0 de 3 000 000 y ≈ 12 048× salen de las cifras de 5.3 y 5.4; no son datos nuevos.

**Límites que hay que conocer antes de consolidar:**
- Las barreras de memoria de arm64 **no** se pudieron corroborar en x86-64 (modelo de memoria más fuerte).
- El `Makefile` de D incluye `-D_GNU_SOURCE`, **necesario** para compilar en Linux/WSL2 (comprobado: sin él falla). Ese cambio se propone en el PR de la rama `reto/camilo-d-linux-wsl2`; el documento (2.6) asume que llega al repositorio.

### ⚠️ Contradicciones detectadas — pendientes de resolver en el consolidado

| # | El documento dice | Otro documento del proyecto dice | Estado |
|---|---|---|---|
| 1 | D no tiene afinidad de núcleo (según código y ADR-002) | `DISENO-ARQUITECTURA.md` §4.2 dibuja D con «núcleo fijado» | El código manda; corregir en el consolidado |
| 2 | Hay 4 `memcpy` de 32 B por intercambio; «0 copias» vale solo para el kernel | `DISENO-ARQUITECTURA.md` §5: «Copias de memoria: 0» | Precisar la redacción |
| 3 | ADR-002 usa `atomic_uint_fast32_t` y `CLOCK_MONOTONIC`; el código usa `_Atomic uint64_t` y `CLOCK_UPTIME_RAW` | ADR-002 (estado «Propuesta») | El código manda; ADR-003 enmienda el reloj |
| 4 | El comentario de `common.h` estima el límite de espera en «~segundos»; medido en x86-64/WSL2 son ≈ 21 s por intercambio perdido | `common.h:60-62` | Dato medido propio; conviene reportarlo al autor del código |
| 5 | El cliente D imprime la granularidad «41.67 ns» de forma fija y `reloj_verificar()` nunca se llama | ADR-003 exige verificar y reportar la granularidad real | Incumplimiento en otra plataforma; sin efecto en el equipo de referencia |
| 6 | 3.4 usa Bc p50 = 12 000 ns y B p50 = 13 209 ns (tabla agregada de `control-Bc-tcp-c.md`) | `variante-E-icmp.md` da Bc = 11,5 µs y B = 13,4 µs para las mismas mediciones | Dos agregaciones distintas del mismo día dentro de los documentos archivados; el documento usa la primera por ser la que descompone el factor |
| 7 | 3.4 apoya la descomposición lenguaje/transporte (9,2 % / 90,8 %) en el control Bc | README del reto y ADR-007: Bc se retiró del árbol y su trabajo queda como historia, «no como sustento de ninguna conclusión vigente» | Declarar en el consolidado cuál se adopta; el documento debería decir que el control ya no es reproducible desde el árbol |

---

## `m1-codigo-variante-d-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-20 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Guía del código de la variante D: qué hace cada archivo y cada bloque |
| **Tipo** | `investigacion` — **documento derivado, generado con IA** |
| **Fuente primaria** | Código de `variante-D-shm/` (`common.h`, `server.c`, `client.c`, `Makefile`) y `sistema/` (`reloj.h`, `clasificador.h`, `run.sh`) |
| **Estado** | recibido · ⬜ sin consolidar |
| **Archivo original** | Creado directamente en esta carpeta |

**Qué contiene:** visión general y flujo de una ejecución; explicación por bloques de cada archivo con sus rangos de
líneas; los tres fragmentos clave comentados (`clasificar`, ruta caliente del servidor, macro `INTERCAMBIO` y bucle
de medición); cómo se ejecuta; glosario.

**Límites:** los rangos de líneas corresponden al código a fecha 2026-09-20 (server.c 155, client.c 277, common.h 64,
clasificador.h 216, reloj.h 109, Makefile 22). Si esos archivos cambian, hay que actualizar los rangos. Se
comprobó mecánicamente que las líneas citadas contienen lo que el texto dice. El `Makefile` incluye `-D_GNU_SOURCE`
(propuesto en el PR de la rama `reto/camilo-d-linux-wsl2`).

## `m1-manual-instalacion-camilo.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón |
| **Fecha de recepción** | 2026-09-20 |
| **Módulo** | 1 — Reto de Latencia Mínima |
| **Tema** | Manual de instalación y diagnóstico del proyecto completo: interfaz web, variante B y variante D (sin mediciones) |
| **Tipo** | `investigacion` — **documento derivado, generado con IA** |
| **Fuente primaria** | `README.md` del reto, `doctor.py`, `iniciar.sh`, `iniciar.ps1`, `iniciar.cmd`, `app/servidor.py`, `sistema/run.sh` |
| **Estado** | versión inicial · ⬜ sin consolidar |
| **Archivo original** | Creado directamente en esta carpeta |

**Qué contiene:** requisitos por pieza, los tres caminos (macOS/Linux, WSL2, Windows nativo), instalación por
plataforma, arranque, puertos, verificación con `doctor` y tabla de problemas frecuentes. No trata mediciones ni
resultados.

**Probado el 20/09/2026 (simulación de instalación desde cero):**
- **WSL2 / Ubuntu:** copia limpia del proyecto sin binarios → `./iniciar.sh 8091` compiló D («variante-D-shm ok»),
  la web respondió 200, B y D arrancaron y pararon por la API, un estímulo a B devolvió veredicto, sin residuos al
  cerrar. `python3 doctor.py` dio «Todo listo» (y avisó del puerto 8080 ocupado, como debe).
- **Windows nativo (sin `make` ni compilador):** `iniciar.ps1 -Puerto 8092` levantó la web (200) y B; al arrancar D
  la interfaz devolvió el aviso con `wsl --install`. `doctor.py` dio «Podés arrancar el proyecto: iniciar.cmd».

**Corrección posterior (20/09):** una primera versión decía que el sistema no necesita internet. Es falso para la
interfaz: `app/index.html` carga React desde cdnjs y las tipografías desde Google Fonts. Se corrigió en el manual.
Comprobado leyendo el código; no se probó abrir la interfaz sin conexión.

**Límites:** el enunciado oficial no pide manuales; son un compromiso interno del equipo (README, «Para el equipo»),
y quién firma cada uno se decide el 21/09. **macOS no se pudo probar** (no hay equipo): sus pasos salen del código y del README. Solo se probó Ubuntu. Se probó con Python 3.14; el mínimo de 3.9 es el que declara el proyecto, no uno
verificado. Con la salida redirigida a un archivo en Windows (cp1252), `doctor.py` falla por los caracteres de caja;
en consola normal no se pudo comprobar aquí.
