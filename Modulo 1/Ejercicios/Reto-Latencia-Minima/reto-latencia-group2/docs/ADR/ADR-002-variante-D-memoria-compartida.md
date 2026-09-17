# ADR-002 — Variante D: mecanismo, lenguaje y estrategia de planificación

**Estado:** Propuesta
**Fecha:** 2026-09-10
**Decisores:** Daniel Mazo Serna (responsable de la variante D)
**Contexto del módulo / ejercicio:** Módulo 1 · Actividad M1 «Reto de Latencia Mínima» ·
variante D del estudio comparativo (ver `PLAN-EQUIPO.md`)

## Contexto

La variante D representa el extremo inferior del estudio: el límite físico de la comunicación
entre dos procesos. Su función en el trabajo no es ganar, es **mostrar cuánto cuesta ganar** —
qué atributos de calidad hay que sacrificar para bajar tres órdenes de magnitud respecto de la
opción convencional.

### Entorno verificado (no supuesto), 2026-09-10

| | |
|---|---|
| CPU | Apple M4 — 10 núcleos: **4 de rendimiento + 6 de eficiencia** |
| Arquitectura | `arm64` — **modelo de memoria débilmente ordenado** |
| SO | macOS 26.6.2 (Darwin 25.6.0) — kernel de propósito general, **no** de tiempo real |
| Compiladores disponibles | Apple clang 21 · Java 21 · Python 3.13. **No hay** Rust, Go ni Zig |

### Restricción de plataforma descubierta al verificar

`thread_policy_set(THREAD_AFFINITY_POLICY)` devuelve **`KERN_NOT_SUPPORTED` (46)** en este
equipo. Comprobado con un programa de prueba, no asumido.

**Consecuencia:** en macOS sobre Apple Silicon **no se puede fijar un hilo a un núcleo.** Esto
no es un detalle de implementación: el *pinning* es la técnica estándar para acotar la cola de
latencia, y aquí simplemente no existe. Peor aún, el planificador puede migrar el hilo a un
núcleo de **eficiencia**, que es sustancialmente más lento que uno de rendimiento — lo que se
manifestará como saltos en los percentiles altos.

> **[REC]** Esto convierte una limitación en el mejor material del informe: la variante D va a
> demostrar que **el hardware y el sistema operativo son restricciones arquitectónicas de primer
> orden**, no un detalle de despliegue. Es exactamente el frente «tecnología» de la taxonomía de
> restricciones del módulo, y aquí se puede mostrar con números en vez de con una definición.

## Problema

¿Con qué mecanismo, en qué lenguaje y bajo qué estrategia de planificación se implementa la
variante D, dado que no existe afinidad de núcleos en la plataforma disponible?

## Opciones consideradas

### Mecanismo de transporte

**M1 — Memoria compartida POSIX (`shm_open` + `mmap`) con banderas atómicas y busy-spin**
- Cero llamadas al sistema en la ruta caliente. Cero copias más allá del `memcpy` del payload.
- El productor publica y el consumidor gira leyendo una bandera atómica: no hay despertar del
  planificador, que es el componente dominante de la latencia en los otros transportes.
- Contra: consume dos núcleos al 100 % sin trabajo útil; requiere razonar sobre visibilidad de
  memoria y barreras, que es donde aparecen los errores sutiles.

**M2 — Memoria compartida con semáforos o *futex* para despertar al consumidor**
- No quema CPU en reposo.
- Contra: **reintroduce el planificador**, que es justo lo que la variante quiere eliminar. El
  coste de un despertar (~1–10 µs) domina y la variante deja de distinguirse de la C. No
  cumpliría su función en el estudio.

**M3 — Cola en memoria compartida con `pthread_mutex` en memoria compartida entre procesos**
- Más convencional y fácil de razonar.
- Contra: el mutex sin contención es barato, pero con contención bloquea, y el bloqueo vuelve a
  pasar por el kernel. Mismo problema que M2, con menos claridad conceptual.

### Lenguaje

**L1 — C11 con `stdatomic.h`**
- Control exacto sobre asignaciones, copias y barreras de memoria. `clang` ya está instalado.
- Acceso directo a `clock_gettime(CLOCK_MONOTONIC)`, a `mmap` y a las primitivas de `mach`.
- Contra: gestión manual de memoria; errores de visibilidad silenciosos.

**L2 — Java 21**
- Disponible. Tiene `System.nanoTime()` y `MemorySegment` para memoria fuera del montículo.
- Contra: el recolector de basura y la compilación JIT introducen pausas justo en los
  percentiles que la variante pretende demostrar. Sería una elección interesante para un
  estudio de *jitter* de JVM, pero contamina el objetivo de esta variante.

**L3 — Python 3.13 con `multiprocessing.shared_memory`**
- Coherente con las demás variantes; el equipo ya lo tiene.
- Contra: el sobrecoste del intérprete (del orden de µs) **es mayor que la latencia que se
  intenta medir**. La variante mediría Python, no memoria compartida. Inviable para su función.

### Estrategia de planificación, sin afinidad disponible

**P1 — No hacer nada**: aceptar que el planificador decida, incluidos los núcleos de eficiencia.
**P2 — Clase de calidad de servicio `QOS_CLASS_USER_INTERACTIVE`** (`pthread_set_qos_class_self_np`):
en Apple Silicon sesga al planificador hacia los núcleos de rendimiento. Es una *sugerencia*, no
una garantía.
**P3 — Simular afinidad ocupando todos los núcleos** con hilos que giran en vacío: hostil,
no determinista y falsea el entorno.

## Decisión

- **Mecanismo: M1** — memoria compartida POSIX + dos banderas atómicas + busy-spin.
- **Lenguaje: L1** — C11 con `stdatomic.h`, compilado con `clang -O2`.
- **Planificación: P2** — `QOS_CLASS_USER_INTERACTIVE` en ambos procesos, **declarando
  explícitamente en el informe que es una sugerencia al planificador y no afinidad real**, y
  reportando la cola de latencia como evidencia de lo que eso cuesta.

Detalles de implementación que quedan fijados por esta decisión:

| Aspecto | Decisión | Por qué |
|---|---|---|
| Sincronización | `atomic_uint_fast32_t` con `memory_order_acquire` / `release` | `arm64` reordena. `volatile` **no** basta: no impone barreras y el código sería incorrecto en esta CPU aunque funcionara en x86 |
| Protocolo | Dos secuencias monótonas (petición, respuesta), sin ring buffer | Con **una petición en vuelo** (ESPEC §2), un ring buffer es sobreingeniería: añade índices, módulo y razonamiento sobre envoltura sin reducir latencia |
| Separación de líneas de caché | Cada bandera en su propia línea de 128 B | Evita *false sharing*: si ambas banderas comparten línea, cada escritura invalida la caché del otro núcleo y la latencia se duplica o peor |
| Reloj | `clock_gettime(CLOCK_MONOTONIC)` | ESPEC §2. Se mide y reporta además su propio sobrecoste |
| Espera | Busy-spin con `__builtin_arm_isb(15)` (`isb sy`) en el bucle | Sugerencia de pausa a la CPU; reduce consumo sin ceder el núcleo |

## Justificación

1. **Cumple su función en el estudio (AC-3).** M1 es la única opción que elimina el planificador
   de la ruta caliente. M2 y M3 lo reintroducen y harían que D se solapara con C, dejando el
   estudio con tres puntos de datos en vez de cuatro.
2. **El lenguaje es una restricción del atributo, no una preferencia.** En L2 y L3 el sobrecoste
   del runtime supera la magnitud a medir. La única forma de que la variante D signifique algo
   es un lenguaje sin runtime en medio. Esto ilustra el frente **tecnología** de las
   restricciones del módulo: la decisión de lenguaje deja de ser gusto y pasa a ser
   arquitectónica cuando el atributo de calidad está en el límite.
3. **P2 es la respuesta honesta a una restricción que no se puede levantar.** No hay afinidad en
   esta plataforma. Fingir determinismo sería peor que documentar su ausencia y medir el daño.

## Ventajas

- Latencia esperada en el rango de decenas a centenas de nanosegundos: 2–3 órdenes de magnitud
  por debajo de la variante A, lo que da al estudio su rango completo.
- Sin llamadas al sistema, sin copias del kernel, sin despertares: cada elemento eliminado es
  atribuible a una capa concreta de la pila, que es lo que el informe quiere demostrar.
- Código corto (~150 líneas por proceso) pese a ser el más exótico.

## Desventajas

- **Dos núcleos al 100 %** de forma permanente, sin trabajo útil. En un servidor real esto es
  inaceptable salvo en nichos concretos.
- **No funciona entre máquinas.** Elimina por completo la interoperabilidad.
- Depende del sistema operativo y de la arquitectura de CPU: no es portable.
- Errores de visibilidad de memoria que no se manifiestan en pruebas cortas y aparecen bajo
  carga. Riesgo real en `arm64`.
- Sin afinidad, la cola seguirá mostrando migraciones a núcleos de eficiencia. **El objetivo de
  determinismo (AC-2) probablemente no se cumpla del todo, y eso hay que reportarlo.**

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Barreras de memoria mal puestas → resultados corruptos silenciosos | Media | **Alto** | Validar el payload recibido en cada iteración fuera de la sección cronometrada; `atomic` con acquire/release, nunca `volatile` |
| Migración a núcleo de eficiencia → saltos en p99.9 | **Alta** | Medio | QoS `USER_INTERACTIVE`; reportar la cola como hallazgo, no ocultarla; 3 rondas independientes |
| El sobrecoste del reloj es comparable a la latencia medida | **Alta** | Medio | Medir el coste del par de llamadas al reloj en vacío y reportarlo como piso de medición junto a cada cifra |
| Termorregulación en un portátil durante 1 M de iteraciones a 100 % de dos núcleos | Media | Medio | Registrar la duración de la corrida; comparar las 3 rondas; si divergen, reducir iteraciones |
| Se lee como «C es más rápido que Python» en vez de «memoria compartida evita el kernel» | **Alta** | Medio | ⚠️ **REABIERTO el 17/09.** Se cerró el 10/09 midiendo el control `Bc` (TCP en C): 9,2 % lenguaje, 90,8 % transporte. El ADR-007 retiró `Bc` del árbol, así que esa cuantificación ya no se reproduce y el riesgo vuelve a estar vivo. El informe lo neutraliza **declarando la limitación** en vez de ocultarla (§7.2 y limitación 3): no atribuye el factor 162× a ninguna de las dos causas |

## Consecuencias

**Queda habilitado**
- El estudio cubre un rango de ~4 órdenes de magnitud, que es la tesis del trabajo.
- Se puede cuantificar por diferencia el coste de cada capa: pila de red (B−C), protocolo de
  aplicación (A−B), y llamadas al sistema + planificador (C−D).

**Queda bloqueado**
- La variante D no puede formar parte de ninguna medición entre máquinas.
- No se puede afirmar determinismo: sin afinidad, la cola no está acotada por diseño.

**Deuda aceptada**
- Sin ring buffer, la variante no soporta varias peticiones en vuelo. Es coherente con S2 y con
  ESPEC §2, pero hay que decirlo: **la variante D no es un sistema, es un experimento.**
- El código no se probará en Linux, donde sí habría afinidad y los números serían mejores. Se
  menciona como trabajo futuro, no se afirma nada sobre ello.

**Revisar si**
- Aparece una máquina Linux para la ronda final → reevaluar P2 y rehacer la medición con
  afinidad real; sería un contraste excelente para el informe.
- El p99.9 de D resulta peor que el de C → **no es un fallo del experimento, es el resultado**:
  significaría que el coste de la migración entre núcleos supera al de la llamada al sistema, y
  ese hallazgo vale más que la mediana.
