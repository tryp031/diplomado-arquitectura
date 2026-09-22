# TCP Python — servidor y cliente sobre TCP crudo

**Implementación de referencia del reto.** Es el punto de comparación contra el que se mide
todo lo demás, y la plantilla de la que salió el bucle de medición de las demás variantes.

Documenta: **Freddy Aparicio** (asignado el 15/09, ADR-007).

## Uso

```bash
# corrida completa, la que sostiene el informe
../run.sh tcp-python 1 --warmup 100000 --iters 1000000

# corrida corta de prueba
../run.sh tcp-python 9 --warmup 20000 --iters 100000

# a mano, servidor y cliente por separado
python3 server.py --port 9101 --tabla ../tabla-hosts.csv
python3 client.py --port 9101 --tabla ../tabla-hosts.csv --iters 50000 --out /tmp/x.csv
```

Corre en cualquier sistema con Python 3: macOS, Linux, WSL2 y **Windows nativo**. Es el
único sistema del reto que no necesita compilador — por eso es también el que sirve para
desarrollar en cualquier máquina. Medir, en cambio, solo vale en el equipo de referencia
(ADR-005).

## Qué hace

Recibe 32 bytes con el identificador de un host y devuelve 32 bytes con un veredicto:
`LOCAL`, `EXTERNO` o `DESCONOCIDO`, según `../tabla-hosts.csv`.

```text
cliente                          servidor
   │  32 B  host_id + seq   ──────▶  │
   │                                 │  clasificar(host_id)  ← 16 comparaciones, sin E/S
   │  ◀────── 32 B  veredicto + eco  │
```

La respuesta **depende del estímulo**: eso es lo que distingue este sistema de un eco puro,
y es lo que se agregó el 14/09 para tener algo que demostrar (ADR-004).

## Las cuatro decisiones que explican la latencia

| Decisión | Qué pasa sin ella |
|---|---|
| **`TCP_NODELAY`** | Sin desactivar Nagle, el kernel agrupa paquetes pequeños y aparecen picos de **decenas de milisegundos**. Es el error clásico de este reto. |
| **Conexión persistente** | El *handshake* se pagaría en cada iteración, y se estaría midiendo `connect()`, no el intercambio. Se paga una vez, en el warmup, fuera de F1 (ADR-001). |
| **`recv_into` sobre buffer preasignado** | Cada `recv()` normal asigna un objeto nuevo: memoria por iteración dentro de la ruta caliente. |
| **`pack_into` sobre `bytearray`** | La respuesta se escribe en sitio, sin construir un `bytes` nuevo en cada vuelta. |

Y una que no es del transporte sino de Python: `dict.get` se enlaza a una variable local
antes del bucle, para no pagar una búsqueda de atributo por iteración. En C esto no
existiría; aquí se nota.

## La frontera de medición

```python
t0 = time.perf_counter_ns()   # justo ANTES de escribir
sock.sendall(msg)
# ... leer hasta completar los 32 B ...
t1 = time.perf_counter_ns()   # justo DESPUÉS de tener la respuesta entera
```

`t1 - t0` es el RTT en espacio de usuario. **No incluye** el establecimiento de la conexión
ni el arranque del proceso. Reloj monótono, nunca el de pared (ADR-003).

## Concurrencia — `--hilos N`

Un hilo por conexión, creado en `accept()`, es decir **fuera de la ruta caliente**. Con un
solo cliente el bucle es byte por byte el mismo de antes, y por eso el histórico sigue
siendo comparable: `N=1` es el punto N=1 de la curva, no otra medición.

Cada hilo tiene **sus propios buffers**. Compartirlos no daría error: daría respuestas
cruzadas de vez en cuando —un cliente recibiendo el veredicto de otro—, que es peor que
fallar. Ver ADR-006.

**Este es el único sistema del reto que admite concurrencia.** Memoria compartida no puede:
tiene una sola ranura por sentido.

## Resultados — corrida oficial del 17/09/2026

3 rondas × 1 000 000 de iteraciones = 3 M de muestras. Apple M4 · macOS 26.6 · arm64.

| | valor |
|---|---|
| p50 | 13 458 ns |
| p99.9 | 116 209 ns |
| máximo | 13 649 750 ns |
| muestras > 1 ms | **136** de 3 000 000 |

### Cómo leer estos números

**El objetivo del enunciado se cumple en la mediana y en el p99,9, y NO en el máximo.**
116 µs de p99,9 están holgadamente por debajo del milisegundo; 136 muestras lo superan, y
la peor llega a 13,6 ms — mil veces la mediana.

Esas 136 muestras son el resultado más interesante del sistema, por esto:

| Corrida | muestras > 1 ms (de 3 M) |
|---|---|
| 14/09 | **0** |
| 17/09 | **136** |

**Mismo código, misma máquina.** Lo único que cambió fue el estado del sistema operativo.
La conclusión que sostiene el informe es que el cumplimiento de este sistema **depende del
estado del SO, no de su arquitectura**: no hay nada en el diseño que acote el peor caso,
porque cada intercambio atraviesa el planificador y la pila de red.

## Contra Memoria compartida C

| | TCP Python | Memoria compartida C |
|---|---|---|
| p50 | 13 458 ns | 83 ns |
| > 1 ms | 136 / 3 M | 0 / 3 M |
| Concurrencia | sí | no |
| Portabilidad | cualquier SO con Python | POSIX, sin afinidad garantizada |

El factor es **162×**. **Matiz obligatorio al citarlo:** entre los dos sistemas cambian *el
transporte y el lenguaje a la vez*, así que ese 162× **no es atribuible a ninguno de los dos
por separado**. El control que sí los separaba (`Bc`, TCP en C) se midió y se retiró del
alcance con ADR-007; su hallazgo queda en `docs/archivo/control-Bc-tcp-c.md` y **no sustenta
ninguna conclusión vigente**.

Lo que sí se puede afirmar: este sistema paga dos llamadas al sistema por intercambio y
memoria compartida no paga ninguna. Esa es la diferencia estructural, y es la razón de que
su peor caso sea de milisegundos.

## Archivos

| | |
|---|---|
| `server.py` | escucha, clasifica y responde. Un hilo por conexión. |
| `client.py` | el medidor. **Es la plantilla**: las demás variantes copian este bucle. |

El clasificador **no se reimplementa aquí**: viene de `../clasificador.py`, que es el mismo
dominio que usa `../clasificador.h` en C. Que los dos coincidan lo comprueba `verificar.py`
con 20 casos; si dejaran de coincidir, los dos sistemas harían trabajos distintos y la
comparación no significaría nada.
