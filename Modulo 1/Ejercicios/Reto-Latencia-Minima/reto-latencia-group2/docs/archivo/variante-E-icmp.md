> **DOCUMENTO ARCHIVADO.** El código que produjo estas mediciones fue eliminado del
> árbol el 16/09/2026 al reducir el alcance de la entrega a las variantes B y D
> (ver `docs/ADR/ADR-007-reduccion-de-alcance.md`).
>
> - **Qué era:** Variante E — ICMP echo, en `sistema/variante-E-icmp/`.
> - **Por qué se conserva este texto:** las mediciones son reales, fueron tomadas el
>   10/09/2026 sobre el equipo de referencia y sostienen conclusiones del informe.
>   El código se borró; el hallazgo no.
> - **Cómo recuperar el código:** `git log --all -- "sistema/variante-E-icmp/"` y `git checkout <sha> -- "sistema/variante-E-icmp/"`.
>
---

# Variante E — ICMP echo · la idea del equipo, hecha bien

> **Esta variante NO cumple el enunciado. Ese es exactamente su valor.**

En la reunión del 13/09 el equipo propuso construir el sistema con `ping`: listas de
hosts, y medir tiempos de respuesta. La propuesta no podía aceptarse como sistema. Pero
la intuición era buena, y aquí está medida en vez de descartada.

---

## Por qué ICMP no puede ser el sistema

El enunciado exige un sistema que *«escuche permanentemente»* y *«retorne una respuesta
específica»*. En ICMP **quien escucha y responde es el kernel del sistema operativo.**

Consecuencia concreta, visible en el código: esta variante **no clasifica**. El kernel
devuelve el payload verbatim porque no ejecuta nuestro código. No hay veredicto
LOCAL/EXTERNO/DESCONOCIDO, no hay arquitectura propia que diseñar y no hay herramientas
que justificar — que es el entregable 2.

```text
  A, B, C, D                          E
  ┌────────┐      ┌────────┐          ┌────────┐      ┌─────────────┐
  │cliente │─────▶│SERVIDOR│          │cliente │─────▶│   KERNEL    │
  │        │◀─────│ nuestro│          │        │◀─────│  del SO     │
  └────────┘      └────────┘          └────────┘      └─────────────┘
                   clasifica                           devuelve el eco tal cual
                   ✅ es un sistema                     ❌ no hay sistema nuestro
```

## Por qué un socket propio y no el comando `ping`

Invocar `/sbin/ping` por iteración paga un `fork`+`exec`: **1–5 ms solo en arrancar el
proceso.** Eso es la frontera **F4** que [ADR-001](../ADR/ADR-001-frontera-de-medicion.md)
descarta por medir el lanzador de procesos en vez del sistema.

Con `SOCK_DGRAM + IPPROTO_ICMP` la frontera sigue siendo **F1**, igual que A, B, C y D, y
los números son comparables. No requiere root en macOS; en Linux depende de
`net.ipv4.ping_group_range` (el programa lo dice si falla).

---

## Resultados — Apple M4, macOS 26.6, arm64

### El hallazgo principal: la herramienta era el cuello de botella

| Medición del **mismo** ICMP al **mismo** destino (127.0.0.1) | p50 |
|---|---|
| Comando `ping` (lo que midió el equipo) | **111 µs** *(min 78 · máx 132)* |
| Socket ICMP propio, frontera F1 | **9,7 µs** |
| **Factor** | **≈ 12×** |

El equipo midió 38–107 µs y concluyó que ICMP local costaba eso. **No estaban midiendo
ICMP: estaban midiendo el comando `ping`** — su arranque, su formateo de salida y su
cadencia entre paquetes.

> **[REC] Este es el mismo error de capa que el estudio ya había encontrado una vez.**
> Frente al requisito de latencia, el reflejo fue «usemos un lenguaje más rápido» y la
> medición demostró que el lenguaje pesaba un 9 % y el transporte un 91 %. Aquí el reflejo
> fue «ICMP es lento» y la medición demuestra que lo lento era la herramienta.
> **Dos veces, la intuición apuntó a la capa equivocada. Esa repetición es el argumento
> del informe, no una anécdota.**

### ICMP en loopback contra las demás variantes

| | p50 | p90 | p99 | p90/p50 |
|---|---|---|---|---|
| **D** memoria compartida | 0,08 µs | 0,08 | 0,08 | 1,0× |
| **E** ICMP *(kernel)* | **9,7 µs** | 10,9 | 11,9 | **1,1×** |
| **Bc** TCP en C | 11,5 µs | 13,7 | 15,7 | 1,2× |
| **B** TCP en Python | 13,4 µs | 14,0 | 17,0 | 1,0× |

**ICMP en loopback es más rápido que TCP en C** (9,7 vs 11,5 µs, ≈1,2×). La razón es
arquitectónica y no de optimización: en TCP el kernel tiene que **despertar el proceso
servidor** —una operación del planificador— y en ICMP responde él mismo sin salir del
kernel. Eso pone precio a una frontera de proceso: **~1,8 µs por cruce**.

> Es el mismo eje que separa D de las demás, un escalón más abajo: D elimina el kernel,
> E elimina el proceso de usuario, B y Bc pagan los dos. Cada capa que desaparece tiene
> su precio en otro atributo — y el de E es que deja de ser un sistema propio.

### Línea base de red real — `--destino 1.1.1.1`

| | valor | vs. objetivo de 1 ms |
|---|---|---|
| p50 | **16 984 µs** (17 ms) | **17× por encima** ❌ |
| p99.9 | 52 111 µs (52 ms) | 52× por encima ❌ |
| muestras > 1 ms | **300 de 300** | incumple siempre |

**Esta es la barra que hace honesto el informe.** Todas las demás mediciones ocurren en
un solo host, sin red física: el supuesto **S3** del diseño. Medir en loopback elimina la
red, que en un sistema real es el componente dominante.

```text
  0,08 µs  █                                    D · memoria compartida
   9,7 µs  ███                                  E · ICMP (kernel)
  11,5 µs  ███▌                                 Bc · TCP en C
  13,4 µs  ████                                 B · TCP en Python
   111 µs  ███████                              comando `ping`
 ─────────────────────────── 1 ms ── OBJETIVO DEL ENUNCIADO ───────────────
 16 984 µs  █████████████████████████████████   E-0 · red real a internet
```

> El sistema está **12 000× por debajo** del objetivo; internet está **17× por encima**.
> Los dos extremos en la misma gráfica, con la línea del enunciado en medio, es la
> diapositiva del video.

---

## Uso

```bash
make
./client --destino 127.0.0.1 --warmup 2000 --iters 50000 --out salida.csv
./client --destino 1.1.1.1   --warmup 20   --iters 300 --timeout-ms 3000 --out base.csv

# o por el harness (sin servidor: no hay ninguno que levantar)
../run.sh E 1 --destino 127.0.0.1 --warmup 2000 --iters 50000
```

## Limitaciones declaradas

- **Sin pérdida de paquetes en loopback**, pero contra internet ICMP puede filtrarse o
  despriorizarse. `--timeout-ms` cuenta los fallos y los reporta.
- **La latencia a internet depende de la conexión del momento.** No es una propiedad del
  sistema: es contexto. Por eso es *línea base* y no variante, y por eso `n=300` basta.
- `--destino` acepta solo IPv4 literal, no nombres: resolver DNS metería una consulta de
  red en la ruta de medición.
