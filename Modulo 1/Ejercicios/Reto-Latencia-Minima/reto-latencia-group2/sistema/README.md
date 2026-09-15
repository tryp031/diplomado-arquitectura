# Harness común — Reto de Latencia Mínima (Group 2)

**Este harness elimina el cuello de botella: ya está probado y funcionando.** Las variantes A, C y D
pueden empezar a implementarse en paralelo desde ahora, sin esperar a nadie.

La regla es una sola: **ninguna variante calcula sus propias métricas.** Todas producen CSV crudo
y `analyze.py` lo interpreta. Así los cuatro resultados son comparables por construcción, no por
buena voluntad.

---

## Cómo se usa

```bash
cd harness
./run.sh B 1                            # variante B, ronda 1, valores por defecto
./run.sh B 1 --warmup 20000 --iters 100000   # corrida corta de prueba
./run.sh E 1 --destino 127.0.0.1        # línea base ICMP (sin servidor propio)
./analyze.py --md resultados/*.csv      # tabla comparativa final

# Demostración en vivo — servidor aparte, NUNCA el cliente medidor
python3 variante-B-tcp/server.py --port 9101 &
python3 demo.py --variante B
```

`run.sh` levanta el servidor, corre el cliente, baja el servidor, analiza y registra en el log
el CPU, el SO, los núcleos y la versión del runtime (ESPEC §4 lo exige en el informe).

**Variantes compiladas:** si el directorio de la variante tiene `Makefile`, `run.sh` compila
antes de medir y usa los binarios `server`/`client`; si no, usa `server.py`/`client.py`. Así
nunca se mide un binario obsoleto y el lenguaje sigue siendo libre por variante.

## Estructura

```text
harness/
├── README.md            ← este archivo: el contrato
├── analyze.py           ← ÚNICO script de métricas. No tocar por variante.
├── run.sh               ← orquestador de una corrida
├── variante-B-tcp/      ← IMPLEMENTACIÓN DE REFERENCIA (probada)
│   ├── server.py
│   └── client.py        ← plantilla del bucle de medición
├── variante-A-http/     ← por implementar
├── variante-C-ipc/      ← por implementar
├── variante-D-shm/      ← IMPLEMENTADA en C11 (Daniel) — ver su README
├── variante-E-icmp/     ← LÍNEA BASE: ICMP. Responde el KERNEL, no un proceso nuestro
├── control-Bc-tcp-c/    ← CONTROL: TCP en C. No es variante; aisla lenguaje vs transporte
├── control-dominio/     ← CONTROL: cuánto cuesta clasificar (~1,9 ns)
├── tabla-hosts.csv      ← EL DOMINIO. Fuente única de verdad. No duplicar.
├── clasificador.h       ← el dominio en C   (Bc, D, E)
├── clasificador.py      ← el dominio en Python (A, B)
├── demo.py              ← DEMOSTRACIÓN EN VIVO (entregable 5). No sirve para medir.
├── reloj.h              ← instrumento compartido por las variantes compiladas
└── resultados/          ← CSV + logs de ejecución
```

---

## ⭐ EL DOMINIO — leer antes de implementar A o C

**Cambió el 14/09.** El sistema ya no es un eco puro: es un **clasificador de hosts**.
Decisión completa en [`ADR-004`](../../../_Base-Conocimiento/ADR/ADR-004-dominio-listas-de-hosts.md).

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
muestra. Copia el bloque de `variante-B-tcp/client.py`. Sin esto el harness puede estar
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

3 % de la variante D · 0,016 % de Bc. Método y por qué el primer método falló:
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

### 3. El bucle de medición — copiar de `variante-B-tcp/client.py`

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
variante D, Python no va a llegar a nanosegundos: C, Rust, Go, Zig o Java son mejores candidatos.

Lo único que importa es que produzcas el mismo CSV.

---

## Resultados al 14/09 — 3 rondas × 1 M por variante (dominio de listas, ADR-004)

Agregado por variante. Microsegundos. El umbral se evalúa contra **p99.9**, no contra la media.

| | **D** shm | **E** ICMP *(línea base)* | **Bc** C+TCP *(control)* | **B** Python+TCP | **E-0** internet *(línea base)* |
|---|---|---|---|---|---|
| p50 | **0,08** | 9,62–10,00 | 11,54–11,62 | 13,33–13,46 | 16 984 |
| p99.9 | **0,12** | 13,88–14,83 | 18,79–30,12 | 20,67–38,96 | 52 111 |
| máx | 1,71–1,88 | 17,0–67,9 | 111–154 | 133–345 | 52 111 |
| **muestras > 1 ms** | **0** / 3 M | **0** / 150 k | **0** / 3 M | **0** / 3 M | **300** / 300 ❌ |

### Cinco lecturas

1. **El rango completo abarca seis órdenes de magnitud:** de 80 ns (memoria compartida) a
   17 ms (red real). La línea de 1 ms del enunciado cae entre las dos.
2. **Todo lo que corre en un solo host cumple el umbral con holgura.** El reto nunca
   estuvo en alcanzar el número.
3. **ICMP en loopback (9,7 µs) es MÁS RÁPIDO que TCP en C (11,5 µs).** No hay que
   despertar ningún proceso de usuario: responde el kernel. Es el único punto del estudio
   donde el respondedor no es código nuestro — y por eso mismo **no cumple el enunciado**
   (ver `variante-E-icmp/README.md`).
4. **El comando `ping` da 111 µs contra los 9,7 µs del mismo ICMP con socket propio: 12×.**
   La diferencia es la herramienta de medición, no el transporte.
5. **⚠️ Los máximos cambiaron radicalmente frente al 10/09 sin que el sistema cambiara.**
   Ver el aviso siguiente. Es el hallazgo más importante de esta ronda.

### ⚠️ Aviso de reproducibilidad — afecta a una conclusión del informe

El 10/09, con el eco puro y el mismo tamaño de muestra (3 M), B registró **363** muestras
por encima de 1 ms y Bc **141**. El 14/09, con 3 M de nuevo, **ambas registran 0**.

El sistema no cambió en nada que explique eso: el dominio añade 1,9 ns. Lo que cambió fue
**el estado de la máquina**.

> **Consecuencia para el informe:** la conclusión anterior —«B y Bc incumplen el umbral por
> el máximo»— **no era una propiedad de la arquitectura, sino del entorno durante aquella
> corrida.** Afirmar «esta arquitectura incumple 1 ms» a partir de una sola corrida es
> afirmar algo sobre la máquina, no sobre la arquitectura.
>
> Esto **refuerza** la tesis del trabajo (el entorno es una restricción arquitectónica de
> primer orden) y **obliga a reescribir** la conclusión 1 del informe. Lo correcto es
> reportar el rango entre rondas y el número de rondas, nunca un máximo suelto.

**Pendiente:** repetir bajo carga controlada para separar «el sistema tiene cola» de «la
máquina estaba ocupada». Es el experimento que falta.

### ⚠️ Pérdida de evidencia — 14/09

La remedición **sobrescribió los CSV y logs crudos del 10/09** antes de que `run.sh`
archivara. Se perdió el dato crudo de aquellas 9 M de muestras; sobreviven las cifras
resumidas en `DISENO-ARQUITECTURA.md §7 bis`, en este archivo y en `INFORME.md`, más
`resultados-B-0.csv` (08/09).

`run.sh` ya no sobrescribe: mueve lo anterior a `resultados/archivo/` con su fecha. **Los
resultados crudos son la evidencia del informe (AC-4); perderlos rompe la cadena.**

## ⚠️ Enmienda al reloj que afecta a todos — leer antes de implementar

`CLOCK_MONOTONIC`, que ESPEC §2 nombraba en primer lugar, **avanza a saltos de 1000 ns** en
macOS (medido). Para A, B y C da igual —`time.perf_counter_ns()` de Python ya usa el contador
de hardware de 41,67 ns—, pero la regla estaba mal escrita y se corrigió:
**verificar y reportar la granularidad real del reloj que use tu variante.**
Ver [`ADR-003`](../../../../_Base-Conocimiento/ADR/ADR-003-resolucion-del-reloj.md).

## Siguientes pasos

- [x] ~~Rehacer la variante B en C~~ → `control-Bc-tcp-c/`
- [x] ~~Decidir el dominio~~ → ADR-004, clasificador de hosts, implementado y remedido
- [x] ~~Línea base de red real~~ → `variante-E-icmp/`, ICMP loopback + internet
- [x] ~~Demostración en vivo~~ → `demo.py`
- [ ] **Implementar A (HTTP) — Freddy.** Puerto 9100. La más importante del informe
- [ ] **Implementar C (Unix socket) — Camilo.** Puerto 9102
- [ ] Congelar `../ESPEC-MEDICION.md` con las enmiendas de ADR-001, ADR-003 y ADR-004
- [ ] Repositorio Git compartido
- [ ] Repetir bajo carga controlada (ver aviso de reproducibilidad)
- [ ] Probar la compilación en Linux/x86 — solo se ha compilado en macOS/arm64
- [ ] Definir la máquina de la ronda final
