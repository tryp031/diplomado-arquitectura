# ADR-006 — Concurrencia: un hilo por conexión, y por qué D no puede tenerla

- **Estado:** Propuesta · pendiente de aceptación del equipo
- **Fecha:** 2026-09-15
- **Decide:** Group 2 (Freddy Aparicio · Camilo Céspedes · Daniel Mazo)
- **Origen:** solicitud del equipo en la reunión del 15/09 — *"agregar paralelismo y abrir
  otro hilo después de x número de peticiones; mostrar si está corriendo varios hilos y
  cantidad de lotes procesando"*
- **Depende de:** [ADR-001](ADR-001-frontera-de-medicion.md) (frontera F1) ·
  [ADR-002](ADR-002-variante-D-memoria-compartida.md) (memoria compartida) ·
  [ADR-005](ADR-005-comparabilidad-entre-maquinas.md) (comparabilidad)

---

## Contexto

Hasta el 15/09 el sistema se medía en el caso **más favorable que existe**: un cliente,
un servidor, cero contención. Ninguna cifra del informe decía qué pasa cuando hay más
de un cliente, y el servidor de la variante B ni siquiera podía aceptarlos —`listen(1)`
y un bucle de `accept()` secuencial—.

Eso es un hueco real: en producción la latencia sin contención es la que nunca se
observa.

---

## Decisión 1 — Un hilo por conexión, no un hilo cada X peticiones

La solicitud del equipo pedía abrir un hilo **cada X peticiones**. Se implementa en su
lugar **un hilo por conexión**, por tres razones:

| | hilo cada X peticiones | hilo por conexión |
|---|---|---|
| **Causa** | un umbral elegido por nosotros | hay un cliente más que atender |
| **Reproducibilidad** | el número de hilos depende de cuándo se mire | determinado por la carga |
| **Como experimento** | el parámetro flota → el resultado no se puede repetir | N es el parámetro, se fija por corrida |

En un experimento el parámetro **se fija, no se deja flotar**. Con un barrido controlado
(N = 1, 2, 4, 8, una corrida por nivel) sale una curva interpretable y repetible; con un
autoescalado sale un número que depende del instante en que se observó.

El objetivo que el equipo perseguía —ver el sistema abrir hilos y procesar en paralelo—
se cumple igual: al subir N, el servidor abre N hilos y la interfaz los muestra.

## Decisión 2 — La frontera de medición no cambia

El hilo se crea en `accept()`, **fuera de la ruta caliente**. El bucle de intercambio es
byte por byte el mismo de antes.

**Control ejecutado** (no supuesto), 60 000 iteraciones, equipo de referencia:

| | p50 |
|---|---|
| Histórico (servidor de un solo hilo, 9,15 M muestras) | 13,4 µs |
| Servidor multihilo, **N=1** | **13,54 µs** |

**1 % de diferencia.** Las mediciones anteriores siguen siendo válidas: son el punto
N=1 de la curva.

## Decisión 3 — El progreso se reporta entre lotes

Mostrar avance exige actualizar un contador, y un contador dentro del bucle medido es
trabajo que se cronometra junto con el intercambio: **la medición no puede pagar por su
propia barra de progreso**.

Las iteraciones se agrupan en lotes. El cronómetro sigue midiendo cada intercambio por
separado —F1 intacta—; el contador se toca entre lote y lote. Es la misma técnica de
lotes de `control-dominio/micro.c`, aplicada a otro fin.

El plano de control lee esos contadores y muestra hilos activos y lotes procesados.
Sigue sin cronometrar nada: observa, no mide.

---

## Resultado — la curva de degradación (variante B)

60 000 iteraciones por hilo, equipo de referencia:

| Clientes | p50 | p99 | p99,9 | vs. objetivo 1 ms |
|---|---|---|---|---|
| 1 | 13,54 µs | 29,54 µs | 51,67 µs | ✅ 19× por debajo |
| 2 | 15,62 µs | 42,46 µs | 61,33 µs | ✅ |
| 4 | 40,38 µs | 108,71 µs | 185,04 µs | ✅ |
| 8 | 88,50 µs | 314,33 µs | 460,12 µs | ✅ 2,2× por debajo |

**El objetivo se sigue cumpliendo con 8 clientes concurrentes**, pero el margen cae de
19× a 2,2×. De 1 a 8 clientes, el p50 se multiplica por 6,5 y la cola p99,9 por 8,9: la
cola se degrada **más rápido** que la mediana, que es el comportamiento que hace peligroso
dimensionar un sistema por su promedio.

Parte de esa degradación es del lenguaje: B está en Python y el GIL serializa el
procesamiento aunque haya un hilo por conexión. El control `Bc` (mismo transporte, en C)
permitiría separar cuánto es del transporte y cuánto del intérprete — **medición pendiente,
no hecha**.

---

## Por qué la variante D no admite concurrencia

D no se extiende a varios clientes, y **no por falta de tiempo**.

Su servidor tiene **una sola ranura**: un par `peticion.seq` / `respuesta.seq` en la
región compartida, con espera activa sobre él. Un segundo cliente exigiría o bien N
ranuras con reparto, o bien un turno entre clientes — es decir, **sincronización**.

Y la sincronización es exactamente lo que D eliminó para llegar a 83 ns. Sumado a que
cada cliente en espera activa ocupa un núcleo entero sin cederlo nunca, N clientes sobre
un equipo de 10 núcleos se pelean por CPU antes de pelearse por la ranura.

> **La arquitectura más rápida en aislamiento es la que peor escala, y por la misma razón
> que la hace rápida.** Los 83 ns no son gratis: se pagan con exclusividad —un cliente, un
> núcleo dedicado, cero sincronización—. D no es «mejor» que B: es una respuesta distinta
> a una pregunta distinta.

Esto no es un defecto que corregir. Es **el trade-off central del informe**, y solo se
vuelve visible cuando se intenta la concurrencia.

---

## Consecuencias

**A favor**

- El informe pasa de «cuánto tarda» a «cómo se degrada», que es la pregunta de arquitectura.
- Se descubrió y corrigió una condición de carrera latente: los buffers `buf`/`vista`/`resp`
  del servidor B eran compartidos. Con hilos, dos clientes se habrían pisado la respuesta
  —sin error, devolviendo el veredicto de otro—.
- Lo que el equipo pidió ver (hilos y lotes) queda visible, y sale de la medición real.

**En contra, y hay que decirlo**

- Solo la variante B tiene concurrencia. La curva no es comparable entre variantes.
- El servidor B multihilo es otro programa que mantener; A y C tendrán que decidir si
  replican el patrón.
- Con concurrencia el número de núcleos domina el resultado: ADR-005 pasa de recomendable
  a imprescindible.
- `Bc` en C sin medir deja abierta la pregunta de cuánto de la degradación es del GIL.

**Alcance declarado:** esto mide la degradación de B bajo carga concurrente. No es un
estudio de throughput ni de saturación: no se buscó el punto de quiebre ni se midió
peticiones por segundo.
