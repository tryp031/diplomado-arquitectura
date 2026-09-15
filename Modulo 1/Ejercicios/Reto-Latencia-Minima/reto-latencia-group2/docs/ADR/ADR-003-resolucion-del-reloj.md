# ADR-003 — Resolución del reloj: enmienda a ESPEC §2

**Estado:** Propuesta *(enmienda a `ESPEC-MEDICION.md` §2; requiere acuerdo del equipo antes de congelar)*
**Fecha:** 2026-09-10
**Decisores:** Daniel Mazo Serna — propuesta para Group 2
**Contexto del módulo / ejercicio:** Módulo 1 · Actividad M1 · afecta a **las cuatro variantes**

## Contexto

`ESPEC-MEDICION.md` §2 fija el reloj de medición así:

> **Reloj** — Monótono, resolución de ns. `clock_gettime(CLOCK_MONOTONIC)` · `steady_clock` ·
> `System.nanoTime()` · `time.perf_counter_ns()`. **Nunca** reloj de pared.

La intención es correcta —descartar el reloj de pared, que salta con NTP— pero contiene un
error de hecho: **«resolución de ns» describe las unidades del valor devuelto, no la
granularidad con que avanza.** Son cosas distintas, y la especificación las confunde.

Medición empírica en el equipo de referencia (Apple M4, macOS 26.6.2, arm64), 200 000 pares
de lecturas consecutivas por reloj:

| Reloj | Granularidad real | % de deltas consecutivos que dan 0 |
|---|---|---|
| `clock_gettime(CLOCK_MONOTONIC)` | **1000 ns** | **97,6 %** |
| `clock_gettime(CLOCK_MONOTONIC_RAW)` | 41 ns | 40,1 % |
| `clock_gettime_nsec_np(CLOCK_UPTIME_RAW)` | 41 ns | 57,0 % |
| Contador de hardware (`mach_absolute_time`) | **41,67 ns** | 82,9 % |

El contador de hardware corre a 24 MHz (*timebase* 125/3): **41,67 ns es el piso físico de la
máquina.** Ningún reloj de este equipo puede hacerlo mejor.

El reloj que la especificación nombra en primer lugar avanza a saltos de **1 µs**. La variante
D mide del orden de **70 ns**. La primera corrida devolvió ceros en casi todas las muestras: no
era un fallo del código, era que el instrumento no alcanzaba.

## Problema

¿Qué reloj deben usar las variantes, dado que el nombrado por la especificación tiene una
granularidad diez veces mayor que el fenómeno que la variante más rápida pretende medir?

## Opciones consideradas

### Opción A — Mantener `CLOCK_MONOTONIC` en las cuatro variantes
- **Ventajas:** uniformidad literal; nadie discute la especificación.
- **Desventajas:** la variante D produciría mayoritariamente ceros. Uniformidad sobre datos
  inválidos no es comparabilidad: es una comparación de la que un término no existe.

### Opción B — Cada variante elige el reloj que le convenga
- **Ventajas:** cada una mide lo mejor que puede.
- **Desventajas:** rompe AC-3. Relojes con sobrecostes distintos introducen un sesgo
  sistemático distinto en cada variante, y el estudio deja de ser comparable.

### Opción C — El reloj de máxima resolución disponible en la plataforma, igual para todas, con su sobrecoste medido y reportado
- **Ventajas:** cumple la intención real de la especificación (monótono y lo bastante fino);
  mismo instrumento para las cuatro; el sesgo se cuantifica en vez de ignorarse.
- **Desventajas:** el nombre concreto del reloj cambia por sistema operativo. Obliga a medir y
  publicar el sobrecoste, que es trabajo extra.

### Opción D — Medir solo por lotes (N intercambios entre un par de lecturas, dividir)
- **Ventajas:** precisión por debajo del tic sin depender de la granularidad.
- **Desventajas:** **destruye la distribución.** Una media por lote no tiene p99.9 ni máximo, y
  la cola es justo lo que el estudio quiere mostrar (AC-2). Inaceptable como método principal.

## Decisión

Se elige **C**, con esta redacción para sustituir la fila «Reloj» de ESPEC §2:

> **Reloj** — Monótono y de **máxima resolución disponible en la plataforma**. Antes de medir,
> cada variante **verifica y reporta la granularidad real** del reloj que usa (menor delta no
> nulo entre dos lecturas consecutivas) y el **sobrecoste** del par de lecturas.
> **La granularidad debe ser al menos 10× menor que el p50 esperado.** Si no lo es, la variante
> añade un **contraste por lotes** como medida secundaria, nunca como sustituto de los
> percentiles.
> Relojes recomendados: macOS `clock_gettime_nsec_np(CLOCK_UPTIME_RAW)` · Linux
> `clock_gettime(CLOCK_MONOTONIC)` · Java `System.nanoTime()` · Python `time.perf_counter_ns()`.
> **Nunca** reloj de pared.

Se añade a **ESPEC §3 (métricas obligatorias)**: toda tabla de resultados incluye la
**granularidad del reloj** y el **sobrecoste del instrumento** junto a los percentiles.

**Aplicación por variante:**

| Variante | p50 esperado | Reloj | ¿Granularidad 10× menor? | Contraste por lotes |
|---|---|---|---|---|
| A · HTTP | ~100 µs | `perf_counter_ns` | ✅ sobra | no hace falta |
| B · TCP | ~13 µs | `perf_counter_ns` | ✅ (41,67 ns ≪ 13 µs) | no hace falta |
| C · IPC | ~10–30 µs | `perf_counter_ns` | ✅ | no hace falta |
| D · shm | **~70 ns** | `CLOCK_UPTIME_RAW` | ❌ **41,67 ns vs 70 ns** | **obligatorio** |

En Python, `time.perf_counter_ns()` ya usa el contador de hardware en macOS: las variantes A,
B y C **no cambian**. La enmienda solo afecta en la práctica a la D, pero la regla tiene que
estar escrita para las cuatro, porque es la regla la que estaba mal, no la variante.

## Justificación

1. **La especificación confundía unidades con granularidad.** Un reloj que devuelve
   nanosegundos pero avanza cada microsegundo no tiene «resolución de ns». La enmienda hace
   verificable lo que antes era una suposición.
2. **AC-3 se preserva mejor con C que con A.** Comparabilidad significa que las cuatro midan
   el mismo fenómeno con error conocido, no que invoquen la misma función. Con A, la variante
   D no mide nada.
3. **El criterio 10× es convencional y explicable** *(conocimiento complementario, no del
   diplomado)*: por debajo de esa relación, el error de cuantización deja de ser despreciable
   frente a la magnitud medida.
4. **D como método secundario, nunca principal.** Se conserva la distribución completa, que es
   el objeto del estudio, y el lote sirve de verificación cruzada: si media por lotes y p50 por
   muestra divergen mucho, una de las dos mediciones está mal.

## Ventajas

- Hace explícito el límite del instrumento en vez de esconderlo en el resultado.
- La discrepancia entre lotes y muestras se vuelve una comprobación de sanidad gratuita: en la
  variante D dio 61 ns (lotes) contra 70,6 ns de media por muestra, y esos ~9 ns de diferencia
  **son** el coste del par de lecturas del reloj. El instrumento queda cuantificado.
- No obliga a tocar A, B ni C.

## Desventajas

- El nombre del reloj deja de ser el mismo en todas las plataformas: hay que documentarlo por
  variante en vez de una sola vez.
- Añade dos cifras obligatorias a cada tabla de resultados.
- La variante D carga con dos métodos de medición y la explicación de por qué.

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| El docente lo lea como «cambiaron las reglas para que saliera bien» | Media | Medio | Se reporta el número **peor** (p50 = 83 ns cuantizado) como principal, y el mejor (61 ns por lotes) solo como contraste. El ADR documenta el porqué antes del resultado |
| Alguien use el contraste por lotes como métrica principal | Media | **Alto** — perdería la cola | Escrito en la enmienda: secundaria, nunca sustituto |
| Otra variante la implemente en otra plataforma con otro reloj y no lo reporte | Media | Medio | La granularidad pasa a ser un campo obligatorio del informe (ESPEC §3) |

## Consecuencias

**Queda habilitado**
- Que la variante D produzca datos válidos, y con ello que el estudio tenga sus cuatro puntos.
- Reportar el error de cuantización como parte del resultado, no como una nota al pie.

**Queda bloqueado**
- Afirmar la latencia de D con precisión mejor que ~42 ns por muestra. **Es un límite del
  hardware de esta máquina, no del código**, y así hay que escribirlo.

**Deuda aceptada**
- No se instrumenta con contadores de rendimiento de la CPU (PMU), que darían resolución de
  ciclo. Requiere privilegios y herramientas específicas; fuera del alcance y del tiempo.

**Revisar si**
- La ronda final se corre en otra máquina → volver a medir la granularidad allí. **La tabla de
  relojes de este ADR es válida para el M4, no universalmente.**
- Alguna otra variante baja de ~500 ns → le aplica la misma regla del 10×.
