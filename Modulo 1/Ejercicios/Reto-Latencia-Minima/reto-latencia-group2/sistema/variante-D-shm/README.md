# Variante D — memoria compartida + espera activa

**Responsable:** Daniel Mazo Serna · **Estado:** implementada y medida (3 rondas) · 2026-09-10
**Decisiones de diseño:** [`ADR-002`](../../docs/ADR/ADR-002-variante-D-memoria-compartida.md)
**Frontera de medición:** [`ADR-001`](../../docs/ADR/ADR-001-frontera-de-medicion.md) (F1, idéntica a las demás variantes)

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
Enmienda propuesta en [`ADR-003`](../../docs/ADR/ADR-003-resolucion-del-reloj.md).

**Consecuencia que hay que reportar siempre:** las muestras individuales están **cuantizadas
en múltiplos de 41,67 ns**. No es ruido, es el tamaño del tic.

---

## Resultados — 3 rondas × 1 000 000 de iteraciones, payload 32 B

Todas las cifras en **nanosegundos**. Integridad: 3 000 000 / 3 000 000 respuestas correctas.

Corrida oficial del **17/09/2026**.

| Ronda | mín | p50 | p90 | p99 | p99.9 | p99.99 | **máx** | media |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 83 | 84 | 125 | 167 | 250 | 37 125 | 77,9 |
| 2 | 0 | 83 | 84 | 84 | 166 | 292 | 33 208 | 77,6 |
| 3 | 0 | 83 | 84 | 125 | 125 | 209 | 16 167 | 81,1 |

**Contraste por lotes** (1000 intercambios cronometrados de una vez, 200 rondas): mediana de
**75 / 66 / 75 ns** por intercambio.

### Cómo leer estos números

La distribución **no es una campana: son escalones de un tic** (ronda 1):

| Valor | Tics | Muestras | % |
|---|---|---|---|
| 0 ns | 0 | 68 | 0,01 % |
| 41–42 ns | 1 | 204 750 | **20,48 %** |
| 83–84 ns | 2 | 726 629 | **72,66 %** |
| 125 ns | 3 | 66 222 | 6,62 % |
| ≥ 167 ns | ≥ 4 | 2 331 | 0,23 % |

El 93,1 % de las muestras cae en dos cubos y el 99,8 % en tres. La latencia real está **entre 1
y 2 tics**, y el contraste por lotes la sitúa en **~66–75 ns**. El p50 reportado de 83 ns es el
tic superior: **sobreestima por cuantización, no porque el sistema sea más lento.**

> Esto es lo que justifica reportar las dos medidas. Con una sola, o se pierde la cola
> (lotes) o se exagera la mediana (muestras). Ninguna de las dos es «la verdadera».

**El observador pesa lo mismo que lo medido.** El piso del instrumento —un par de lecturas del
reloj sin nada en medio— se midió en cada ronda: p50 de 0 a 41 ns, p99 de 42 ns, frente a un p50
de 83 ns. A esta escala el instrumento no es despreciable, y hay que declararlo.

---

## Contra TCP

Agregado de 3 rondas × 1 M por columna (3 M de muestras). Nanosegundos. Corrida del 17/09.

| | **B** Python+TCP | **D** C+shm |
|---|---|---|
| p50 | 13 458 | **83** |
| p99.9 | 116 209 | **167** |
| máx | 13 649 750 | **37 125** |
| **muestras > 1 ms** | **136** ❌ | **0** ✅ |

> **La comparación mezcla dos variables, y hay que decirlo.** Entre B y D cambian el
> transporte *y* el lenguaje a la vez, así que el factor 162× **no es atribuible a ninguno de
> los dos por separado**. Un control que sí las separaba (`Bc`, TCP en C) se midió y se retiró
> con el ADR-007; el informe declara la limitación en vez de ocultarla (§7.2, limitación 3).

> **Lo que sí distingue a D no es su velocidad, sino que su peor caso está acotado por
> construcción.** B dio 136 muestras sobre 1 ms el 17/09 y **0** el 14/09, con el mismo código:
> su cumplimiento depende del estado de la máquina. D dio 0 en las dos corridas.

### La cola sigue ahí, sin un solo syscall

Máximos de 16,2 a 37,1 µs con cero llamadas al sistema y cero copias del kernel. **447× el
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
