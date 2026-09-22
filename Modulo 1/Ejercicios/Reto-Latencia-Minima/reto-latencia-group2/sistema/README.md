# Harness común — Reto de Latencia Mínima (Group 2)

**Este harness elimina el cuello de botella: ya está probado y funcionando.** Las variantes A, C y D
pueden empezar a implementarse en paralelo desde ahora, sin esperar a nadie.

La regla es una sola: **ninguna variante calcula sus propias métricas.** Todas producen CSV crudo
y `analyze.py` lo interpreta. Así los cuatro resultados son comparables por construcción, no por
buena voluntad.

---

## Cómo se usa

```bash
cd sistema
./run.sh tcp-python 1                   # variante TCP Python, ronda 1, por defecto
./run.sh tcp-python 1 --warmup 20000 --iters 100000   # corrida corta de prueba
./run.sh memoria-compartida-c 1         # variante Memoria compartida C
./analyze.py --md resultados/*.csv      # tabla comparativa final

# Demostración en vivo — servidor aparte, NUNCA el cliente medidor
python3 tcp-python/server.py --port 9101 &
python3 demo.py --variante tcp-python
```

`run.sh` levanta el servidor, corre el cliente, baja el servidor, analiza y registra en el log
el CPU, el SO, los núcleos y la versión del runtime (ESPEC §4 lo exige en el informe).

**Variantes compiladas:** si el directorio de la variante tiene `Makefile`, `run.sh` compila
antes de medir y usa los binarios `server`/`client`; si no, usa `server.py`/`client.py`. Así
nunca se mide un binario obsoleto y el lenguaje sigue siendo libre por variante.

## Estructura

```text
sistema/
├── README.md            ← este archivo: el contrato
├── analyze.py           ← ÚNICO script de métricas. No tocar por variante.
├── run.sh               ← orquestador de una corrida
├── tcp-python/             ← TCP en Python · referencia — documenta Freddy
│   ├── server.py
│   └── client.py        ← plantilla del bucle de medición
├── memoria-compartida-c/   ← memoria compartida en C11 — documenta Camilo
├── control-dominio/     ← CONTROL: cuánto cuesta clasificar (~1,9 ns)
├── tabla-hosts.csv      ← EL DOMINIO. Fuente única de verdad. No duplicar.
├── clasificador.h       ← el dominio en C      (D)
├── clasificador.py      ← el dominio en Python (B)
├── demo.py              ← DEMOSTRACIÓN EN VIVO (entregable 5). No sirve para medir.
├── reloj.h              ← instrumento compartido por las variantes compiladas
├── graficas.py          ← figuras SVG del informe, sin dependencias
├── visor/               ← visor estático de resultados
└── resultados/          ← CSV + logs de ejecución
```

> **Alcance: B y D.** Las variantes A y C nunca se implementaron; los experimentos `Bc`
> (TCP en C) y `E` (ICMP) se midieron y se retiraron el 16/09. Sus hallazgos están en
> [`../docs/archivo/`](../docs/archivo/) y el porqué en
> [ADR-007](../docs/ADR/ADR-007-reduccion-de-alcance.md).

---

## ⭐ EL DOMINIO — leer antes de implementar A o C

**Cambió el 14/09.** El sistema ya no es un eco puro: es un **clasificador de hosts**.
Decisión completa en [`ADR-004`](../docs/ADR/ADR-004-dominio-listas-de-hosts.md).

```text
ESTÍMULO — 32 B                            RESPUESTA — 32 B
┌────────┬────────┬──────────────┐         ┌──────────┬────────┬────────────┐
│host_id │  seq   │   relleno    │   ──▶   │veredicto │host_id │  relleno   │
│ 4 B    │  4 B   │    24 B      │         │   1 B    │  4 B   │   27 B     │
└────────┴────────┴──────────────┘         └──────────┴────────┴────────────┘
 IPv4 en orden de red                       LOCAL(1) · EXTERNO(0) · DESCONOCIDO(2)
```

Mismo tamaño en ambos sentidos que antes: **el transporte y la frontera F1 no cambian.**

### Lo único que tiene que hacer tu servidor

```python
from clasificador import cargar, VEREDICTO_DESCONOCIDO   # o #include "../clasificador.h"

tabla = cargar(ruta)          # UNA VEZ, al arrancar. NUNCA dentro del bucle.
...
host_id = leer_uint32(peticion, 0)
veredicto = tabla.get(host_id, VEREDICTO_DESCONOCIDO)
escribir(respuesta, veredicto, host_id)      # 1 B veredicto + eco del host_id
```

### Cuatro reglas del dominio — no negociables

| Regla | Por qué |
|---|---|
| **No copies la tabla a tu código.** Usa `clasificador.py` / `clasificador.h`, que leen `tabla-hosts.csv` | Si cada variante define su tabla, la comparación deja de aislar el transporte y pasa a mezclar «transporte» con «tablas que divergieron» |
| **Cárgala al arrancar, nunca en el bucle** | Abrir un archivo en la ruta caliente cuesta más que todo lo que estamos midiendo |
| **Devuelve el `host_id` como eco** | Es la verificación de integridad: sin ella no se distingue «la respuesta llegó» de «llegó basura» |
| **Nada de logs, red, disco ni asignación de memoria al clasificar** | Cualquiera de esas cosas domina la medición |

### Autoprueba obligatoria antes de medir

Tu cliente debe verificar los 16 hosts **más uno fuera de tabla** antes de la primera
muestra. Copia el bloque de `tcp-python/client.py`. Sin esto el harness puede estar
midiendo un transporte que transporta basura, y nadie se entera.

### El ciclo de estímulos

16 estímulos **preconstruidos antes del bucle**, recorridos con `i & 15` (un AND, no un
módulo). Mezcla medida: 10 LOCAL · 6 EXTERNO · 0 DESCONOCIDO. Que falte DESCONOCIDO no
sesga porque `clasificar` es de tiempo constante — verificado en ensamblador: 16 `csel`,
cero saltos condicionales.

### Coste del dominio, medido

| | ns/llamada |
|---|---|
| `clasificar()` en C | **≈ 1,9** |
| `dict.get` en Python | ≈ 40 |

3 % de la variante Memoria compartida C · 0,016 % de Bc. Método y por qué el primer método falló:
[`control-dominio/README.md`](control-dominio/README.md).

---

## Contrato que debe cumplir cada variante

Si tu variante cumple estas cuatro cosas, encaja con el resto sin coordinación adicional.

### 1. Interfaz de línea de comandos

**Servidor** — `server.py` (o el binario equivalente):

```
--host 127.0.0.1   --port <puerto propio>   --payload 32   --tabla <ruta al CSV>
```

**Cliente** — `client.py`:

```
--host 127.0.0.1   --port <puerto>   --payload 32   --tabla <ruta al CSV>
--warmup 100000    --iters 1000000   --out <ruta CSV>
```

`run.sh` pasa `--tabla` automáticamente. No lo codifiques por defecto en tu variante.

Puertos por variante para poder correrlas en paralelo: **A=9100 · B=9101 · C=9102 · D=9103**.
(E no usa puerto: responde el kernel.)

### 2. Formato de salida — exacto

```csv
iteracion,latencia_ns
1,23417
2,21980
```

Nombre: `resultados/resultados-<VARIANTE>-<RONDA>.csv`

### 3. El bucle de medición — copiar de `tcp-python/client.py`

No reinventarlo. Lo que **no** se negocia:

| Requisito | Por qué |
|---|---|
| `t0` justo antes de escribir, `t1` justo después de leer la respuesta completa | Es la frontera declarada (ESPEC §1). Cambiarla invalida la comparación. |
| Reloj **monótono** en ns | `perf_counter_ns` · `clock_gettime(CLOCK_MONOTONIC)` · `steady_clock` · `System.nanoTime()`. Nunca reloj de pared. |
| Warmup descartado (100 k) | Cachés, TLB, JIT, ramp-up de frecuencia de CPU. |
| Array de muestras **preasignado** | Asignar memoria en el bucle caliente contamina la medición. |
| Volcado a CSV **al final** | Escribir a disco dentro del bucle mide el disco, no el transporte. |
| Closed-loop, **1 petición en vuelo** | Evita *coordinated omission*. Y hay que declararlo en el informe. |
| Payload fijo de 32 B en ambos sentidos | Idéntico en las 4 variantes o no hay comparación. |

### 4. Lenguaje: libre

La referencia está en Python porque es la que todos tienen instalada, pero **el lenguaje es parte
de tu decisión técnica y hay que justificarla** (el enunciado lo pide explícitamente). Para la
variante Memoria compartida C, Python no va a llegar a nanosegundos: C, Rust, Go, Zig o Java son mejores candidatos.

Lo único que importa es que produzcas el mismo CSV.

---

## Resultados — 3 rondas × 1 M por variante (dominio de listas, ADR-004)

Agregado por variante. Microsegundos. El umbral se evalúa contra **p99.9**, no contra la media.

**Corrida oficial del 17/09** (la del informe), reproducible desde el árbol:

| | **D** shm | **B** Python+TCP |
|---|---|---|
| p50 | **0,083** | 13,46 |
| p99.9 | **0,167** | 116,2 |
| máx | 37,1 | 13 650 |
| **muestras > 1 ms** | **0** / 3 M | **136** / 3 M ❌ |

Corrida del 14/09, conservada en `resultados/archivo/` — mismo código, otro veredicto:

| | **D** shm | **B** Python+TCP |
|---|---|---|
| p50 | **0,08** | 13,33–13,46 |
| p99.9 | **0,12** | 20,67–38,96 |
| máx | 1,71–1,88 | 133–345 |
| **muestras > 1 ms** | **0** / 3 M | **0** / 3 M |

Archivadas — medidas de verdad, código retirado del árbol el 16/09 (ADR-007):

| | **E** ICMP *(línea base)* | **Bc** C+TCP *(control)* | **E-0** internet *(línea base)* |
|---|---|---|---|
| p50 | 9,62–10,00 | 11,54–11,62 | 16 984 |
| p99.9 | 13,88–14,83 | 18,79–30,12 | 52 111 |
| máx | 17,0–67,9 | 111–154 | 52 111 |
| **muestras > 1 ms** | **0** / 150 k | **0** / 3 M | **300** / 300 ❌ |

### Cinco lecturas

1. **El rango completo abarca seis órdenes de magnitud:** de 80 ns (memoria compartida) a
   17 ms (red real). La línea de 1 ms del enunciado cae entre las dos.
2. **Todo lo que corre en un solo host cumple el umbral con holgura.** El reto nunca
   estuvo en alcanzar el número.
3. **ICMP en loopback (9,7 µs) es MÁS RÁPIDO que TCP en C (11,5 µs).** No hay que
   despertar ningún proceso de usuario: responde el kernel. Es el único punto del estudio
   donde el respondedor no es código nuestro — y por eso mismo **no cumple el enunciado**
   (ver `../docs/archivo/variante-E-icmp.md`).
4. **El comando `ping` da 111 µs contra los 9,7 µs del mismo ICMP con socket propio: 12×.**
   La diferencia es la herramienta de medición, no el transporte.
5. **⚠️ El veredicto de B cambia entre corridas sin que el sistema cambie.** Ver el aviso
   siguiente. Es el hallazgo más importante del trabajo, y está en el informe §7.1.

> Las lecturas 3 y 4 salen de mediciones reales cuyo código se retiró del árbol con el
> ADR-007. Se conservan aquí como contexto del estudio; **el informe no se apoya en ellas.**

### ⚠️ La cola de B no es reproducible — ya es una conclusión del informe

Tres corridas del **mismo código**, con el mismo tamaño de muestra (3 M), sobre la misma
máquina. Muestras por encima de 1 ms en la variante TCP Python:

| Corrida | B | D | Evidencia |
|---|---|---|---|
| 10/09 | **363** | 0 | ❌ el log no se conservó — no se usa como evidencia |
| 14/09 | **0** | 0 | ✅ `resultados/archivo/` |
| 17/09 | **136** | 0 | ✅ `resultados/` — corrida oficial |

El sistema no cambió en nada que explique eso: el dominio añade 1,9 ns. Lo que cambió fue
**el estado de la máquina**.

> **Afirmar «esta arquitectura incumple 1 ms» a partir de una sola corrida es afirmar algo
> sobre la máquina, no sobre la arquitectura.** Lo correcto es reportar cuántas corridas se
> hicieron y el rango entre ellas, nunca un máximo suelto.
>
> Esto **refuerza** la tesis del trabajo —el entorno es una restricción arquitectónica de
> primer orden— y **ya está incorporado** al informe (§5.2, §6, §7.1 y limitación 7). La
> diferencia real entre las dos variantes no es que una sea lenta, sino que Memoria compartida C
> **saca de la ruta crítica las fuentes de variabilidad** —sin llamadas al sistema no hay
> planificador que intervenga— y TCP Python queda a merced de él.
>
> ⚠ **Eso no la acota.** El máximo de Memoria compartida C fue 37 µs, **447× su propia
> mediana**, sin una sola llamada al sistema. No se observaron muestras sobre 1 ms; no es lo
> mismo que no puedan ocurrir.

### Convención de rondas — cuáles entran en el informe

| Ronda | Qué es | ¿Entra en tablas y figuras? |
|---|---|---|
| **1, 2, 3** | Las del informe: 1 000 000 de iteraciones cada una | ✅ sí |
| 0 | Corridas de validación | ❌ no |
| 9 | Pruebas rápidas (20 000 iteraciones) | ❌ no |

`graficas.py` aplica este filtro. Hasta el 17/09 solo excluía la ronda 0: la 9 se colaba y las
figuras decían `n = 3 020 000` mientras la tabla del informe decía 3 000 000. No fallaba —
mentía en silencio, que es peor.

**Pendiente:** repetir bajo carga controlada para separar «el sistema tiene cola» de «la
máquina estaba ocupada». Es el experimento que falta.

### ⚠️ Pérdida de evidencia — 14/09

La remedición **sobrescribió los CSV y logs crudos del 10/09** antes de que `run.sh`
archivara. Se perdió el dato crudo de aquellas 9 M de muestras; sobreviven las cifras
resumidas en `DISENO-ARQUITECTURA.md §7 bis`, en este archivo y en `INFORME.md`, más
`resultados-tcp-python-0.csv` (08/09).

`run.sh` ya no sobrescribe: mueve lo anterior a `resultados/archivo/` con su fecha. **Los
resultados crudos son la evidencia del informe (AC-4); perderlos rompe la cadena.**

## ⚠️ Enmienda al reloj que afecta a todos — leer antes de implementar

`CLOCK_MONOTONIC`, que ESPEC §2 nombraba en primer lugar, **avanza a saltos de 1000 ns** en
macOS (medido). Para A, B y C da igual —`time.perf_counter_ns()` de Python ya usa el contador
de hardware de 41,67 ns—, pero la regla estaba mal escrita y se corrigió:
**verificar y reportar la granularidad real del reloj que use tu variante.**
Ver [`ADR-003`](../docs/ADR/ADR-003-resolucion-del-reloj.md).

## Siguientes pasos

- [x] ~~Rehacer la variante TCP Python en C~~ → medido 10/09, archivado en `docs/archivo/`
- [x] ~~Decidir el dominio~~ → ADR-004, clasificador de hosts, implementado y remedido
- [x] ~~Línea base de red real~~ → medida 13/09, archivada en `docs/archivo/`
- [x] ~~Demostración en vivo~~ → `demo.py`
- [x] ~~Reducir el alcance a B y D~~ → ADR-007, 16/09
- [ ] **Documentación técnica de la variante TCP Python — Freddy.**
- [ ] **Documentación técnica de la variante Memoria compartida C — Camilo.**
- [ ] **Repetir bajo carga controlada**, para separar «el sistema tiene cola» de «la
      máquina estaba ocupada». Es el experimento que sigue faltando.
- [ ] Congelar `../ESPEC-MEDICION.md` con las enmiendas de ADR-001, ADR-003 y ADR-004
- [ ] Repositorio Git compartido
- [ ] Repetir bajo carga controlada (ver aviso de reproducibilidad)
- [ ] Probar la compilación en Linux/x86 — solo se ha compilado en macOS/arm64
- [ ] Definir la máquina de la ronda final
