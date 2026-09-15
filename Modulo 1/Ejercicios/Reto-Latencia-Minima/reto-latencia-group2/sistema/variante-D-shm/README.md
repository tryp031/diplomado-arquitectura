# Variante D — memoria compartida + espera activa

**Responsable:** Daniel Mazo Serna · **Estado:** implementada y medida (3 rondas) · 2026-09-10
**Decisiones de diseño:** [`ADR-002`](../../../../../_Base-Conocimiento/ADR/ADR-002-variante-D-memoria-compartida.md)
**Frontera de medición:** [`ADR-001`](../../../../../_Base-Conocimiento/ADR/ADR-001-frontera-de-medicion.md) (F1, idéntica a las demás variantes)

Función en el estudio: marcar el extremo inferior. No es «la mejor arquitectura» —
es el límite físico, y sirve para cuantificar qué hay que sacrificar para llegar ahí.

---

## Uso

```bash
make                                  # compila server y client
../run.sh D 1                         # ronda 1 completa (1 M iteraciones)
../run.sh D 1 --iters 100000          # corrida corta de prueba
```

`run.sh` compila antes de medir, así que nunca se mide un binario obsoleto.

## Cómo funciona

Dos procesos comparten 256 bytes de memoria física (`shm_open` + `mmap`). No hay sockets,
no hay kernel en la ruta caliente, no hay planificador.

```text
   CLIENTE                          región compartida (256 B)          SERVIDOR
   ───────                          ─────────────────────────          ────────
                          ┌──── línea de caché 0 (128 B) ────┐
   t0 = reloj             │  seq_peticion │ payload 32 B     │      gira leyendo
   memcpy payload  ──────▶│               │                  │◀──── seq_peticion
   store(seq, release) ──▶│               │                  │      (acquire)
                          └──────────────────────────────────┘
                          ┌──── línea de caché 1 (128 B) ────┐
   gira leyendo ─────────▶│  seq_respuesta│ payload 32 B     │◀───── memcpy respuesta
   seq_respuesta (acquire)│               │                  │◀───── store(seq, release)
   memcpy a buffer local  └──────────────────────────────────┘
   t1 = reloj
```

Tres decisiones que **no** son microoptimización, sino corrección o diferencia de un orden
de magnitud:

1. **Cada sentido en su propia línea de caché (128 B en Apple Silicon).** Si compartieran
   línea, cada escritura de un proceso invalidaría la caché del otro (*false sharing*).
2. **`_Atomic` con `acquire`/`release`, nunca `volatile`.** `arm64` tiene modelo de memoria
   débilmente ordenado: sin barreras, el otro núcleo puede ver la bandera actualizada antes
   que el payload. El mismo código con `volatile` funcionaría en x86 y estaría **roto** aquí.
3. **Espera activa sin ceder el núcleo.** Ceder significa volver al planificador, que es
   justamente el coste que esta variante existe para eliminar. El precio: dos núcleos al
   100 % de forma permanente.

**Lo que NO tiene, a propósito:** ring buffer. Con una sola petición en vuelo (ESPEC §2)
añadiría índices y aritmética modular sin reducir latencia. Sería sobreingeniería.

---

## El problema que apareció al medir: el instrumento no alcanzaba

La primera corrida devolvió **ceros**. No era un fallo del código.

Granularidad real de cada reloj, medida en este equipo (Apple M4 / macOS 26.6):

| Reloj | Granularidad | ¿Sirve? |
|---|---|---|
| `CLOCK_MONOTONIC` ← **el que exige ESPEC §2** | **1000 ns** | ❌ 97,6 % de los deltas dan cero |
| `CLOCK_MONOTONIC_RAW` | 41 ns | ✅ |
| `CLOCK_UPTIME_RAW` | 41 ns | ✅ menor sobrecoste — **el elegido** |
| Contador de hardware (timebase 125/3) | **41,67 ns** | piso físico de la máquina |

La especificación del equipo obligaba a un reloj **diez veces más grueso que el fenómeno**.
Enmienda propuesta en [`ADR-003`](../../../../../_Base-Conocimiento/ADR/ADR-003-resolucion-del-reloj.md).

**Consecuencia que hay que reportar siempre:** las muestras individuales están **cuantizadas
en múltiplos de 41,67 ns**. No es ruido, es el tamaño del tic.

---

## Resultados — 3 rondas × 1 000 000 de iteraciones, payload 32 B

Todas las cifras en **nanosegundos**. Integridad: 3 000 000 / 3 000 000 respuestas correctas.

| Ronda | mín | p50 | p90 | p99 | p99.9 | p99.99 | **máx** | media |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 83 | 84 | 125 | 167 | 292 | 34 833 | 70,6 |
| 2 | 0 | 83 | 84 | 125 | 166 | 2 083 | 22 625 | 65,2 |
| 3 | 0 | 83 | 84 | 125 | 167 | 291 | 17 625 | 74,4 |

**Contraste por lotes** (1000 intercambios cronometrados de una vez, 200 rondas): mediana de
**61 / 61 / 68 ns** por intercambio.

### Cómo leer estos números

La distribución **no es una campana: son escalones de un tic** (ronda 1):

| Valor | Tics | Muestras | % |
|---|---|---|---|
| 0 ns | 0 | 100 | 0,01 % |
| 41,7 ns | 1 | 329 034 | **32,90 %** |
| 83,3 ns | 2 | 658 889 | **65,89 %** |
| 125,0 ns | 3 | 10 054 | 1,01 % |
| 166,7 ns | 4 | 1 417 | 0,14 % |
| > 291 ns | > 7 | 83 | 0,01 % |

El 98,8 % de las muestras caen en dos cubos. La latencia real está **entre 1 y 2 tics**, y el
contraste por lotes la sitúa en **~61–68 ns**. El p50 reportado de 83 ns es el tic superior:
**sobreestima en unos 20 ns por cuantización, no porque el sistema sea más lento.**

> Esto es lo que justifica reportar las dos medidas. Con una sola, o se pierde la cola
> (lotes) o se exagera la mediana (muestras). Ninguna de las dos es «la verdadera».

**El observador pesa el 15 %.** Media por muestra 70,6 ns vs. media por lotes 61 ns: los dos
`clock_gettime` de cada iteración cuestan ~9 ns. A esta escala el instrumento ya no es
despreciable frente a lo medido, y hay que declararlo.

---

## Contra TCP — con el control que separa lenguaje de transporte

Agregado de 3 rondas × 1 M por fila (3 M de muestras). Nanosegundos.

| | **B** Python+TCP | **Bc** C+TCP | **D** C+shm |
|---|---|---|---|
| p50 | 13 209 | 12 000 | **83** |
| p99.9 | 184 083 | 107 458 | **167** |
| máx | 44 020 084 | 29 423 042 | **34 833** |
| **muestras > 1 ms** | **363** ❌ | **141** ❌ | **0** ✅ |

**La comparación ya no mezcla variables.** `control-Bc-tcp-c/` mantiene el transporte de B
y cambia solo el lenguaje:

| Salto | Δ p50 | Factor | Peso |
|---|---|---|---|
| Lenguaje (B → Bc) | 1 209 ns | 1,1× | **9,2 %** |
| Transporte (Bc → D) | 11 917 ns | **144,6×** | **90,8 %** |

> **El mérito de D no es estar escrita en C: es no atravesar el kernel.** Reescribir el
> servicio en C sin cambiar de transporte lo habría dejado igual de incumplidor — pasa de
> 363 a 141 muestras por encima de 1 ms, y sigue fallando.

### La cola sigue ahí, sin un solo syscall

Máximos de 17,6 a 34,8 µs con cero llamadas al sistema y cero copias del kernel. **420× el
p50.** No lo causa el transporte: lo causan el planificador del sistema operativo, las
interrupciones y —muy probablemente— la migración del hilo a un núcleo de eficiencia, que en
macOS/arm64 no se puede impedir porque **no existe afinidad de núcleo** (`thread_policy_set`
devuelve `KERN_NOT_SUPPORTED`, verificado).

> Eliminar el software de la ruta caliente **no elimina la cola**. La cola la pone el sistema
> operativo y el hardware, y con esta plataforma no se puede quitar.
> Esa es la conclusión arquitectónica de la variante D, y vale más que los 83 ns.

---

## Archivos

| Archivo | Contenido |
|---|---|
| `common.h` | Región compartida, alineación a línea de caché, reloj, pausa de spin |
| `server.c` | Servidor: gira sobre la bandera, responde payload fijo. Escucha permanentemente |
| `client.c` | Cliente medidor: piso de medición, warmup, medición, contraste por lotes, CSV |
| `Makefile` | `-std=c11 -O2 -Wall -Wextra -pedantic` (no `-O3`: ver comentario en el archivo) |

Resultados en `../resultados/resultados-D-{1,2,3}.csv` y `../resultados/ejecucion-D-{1,2,3}.log`.
