# Reto de Latencia Mínima — Documentación técnica e informe de resultados

**Diplomado en Arquitectura de Software y Cloud Computing** · Pontificia Universidad Javeriana Cali  
**Módulo 1** — Fundamentos de la Arquitectura de Software · **Group 2**  
Daniel Mazo Serna · Freddy Aparicio Marín · Camilo Céspedes Leguizamón

> Este documento cubre los **entregables 2 y 4** del enunciado (documentación técnica e informe
> de resultados), que el enunciado permite fusionar.
>
> **Corrida oficial: 17/09/2026.** Dos configuraciones, 3 rondas × 1 000 000 de iteraciones cada
> una, 3 000 000 de muestras por configuración. Toda cifra de este informe sale de los CSV y los
> logs que acompañan a la entrega, y se reproduce con los comandos de §10.2.
>
> Alcance: variantes **B** y **D** ([ADR-007](reto-latencia-group2/docs/ADR/ADR-007-reduccion-de-alcance.md)).
> Las variantes A y C nunca se implementaron; los experimentos `Bc` y `E` se midieron y se
> retiraron del árbol. **Ninguna conclusión de este informe se apoya en ellos**; sus hallazgos
> quedan archivados en `reto-latencia-group2/docs/archivo/` como historia del proyecto.

---

## 1. Resumen ejecutivo

Se construyó un servicio que responde a un estímulo de 32 bytes con una respuesta de 32 bytes
—un veredicto sobre el host consultado— y se midió su latencia de ida y vuelta bajo una
metodología única. El objetivo del enunciado era **una latencia inferior a 1 ms**.

**El objetivo se alcanza trivialmente.** La configuración más lenta que medimos —un servidor
TCP escrito en Python— responde con una mediana de **13,5 µs**, unas **74 veces por debajo** del
umbral. Conseguir el número no era el reto.

El trabajo real fue otro. Medimos **dos configuraciones bajo condiciones idénticas** y obtuvimos
tres resultados que no se ven mirando el promedio:

| Hallazgo | Evidencia |
|---|---|
| **Si una de las dos cumple el objetivo depende del día, no de su arquitectura.** | Por p50 ambas cumplen con holgura (74× y 12 048× por debajo). Por la cola, B superó 1 ms en **136 muestras de 3 000 000** el 17/09 y en **0 de 3 000 000** el 14/09, con el mismo código. D no lo superó **ninguna vez en las dos corridas**. |
| **El máximo no es una propiedad del sistema sino de cuánto se observe.** | Dentro de **la misma corrida**, el máximo de B pasa de 167 µs con 10 000 muestras a **13,6 ms con 3 000 000**: 81× peor sin que cambie nada del sistema. |
| **Eliminar el software de la ruta crítica no elimina la latencia impredecible.** | D no hace una sola llamada al sistema operativo y aun así su máximo es de 37 µs, **447× su mediana**. La imponen el planificador y el hardware. |

**Conclusión arquitectónica:** el reto no se gana optimizando, se gana **decidiendo en qué capa
está el coste** y aceptando explícitamente qué se sacrifica a cambio. Un informe basado en
promedios (14,7 µs frente a 79 ns) habría dado las dos configuraciones por buenas. **La métrica
elegida, no el sistema, es lo que determina el veredicto.**

---

## 2. El problema y los drivers arquitectónicos

### 2.1 Requisitos, extraídos del enunciado

| # | Driver | Origen textual | Tipo |
|---|---|---|---|
| D1 | Latencia de ida y vuelta < 1 ms | «preferiblemente menor a un milisegundo» | Atributo de calidad |
| D2 | El sistema escucha permanentemente | «debe escuchar permanentemente peticiones» | Restricción funcional |
| D3 | Ante un estímulo, retorna una respuesta específica | «retornar una respuesta específica» | Requisito funcional |
| D4 | La latencia debe medirse | «debe medirse el tiempo transcurrido» | Observabilidad |
| D5 | Las herramientas deben justificarse | «justificación de herramientas, lenguajes y metodologías» | Proceso |
| D6 | Comparación explícita contra 1 ms | «comparación explícita con el objetivo de 1 ms» | Reporte |

### 2.2 Lo que el enunciado no pide — y por qué importa

El enunciado **no** exige concurrencia, durabilidad, disponibilidad, red física entre máquinas,
ni seguridad. Esa ausencia define el alcance tanto como lo que sí pide, y es la justificación
formal para **no** incorporar contenedores, frameworks, brokers de mensajes, balanceadores ni
TLS: ninguno reduce la latencia y todos la aumentan.

### 2.3 Supuestos declarados

| # | Supuesto | Riesgo si es falso |
|---|---|---|
| S1 | Mensajes de tamaño fijo y pequeño (32 B) | Bajo: por debajo del MTU el orden de magnitud no cambia |
| S2 | Un solo cliente, una petición en vuelo | Medio: cambia la interpretación; se declara en §5.2 |
| S3 | Cliente y servidor en el mismo host | **Alto: es lo que más baja el número. Ver §8.2** |
| S4 | Sistema en reposo durante la medición | Medio: infla la cola; se registra la carga |

> **S3 se declara en voz alta y no se esconde.** Medir en loopback elimina la red, que en un
> sistema real es el componente dominante. Presentar 13 µs como «latencia del sistema» sin
> decir que no hay red de por medio sería deshonesto.

### 2.4 Atributos de calidad — escenarios medibles

Un atributo sin medida de respuesta es un deseo, no un requisito.

**AC-1 · Latencia.** Ante un estímulo de 32 B con el sistema en reposo y una petición en vuelo,
**el p99.9 del RTT debe ser inferior a 1 ms**, medido en espacio de usuario del cliente.

**AC-2 · Determinismo.** Sobre 1 000 000 de mensajes consecutivos, **la relación p99.9/p50 debe
ser ≤ 10 y ninguna muestra debe superar 1 ms.** *(Este atributo no lo pide el enunciado: lo
añadimos porque en sistemas de baja latencia reales el requisito nunca es «que sea rápido» sino
«que la cola sea acotada».)*

**AC-3 · Comparabilidad.** Todas las configuraciones producen el mismo formato de muestras
crudas y sus métricas las calcula **un único script**.

**AC-4 · Trazabilidad.** Toda cifra de este informe es reproducible desde un CSV de la entrega
más el entorno registrado en su log.

---

## 3. Arquitectura del sistema

### 3.1 Contexto

```text
   ┌──────────────────┐   estímulo 32 B    ┌────────────────────┐
   │ Cliente medidor  │ ─────────────────▶ │ Clasificador       │
   │ genera y         │                    │ escucha permanente │
   │ cronometra       │ ◀───────────────── │ responde 32 B      │
   └────────┬─────────┘   veredicto 32 B   └────────────────────┘
            │ vuelca al final
            ▼
   ┌──────────────────┐                    ┌────────────────────┐
   │ CSV crudo        │ ─────────────────▶ │ Analizador         │
   │ iteracion,ns     │                    │ percentiles + SVG  │
   └──────────────────┘                    └────────────────────┘
```

El analizador está **fuera de la ruta crítica por diseño**: calcular percentiles dentro del
bucle mediría el analizador, no el sistema.

### 3.2 Las configuraciones medidas

La diferencia entre ellas es **cuánta pila de sistema atraviesa cada mensaje**:

```text
 B  aplicación ──────────────→ TCP → IP → loopback → IP → TCP ──────────────→ aplicación
 D  aplicación ─────────────→ memoria física compartida ─────────────────────→ aplicación
                              (sin llamadas al sistema en la ruta crítica)
```

| ID | Transporte | Lenguaje | n | Estado |
|---|---|---|---|---|
| **B** | TCP crudo, `TCP_NODELAY`, conexión persistente | Python 3.13 | 3 000 000 | ✅ medida |
| **D** | Memoria compartida POSIX + espera activa | C11 | 3 000 000 | ✅ medida |

**Estas dos son los extremos del espectro razonable**: la opción más portable y convencional
frente a la más rápida posible en un solo host. Se consideraron configuraciones intermedias
—HTTP/REST y socket de dominio Unix— y no se implementaron; la decisión y su coste están en el
ADR-007.

> **Limitación que esta elección impone, y que se declara aquí y en §9:** B y D difieren en
> **dos** dimensiones a la vez, transporte *y* lenguaje. Por tanto el factor de 162× entre ellas
> **no puede atribuirse a una sola causa** con los datos de esta entrega. Lo que el experimento
> sostiene es el efecto conjunto, no su descomposición.

### 3.3 La variante Memoria compartida C en detalle

Dos procesos comparten 256 bytes de memoria física (`shm_open` + `mmap`). No hay sockets, no hay
kernel en la ruta crítica, no hay planificador.

```text
   CLIENTE                      región compartida (256 B)         SERVIDOR
   t0 = reloj          ┌─── línea de caché 0 (128 B) ───┐
   memcpy payload ────▶│ seq_peticion │ payload 32 B    │◀──── espera activa
   store(seq,release)─▶│              │                 │      load(acquire)
                       └────────────────────────────────┘
                       ┌─── línea de caché 1 (128 B) ───┐
   espera activa ─────▶│ seq_respuesta│ payload 32 B    │◀──── memcpy respuesta
   load(acquire)       │              │                 │◀──── store(seq,release)
   memcpy a local      └────────────────────────────────┘
   t1 = reloj
```

Tres decisiones que no son microoptimización sino corrección o un orden de magnitud:

1. **Cada sentido en su propia línea de caché (128 B en Apple Silicon).** Compartir línea
   provocaría *false sharing*: cada escritura de un proceso invalidaría la caché del otro.
2. **`_Atomic` con `acquire`/`release`, nunca `volatile`.** `arm64` tiene modelo de memoria
   débilmente ordenado: sin barreras, el otro núcleo puede ver la bandera antes que el dato. El
   mismo código con `volatile` funcionaría en x86 y **estaría roto aquí**.
3. **Espera activa que no cede el núcleo.** Ceder significa volver al planificador, que es
   exactamente el coste que esta configuración existe para eliminar. Precio: dos núcleos al
   100 % permanentemente.

**Lo que deliberadamente no tiene:** ring buffer. Con una sola petición en vuelo añadiría
índices y aritmética modular sin reducir latencia. Sería sobreingeniería.

---

## 4. Justificación de herramientas, lenguajes y metodologías

> Requisito explícito del enunciado (entregable 2, D5).

| Decisión | Alternativas descartadas | Por qué |
|---|---|---|
| **Un estudio comparativo en vez de una implementación** | Una sola implementación optimizada | El objetivo se cumple con 40 líneas. Tres personas en un servidor de eco se estorban, y el informe quedaría sin contenido arquitectónico. El temario del módulo es trade-offs; esto los ejercita, aquello no. |
| **Python para B** | C, Go, Java | Es el candidato más lento imaginable, y por eso el más informativo: si Python cumple el umbral, el umbral no es el reto. Además todos en el equipo lo tienen. |
| **C11 para D** | Java 21, Python | En Java el recolector de basura y el JIT introducen pausas en los percentiles que la configuración pretende demostrar. En Python el sobrecoste del intérprete (~µs) **es mayor que la latencia a medir**: mediría Python, no memoria compartida. |
| **Memoria compartida + espera activa para D** | Semáforos o *futex* sobre memoria compartida | Reintroducen el planificador, que es lo que D quiere eliminar. |
| **`TCP_NODELAY` en B** | Dejar Nagle activo | Sin ello el kernel agrupa paquetes pequeños y aparecen picos de decenas de ms. Es el error clásico del ejercicio. |
| **Conexión persistente** | Conexión por petición | El handshake se paga una vez, en el calentamiento. Repartirlo por iteración falsearía. |
| **SVG generado sin dependencias** | matplotlib | El proyecto lo comparten tres personas: una dependencia obliga a las tres a instalarla y a que coincidan las versiones. Con la librería estándar cualquiera regenera las figuras idénticas. |
| **Un único script de análisis** | Que cada uno calcule sus percentiles | Sin esto los resultados no son comparables (AC-3), y la comparabilidad es la tesis del trabajo. |

### Lo que se decidió NO construir

| Descartado | Por qué |
|---|---|
| Base de datos | Nada que persistir |
| Contenedores | Añaden red virtualizada: **aumentan** la latencia |
| Framework web (en el plano de datos) | Capas de indirección en la ruta crítica |
| Broker de mensajes | Un salto de red y persistencia: tres órdenes de magnitud en contra |
| TLS / autenticación | Sin superficie de amenaza en el alcance; añade handshake y cifrado por mensaje |
| Reintentos, circuit breaker | Sin requisito de disponibilidad; añaden ramas en la ruta crítica |

> Justificar una ausencia es más difícil, y vale más, que justificar una presencia.

---

## 5. Cómo se mide la latencia

> Requisito explícito del enunciado (entregable 2, D4). **Es la decisión arquitectónica central
> del trabajo:** el mismo sistema, sin cambiar una línea, reporta entre 5 µs y 50 ms según dónde
> se coloquen las sondas.

### 5.1 La frontera de medición

Se adopta **F1 — RTT de aplicación medido en el cliente**:

```text
t0 = reloj monótono, inmediatamente ANTES de escribir el estímulo
t1 = reloj monótono, inmediatamente DESPUÉS de tener la respuesta completa en buffer local
latencia = t1 - t0
```

**Incluye** serialización, escritura, transporte, procesamiento del servidor, transporte de
vuelta, lectura completa y cualquier cambio de contexto ocurrido en medio.
**Excluye** el establecimiento de la conexión (se paga una vez, en el calentamiento) y el
arranque del proceso.

Fronteras consideradas y descartadas:

| Frontera | Qué mide | Valor típico | Por qué se descartó |
|---|---|---|---|
| **F1 ✅** | RTT de aplicación completo | ~13 µs | *Es lo que percibe un consumidor real* |
| F2 | Solo la llamada al sistema | ~5 µs | Esconde el coste de recibir; no tiene análogo en D, que no hace llamadas al sistema |
| F3 | Incluye la conexión | ~100 µs | Con conexión persistente, repartir el handshake por iteración falsea |
| F4 | Incluye el arranque del proceso | ~50 ms | Mide el arranque del runtime, no el sistema |
| F5 | Solo ida (cliente→servidor) | ~6 µs | **Inválida:** exige dos relojes sincronizados mejor que la magnitud medida. Entre procesos, el desfase es del mismo orden que la latencia |

> **F1 es la más desfavorable de las defendibles.** Elegir deliberadamente la medida que nos
> perjudica es lo que da credibilidad al cumplimiento. Podríamos haber reportado 5 µs con F2, y
> habría sido igualmente «cierto».

Decisión completa y consecuencias: **ADR-001**.

### 5.2 Protocolo experimental

| Parámetro | Valor | Por qué |
|---|---|---|
| Modo | Closed-loop, **1 petición en vuelo** | Mide tiempo de servicio en vacío. Evita *coordinated omission* |
| Calentamiento | 100 000 iteraciones, descartadas | Cachés, TLB, JIT, ramp-up de frecuencia de CPU |
| Medición | 1 000 000 iteraciones × 3 rondas | 3 000 000 de muestras por configuración |
| Payload | 32 B fijos en ambos sentidos | Idéntico en todas o la comparación no vale |
| Almacenamiento | Array preasignado y pre-tocado | Asignar o provocar fallos de página en el bucle contaminaría |
| Volcado | Al final, nunca dentro del bucle | Escribir a disco mediría el disco |
| Rondas del informe | **1, 2 y 3** | Las rondas 0 y 9 son validación y pruebas rápidas: no entran ni en las tablas ni en las figuras |
| Corridas independientes | **2** (14/09 y 17/09) | Un solo conjunto de rondas no distingue una propiedad de la arquitectura de un estado pasajero de la máquina. Ver §7.1 |

### 5.3 El instrumento: un problema que apareció al medir

La primera corrida de la variante Memoria compartida C devolvió **ceros**. No era un fallo del código.

Granularidad real de cada reloj, medida en el equipo (200 000 pares de lecturas consecutivas):

| Reloj | Granularidad | % de deltas nulos |
|---|---|---|
| `clock_gettime(CLOCK_MONOTONIC)` | **1000 ns** | **97,6 %** |
| `clock_gettime(CLOCK_MONOTONIC_RAW)` | 41 ns | 40,1 % |
| `clock_gettime_nsec_np(CLOCK_UPTIME_RAW)` ✅ | 41 ns | 57,0 % |
| Contador de hardware (24 MHz) | **41,67 ns** | piso físico |

«Resolución de nanosegundos» describe **las unidades del valor**, no **la granularidad con que
avanza**. `CLOCK_MONOTONIC` devuelve nanosegundos y salta de microsegundo en microsegundo.
Nuestra propia especificación de medición contenía ese error, y la variante Memoria compartida C lo destapó.

**Regla adoptada (ADR-003):** la granularidad debe ser al menos **10× menor** que el p50
esperado. Si no lo es, la configuración añade un **contraste por lotes** como medida
*secundaria* —nunca sustituta— de los percentiles.

**Consecuencia reportada:** las muestras de D están **cuantizadas en múltiplos de 41,67 ns**.
No es ruido: es el tamaño del tic.

### 5.4 Entorno

| | |
|---|---|
| CPU | Apple M4 — 10 núcleos (4 de rendimiento + 6 de eficiencia) |
| Arquitectura | `arm64`, modelo de memoria débilmente ordenado |
| Sistema operativo | macOS 26.6 (Darwin 25.6.0), kernel de propósito general |
| Compilador | Apple clang, `-std=c11 -O2` |
| Runtime | Python 3.13 |
| Fijación de hilos a núcleos | **No disponible.** `thread_policy_set(THREAD_AFFINITY_POLICY)` devuelve `KERN_NOT_SUPPORTED` (verificado con programa de prueba) |

**Las dos configuraciones se midieron en la misma máquina en reposo, el mismo día.** Si se
ejecutaran en equipos distintos, los números no serían comparables y el estudio perdería su
tesis; `analyze.py` se niega a mezclar plataformas por esa razón (ADR-005).

---

## 6. Resultados

Agregado de 3 rondas × 1 000 000 por columna. Todo en **nanosegundos**. Corrida del 17/09/2026.

| | **B** Python + TCP | **D** C + memoria compartida |
|---|---|---|
| n | 3 000 000 | 3 000 000 |
| mín | 7 625 | 0 |
| **p50** | 13 458 | **83** |
| p90 | 17 459 | 84 |
| p99 | 44 917 | **125** |
| **p99.9** | 116 209 | **167** |
| p99.99 | 599 125 | **250** |
| **máx** | **13 649 750** | **37 125** |
| media *(no es la métrica principal)* | 14 746 | 79 |
| **muestras > 1 ms** | **136** | **0** |
| p99.9 / p50 | 8,6× | **2,0×** |
| máx / p50 | 1 014× | 447× |

> **Esta tabla describe una corrida, no la arquitectura.** Una corrida anterior del 14/09, con
> el mismo código y el mismo `n`, dio para B un máximo de 344 880 ns y **cero** muestras sobre
> 1 ms. La diferencia no está en el sistema sino en el estado de la máquina; se analiza en §7.1
> y es uno de los resultados del trabajo. Su evidencia se conserva en
> `sistema/resultados/archivo/`.

**Figuras:** `reto-latencia-group2/sistema/graficas/percentiles.svg` y `…/histograma.svg`.
Se regeneran con `python3 reto-latencia-group2/sistema/graficas.py` (sin dependencias externas).

### 6.1 Contraste por lotes para la variante Memoria compartida C

Cronometrando 1000 intercambios de una vez y dividiendo (200 rondas), la mediana por intercambio
fue de **75, 66 y 75 ns** en las tres rondas, frente a los 83 ns del p50 por muestra.

La diferencia es explicable y no es contradicción:

- El p50 de 83 ns es el **segundo tic** de la cuantización. La latencia real está entre uno y dos
  tics; los lotes la sitúan en ~66–75 ns. **El p50 sobreestima por cuantización.**
- El piso del instrumento —un par de lecturas del reloj sin nada en medio— se midió en cada
  ronda: p50 de 0 a 41 ns, p99 de 42 ns. **A esta escala el instrumento es del mismo orden que
  lo medido**, y por eso se reporta aparte.

> Se reportan las dos medidas, etiquetadas. Con una sola, o se pierde la cola (lotes) o se
> exagera la mediana (muestras). Ninguna es «la verdadera».

### 6.2 Distribución de la variante Memoria compartida C — no es una campana

Ronda 1, n = 1 000 000. El tic del contador es de 41,67 ns:

| Valor | Tics | Muestras | % |
|---|---|---|---|
| 0 ns | 0 | 68 | 0,01 % |
| 41–42 ns | 1 | 204 750 | **20,48 %** |
| 83–84 ns | 2 | 726 629 | **72,66 %** |
| 125 ns | 3 | 66 222 | 6,62 % |
| ≥ 167 ns | ≥ 4 | 2 331 | 0,23 % |

El 93,1 % de las muestras cae en dos cubos y el 99,8 % en tres: son los tics del reloj. **El
instrumento es visible en el resultado**, y por eso hay que declararlo.

### 6.3 El dominio no contamina la medición — y no se supone, se mide

El servicio no hace eco: clasifica. Consultar la tabla de 16 hosts ocurre **dentro** de la ruta
caliente, así que hay que demostrar que no es eso lo que se está midiendo.

**El método obvio no sirve, y descartarlo es parte del resultado.** El primer intento fue
restar dos corridas de D, con y sin clasificador. La varianza entre rondas (±13 ns) resultó ser
mayor que el efecto buscado (~2 ns): una pareja de corridas dio 7 ns de diferencia que al
repetirse se disolvió. **Era ruido presentado como señal**, y nadie lo habría detectado desde
fuera. Un método que no resuelve el efecto que mide produce números, no resultados.

El método válido aísla el clasificador del RTT (`sistema/control-dominio/micro.c`): se cronometra
por lotes de 100 000 iteraciones contra un bucle de referencia idéntico **sin** la llamada, y se
resta. El acumulador es `volatile` para que el optimizador no borre el bucle.

| | ns por llamada |
|---|---|
| Bucle de referencia | 0,281 |
| Bucle con `clasificar()` | 2,226 |
| **Coste del clasificador** | **1,945** |

| Frente a | Peso |
|---|---|
| Variante Memoria compartida C (p50 83 ns) | 2,3 % |
| Variante TCP Python (p50 13 458 ns) | **0,014 %** |
| Un tic del reloj (41,67 ns) | por debajo de un solo tic |

**El matiz honesto: en D es el 2,3 %, no cero.** A 83 ns ya nada es gratis. Decir «despreciable»
sin el número sería la misma afirmación sin respaldo que este informe critica en otros sitios.

**Segundo control: ¿cuesta lo mismo responder LOCAL que EXTERNO?** `clasificador.h` *afirma* ser
de tiempo constante —recorre siempre las 16 ranuras, sin salida anticipada—;
`control-dominio/veredicto.c` lo *mide*:

| Veredicto | p50 |
|---|---|
| LOCAL | 2,229 ns |
| EXTERNO | 2,225 ns |
| DESCONOCIDO | 2,229 ns |

Diferencia máxima entre veredictos: **0,004 ns**. Dispersión de un mismo veredicto al repetirlo:
**101 ns**. Los veredictos se separan entre sí cuatro órdenes de magnitud menos que lo que varía
uno solo: **la diferencia no se puede afirmar que exista**. El criterio no es un umbral elegido a
dedo, sino la comparación de dos dispersiones — el mismo razonamiento que invalidó el primer
intento de `micro.c`.

Esto aporta dos conclusiones independientes:

1. **Metodológica.** La latencia no depende del dato. Dos corridas con distinta mezcla de IPs dan
   el mismo número, así que la comparación entre transportes no está contaminada por qué se
   preguntó.
2. **De seguridad.** No hay **canal lateral temporal**: cronometrando la respuesta no se puede
   deducir si un host está en la lista negra. En un control de acceso real —el escenario que
   declara `tabla-hosts.csv`— eso sería una fuga de información.

```bash
cd reto-latencia-group2/sistema/control-dominio && make && ./micro ../tabla-hosts.csv && ./veredicto ../tabla-hosts.csv
```

---

## 7. Análisis

### 7.1 Comparación explícita con el objetivo de 1 ms

> Requisito explícito del enunciado (entregable 4, D6).

**Por mediana, las dos configuraciones cumplen con holgura:**

| | p50 | veces por debajo de 1 ms |
|---|---|---|
| B | 13 458 ns | 74× |
| D | 83 ns | **12 048×** |

**Por la cola, el resultado de B no es reproducible — y ese es el hallazgo:**

| | máx | muestras > 1 ms (de 3 M) | AC-1 (p99.9 < 1 ms) | AC-2 (ninguna > 1 ms) |
|---|---|---|---|---|
| B · corrida del **17/09** | 13 649 750 ns | **136** | ✅ cumple (116 µs) | ❌ **incumple** |
| B · corrida del **14/09** | 344 880 ns | **0** | ✅ cumple (39 µs) | ✅ **cumple** |
| D · ambas corridas | 37 125 ns | **0** | ✅ cumple (167 ns) | ✅ **cumple** |

**Mismo código, misma máquina, mismo tamaño de muestra, tres días de diferencia: un veredicto
distinto.** Lo único que cambió fue el estado del sistema operativo durante la medición. Una
tercera corrida, del 10/09, reportó 363 incumplimientos; se cita como referencia pero **su log
no se conservó**, así que este informe no la usa como evidencia.

> **Consecuencia metodológica, y es la más importante del trabajo:** afirmar «esta arquitectura
> incumple 1 ms» a partir de una sola corrida es afirmar algo **sobre la máquina, no sobre la
> arquitectura**. Lo correcto es reportar el número de corridas y el rango entre ellas, nunca un
> máximo suelto.

**Esta es la comparación que el enunciado pide, y la respuesta depende de cómo se lea «lograr
una latencia menor a 1 ms»:**

- Si significa *«la respuesta típica tarda menos de 1 ms»* → **las dos cumplen siempre**, y el
  reto se resuelve con 40 líneas de Python.
- Si significa *«el sistema nunca tarda más de 1 ms»* → **B lo cumple unas veces sí y otras no**,
  y D no falló en **6 000 000 de muestras repartidas en dos corridas**.

Un informe basado en promedios (14,7 µs frente a 79 ns) habría dado las dos por buenas. **La
métrica elegida, no el sistema, es lo que determina el veredicto.** Nótese además que B cumple
la parte de AC-2 referida a la forma de la distribución —p99.9/p50 = 8,6, por debajo del límite
de 10— y la incumple solo por los eventos raros: **un sistema puede tener una distribución sana
y aun así violar un requisito absoluto.**

**La lectura arquitectónica, que es lo que se califica:** para un requisito absoluto, una
arquitectura cuyo cumplimiento depende del estado de la máquina **no cumple**, aunque una
corrida concreta salga en cero. No se trata de que B sea lenta —es 74× más rápida que el
umbral— sino de que **su peor caso no está acotado por diseño**, mientras que el de D lo está
por construcción: sin llamadas al sistema no hay planificador que pueda robarle 13 ms.

### 7.2 Dónde está el coste, y qué no podemos afirmar

El salto de B a D es de **13 375 ns de mediana, un factor de 162×**. Entre las dos
configuraciones cambian dos cosas a la vez: el transporte (TCP sobre loopback → memoria física
compartida) y el lenguaje (Python → C11).

> **Limitación declarada: con los datos de esta entrega ese factor no se puede descomponer.**
> Atribuirlo al transporte sería una afirmación que el experimento no sostiene. Para separarlo
> haría falta un control que cambie **una sola** variable —el mismo transporte en el otro
> lenguaje—, y esa configuración no forma parte del alcance (ADR-007).

Lo que sí se sostiene con lo medido:

1. **El servicio no hace trabajo útil, y eso está medido, no supuesto.** Recibe 32 bytes,
   consulta una tabla de 16 entradas que cabe en una línea de caché y devuelve 32 bytes. Ese
   trabajo cuesta **1,9 ns** (§6.3): el 0,014 % del RTT de B. Por tanto **lo que separa a B de D
   es el coste de mover 32 bytes de un proceso a otro**, no el de procesarlos.
2. **Ese coste de transporte es de decenas de microsegundos en B**: dos llamadas al sistema, dos
   copias por el kernel, la pila TCP/IP completa y el despertar del planificador. En D es cero
   llamadas al sistema y una escritura en memoria física.
3. **La decisión que mueve la aguja es de arquitectura, no de implementación.** Es la distinción
   que el Módulo 1 plantea entre decisiones estructurales y detalles de implementación: la
   elección de la capa de comunicación es estructural, y es la que decide el orden de magnitud.

**Matiz obligatorio, para no convertir el hallazgo en consigna:** esto vale *en este servicio*,
que no hace trabajo útil. Con lógica de negocio, serialización o acceso a datos, la proporción
cambia. Lo demostrado es que **el transporte domina cuando el trabajo útil es despreciable**, no
que el lenguaje o el algoritmo nunca importen.

### 7.3 El máximo depende de cuánto se mire

Este es el resultado más incómodo, y se obtiene **sin cambiar nada del sistema**: basta con leer
la misma corrida de B tomando ventanas de observación cada vez más grandes.

| Muestras observadas (misma corrida) | Máximo acumulado |
|---|---|
| 10 000 | 167 541 ns |
| 100 000 | 3 129 125 ns — ya supera 1 ms |
| 1 000 000 | 6 386 208 ns |
| 3 000 000 | **13 649 750 ns** — **81× el de 10 000** |

No cambió el sistema, no cambió la máquina, no cambió el momento: **cambió cuánto se miró**. Al
observar más se capturan eventos más raros (planificación, interrupciones, presión de memoria,
termorregulación).

Tres consecuencias:

1. **Un máximo sin su `n` al lado no significa nada.** Por eso `n` aparece en todas las tablas.
2. **Por eso los sistemas serios se especifican en percentiles.** El p99.9 de B se movió entre
   72 y 254 µs según la ronda, mientras su máximo saltaba entre 6,4 y 13,6 ms. Ninguna de las
   dos medidas es perfectamente estable, pero el percentil describe la experiencia del 99,9 % de
   las peticiones y el máximo describe una sola.
3. Cualquier afirmación del tipo «nunca supera X» es, en rigor, «no lo superó en las N muestras
   que observamos». **Una demostración de 10 000 mensajes no habría visto un solo
   incumplimiento** de los 136 que existen.

### 7.4 La cola persiste aunque se elimine el software

La variante Memoria compartida C no hace **una sola llamada al sistema** en la ruta crítica, no copia por el
kernel y no cede el núcleo. Aun así:

```text
   p50 =     83 ns
   máx = 37 125 ns   →   447× la mediana
```

No lo causa el transporte. Lo causan el planificador del sistema operativo, las interrupciones
y, muy probablemente, la migración del hilo a un núcleo de eficiencia — que en macOS/arm64 **no
se puede impedir**, porque la afinidad de núcleo no existe (`KERN_NOT_SUPPORTED`, verificado).
Lo único disponible es la clase de calidad de servicio `QOS_CLASS_USER_INTERACTIVE`, que es una
sugerencia al planificador, no una garantía.

> **El sistema operativo y el hardware son restricciones arquitectónicas de primer orden, no
> detalles de despliegue.** Es el frente «tecnología» de la taxonomía de restricciones del
> módulo, demostrado aquí con medidas propias en lugar de con una definición.

---

## 8. Conclusiones y trade-offs

### 8.1 Ninguna arquitectura gana

| | **B** TCP + Python | **D** memoria compartida + C |
|---|---|---|
| Latencia p50 | 13,5 µs | **83 ns** |
| Muestras > 1 ms (de 3 M) | 136 una corrida, 0 la otra | **0 en las dos** |
| Peor caso acotado por diseño | ❌ depende del planificador | ✅ sin llamadas al sistema |
| Llamadas al sistema por RTT | 2 | **0** |
| Funciona entre máquinas | ✅ | ❌ |
| Interoperabilidad | media | ❌ nula |
| CPU en reposo | baja | ❌ **2 núcleos al 100 %** |
| Complejidad | baja | **alta** |
| Portabilidad | ✅ cualquier SO con Python | solo POSIX, y sin afinidad en macOS |
| Depurable con herramientas comunes | ✅ | ❌ |

**La pregunta correcta no es cuál es mejor, sino qué atributo prioriza el negocio:**

- Prioriza **interoperabilidad, portabilidad y velocidad de desarrollo** → **B**. Los 13 µs son
  irrelevantes para el 99 % de los sistemas de negocio, y el umbral del enunciado ya lo cumple.
- Prioriza **determinismo extremo en un solo host** y puede pagar dos núcleos dedicados, código
  no portable y nula interoperabilidad → **D**.

**La trampa del ejercicio:** el enunciado premia el número bajo, y el número bajo lo gana D.
Pero D es la peor arquitectura posible para casi cualquier sistema real. Concluir «usen memoria
compartida» sería haber aprendido a optimizar, no a arquitecturar. **El umbral de 1 ms ya lo
cumple la opción más simple y portable**; pasar de B a D compra dos órdenes de magnitud que
casi nadie necesita, al precio de todos los demás atributos.

La excepción es precisamente el requisito absoluto: si el contrato dice *«ninguna respuesta por
encima de 1 ms»*, B no sirve — no por lenta, sino porque **su peor caso depende del estado de la
máquina** y no de su diseño: una corrida da cero incumplimientos y la siguiente, 136.
**Ese es el único escenario en que el precio de D se justifica**, y la razón no es que D sea
rápida sino que su peor caso está acotado por construcción.

### 8.2 Atributos sacrificados por la variante Memoria compartida C

| Atributo | Se sacrifica | A cambio de |
|---|---|---|
| Portabilidad | Depende del SO y de la arquitectura de CPU | 2 órdenes de magnitud de latencia |
| Escalabilidad | Un solo cliente; dos núcleos al 100 % | Eliminar el despertar del planificador |
| Eficiencia de recursos | Dos núcleos quemados sin trabajo útil | Determinismo en la cola |
| Interoperabilidad | Solo entre procesos del mismo host | Evitar la pila de red completa |
| Mantenibilidad | Código de bajo nivel, errores de visibilidad silenciosos | Control sobre cada copia y cada barrera |
| Seguridad | Sin autenticación, cifrado ni validación | Sin superficie de amenaza en el alcance declarado |

Esta tabla responde a «¿por qué no se usa esto en producción para todo?».

---

## 9. Limitaciones

1. **Sin red física.** Todo se midió en loopback (S3). En un sistema real la red domina la
   latencia, y ninguna de estas cifras la incluye.
2. **Sin carga concurrente.** Closed-loop con una petición en vuelo (S2). Estas cifras son
   latencia en vacío, no latencia bajo carga.
3. **El factor B→D no es descomponible.** Las dos configuraciones difieren en transporte y
   lenguaje simultáneamente (§7.2). El estudio mide el efecto conjunto y no atribuye cuánto
   aporta cada causa.
4. **Sin afinidad de núcleo.** No disponible en la plataforma. En Linux los resultados de D
   probablemente tendrían mejor cola; **no lo afirmamos porque no lo medimos**.
5. **Precisión acotada por el hardware.** Las muestras de D están cuantizadas en 41,67 ns: es
   el piso físico del contador de la máquina, no una limitación del código. A esa escala el
   instrumento pesa lo mismo que lo medido (§6.1).
6. **Una sola máquina, un solo modelo de CPU.** Los factores relativos deberían mantenerse en
   otros equipos; los valores absolutos no.
7. **Dos corridas no bastan para caracterizar la cola de B.** Sabemos que su conteo de
   incumplimientos varía entre 0 y 136 según el estado de la máquina (§7.1), pero con dos
   observaciones no podemos dar ni una frecuencia esperada ni una cota. Lo que sí se sostiene es
   la afirmación negativa: **el cumplimiento de B no es una propiedad estable de su
   arquitectura.** Caracterizarlo exigiría muchas corridas en condiciones controladas.

### Trabajo futuro

- **Reintroducir un control que aísle una sola variable** (mismo transporte, otro lenguaje) para
  poder descomponer el factor de 162× — es la limitación nº 3.
- Repetir la variante Memoria compartida C en Linux con afinidad real de núcleo y comparar colas.
- Medir entre dos máquinas físicas para cuantificar cuánto aporta la red.
- Medir bajo carga concurrente, que es el escenario realista.

---

## 10. Anexos

### 10.1 Decisiones arquitectónicas registradas

| ADR | Decisión |
|---|---|
| **ADR-001** | Frontera de medición F1 — RTT de aplicación en el cliente |
| **ADR-002** | Variante Memoria compartida C: memoria compartida + espera activa, C11, QoS en lugar de afinidad |
| **ADR-003** | Resolución del reloj: enmienda a la especificación de medición |
| **ADR-004** | Dominio del reto: tabla de 16 hosts, payload de 32 B, tabla como archivo |
| **ADR-005** | Comparabilidad entre máquinas: una sola plataforma declarada |
| **ADR-006** | Concurrencia: un hilo por conexión, fuera de la ruta caliente; N=1 en el informe |
| **ADR-007** | Reducción del alcance a las variantes TCP Python y Memoria compartida C |

Los siete viven en `reto-latencia-group2/docs/ADR/`.

### 10.2 Reproducibilidad

```bash
cd reto-latencia-group2/sistema
./run.sh tcp-python 1 --warmup 100000 --iters 1000000    # TCP en Python   (repetir con 2 y 3)
./run.sh memoria-compartida-c 1 --warmup 100000 --iters 1000000    # memoria compartida en C
./analyze.py --md resultados/resultados-{B,D}-{1,2,3}.csv   # tabla comparativa
./graficas.py                                   # figuras SVG del informe
```

`run.sh` compila si hay `Makefile`, registra CPU, sistema operativo, núcleos, compilador y
runtime en el log, **archiva la corrida anterior en vez de pisarla** y ejecuta el mismo
analizador para todas las configuraciones.

Para comprobar que el experimento sigue siendo válido antes de creerse cualquier número:

```bash
cd reto-latencia-group2 && python3 verificar.py
```

### 10.3 Evidencia

| Entregable del enunciado | Ubicación |
|---|---|
| 1 · Código fuente | `reto-latencia-group2/` completo |
| 2 · Documentación técnica | este documento, §§ 2–5 |
| 3 · Logs de ejecución | `reto-latencia-group2/sistema/resultados/ejecucion-{B,D}-{1,2,3}.log` |
| 4 · Informe de resultados vs 1 ms | este documento, §§ 6–8 |
| 5 · Video ≤ 5 min o demo en vivo | guion en `GUION-VIDEO.md` |

Muestras crudas: `reto-latencia-group2/sistema/resultados/resultados-{B,D}-{1,2,3}.csv`
(3 000 000 de filas por variante). Las corridas anteriores no se borran: `run.sh` las mueve a
`resultados/archivo/` con su fecha.
