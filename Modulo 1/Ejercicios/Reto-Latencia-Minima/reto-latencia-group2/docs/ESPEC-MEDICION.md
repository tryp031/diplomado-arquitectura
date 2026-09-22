# Especificación de medición — común a todas las variantes

> **Estado: BORRADOR.** Debe congelarse por acuerdo del equipo antes de implementar.
> Esta es la decisión arquitectónica central del reto: el enunciado exige como entregable la
> *"explicación de cómo se mide la latencia"*.

---

## 1. Definición de la magnitud medida

**Latencia = tiempo de ida y vuelta (RTT) en espacio de usuario de la aplicación cliente.**

```text
        proceso CLIENTE                         proceso SERVIDOR
        ───────────────                         ────────────────
  t0 ──▶ marca de tiempo
         escritura del estímulo  ──────────────▶ lectura
                                                 (respuesta fija, sin lógica)
         lectura de la respuesta ◀────────────── escritura
  t1 ──▶ marca de tiempo

        latencia = t1 - t0
```

**Frontera declarada:** `t0` se toma inmediatamente **antes** de la llamada de escritura;
`t1` inmediatamente **después** de que la respuesta esté completamente leída en el cliente.
Incluye serialización, transporte y cambios de contexto. **No** incluye establecimiento de
conexión (se hace una vez, en el warmup) ni arranque del proceso.

> Esta frontera es una **decisión**, no un hecho. Justificarla en el informe: es la que
> corresponde a lo que percibe un consumidor real del servicio.

## 2. Protocolo experimental

| Parámetro | Valor | Por qué |
|---|---|---|
| Modo | **Closed-loop, 1 petición en vuelo** | Mide tiempo de servicio en vacío, sin encolamiento. Evita *coordinated omission*. |
| Warmup | 100 000 iteraciones, **descartadas** | Estabiliza cachés, JIT, TLB, ramp-up de frecuencia de CPU |
| Medición | 1 000 000 iteraciones | Suficiente para un p99.99 con sentido estadístico |
| Payload del estímulo | Fijo, **32 bytes** | Idéntico en todas las variantes o la comparación no vale |
| Payload de la respuesta | Fijo, **32 bytes** | Ídem |
| Reloj | Monótono, **máxima resolución de la plataforma** ⚠️ | Ver **enmienda** más abajo. macOS `clock_gettime_nsec_np(CLOCK_UPTIME_RAW)` · Linux `clock_gettime(CLOCK_MONOTONIC)` · `System.nanoTime()` · `time.perf_counter_ns()`. **Nunca** reloj de pared |
| Almacenamiento de muestras | Array **preasignado**, volcado al final | Escribir a disco o asignar memoria dentro del bucle contamina la medición |
| Rondas | 3 ejecuciones independientes | Detecta variación entre corridas |

> ### ⚠️ Enmienda pendiente de aprobación — el reloj (2026-09-10)
>
> La redacción original decía «resolución de ns» y nombraba `CLOCK_MONOTONIC` en primer lugar.
> **Eso confundía las unidades del valor con la granularidad con que el reloj avanza.**
> Medido en el M4: `CLOCK_MONOTONIC` avanza a saltos de **1000 ns**, mientras el contador de
> hardware da **41,67 ns**. La variante Memoria compartida C mide ~70 ns: con el reloj original, el 97,6 % de sus
> muestras salían **cero**.
>
> Regla propuesta: **la granularidad del reloj debe ser al menos 10× menor que el p50 esperado**;
> si no lo es, la variante añade un contraste por lotes como medida *secundaria*. Cada variante
> verifica y reporta su granularidad real y el sobrecoste del par de lecturas.
>
> **No afecta a A, B ni C** — `time.perf_counter_ns()` ya usa el contador de hardware en macOS.
> Justificación completa y consecuencias en
> [`ADR-003`](ADR/ADR-003-resolucion-del-reloj.md).

## 3. Métricas obligatorias

Reportar **siempre**, por variante:

```text
n · mín · p50 · p90 · p99 · p99.9 · p99.99 · máx · desviación estándar
```

**Prohibido reportar el promedio como métrica principal.** En sistemas de baja latencia el
promedio esconde exactamente lo que importa: la cola. Se puede incluir, pero nunca como titular.

Adjuntar además un **histograma** por variante (log-log o escala lineal recortada en p99.9).

## 4. Condiciones del entorno — registrar en el informe

- Modelo de CPU, número de núcleos, frecuencia base y turbo
- Sistema operativo y versión de kernel
- RAM
- Si se fijaron hilos a núcleos (*pinning*) y cómo
- Si se desactivaron estados de ahorro de energía / turbo boost
- Carga del sistema durante la medición (idealmente máquina en reposo)
- Versión de compilador / runtime y flags de optimización

**La ronda final de las 4 variantes debe ejecutarse en una única máquina.** Si se corre en
equipos distintos, los números no son comparables y el estudio pierde su tesis.

## 5. Trampas conocidas — declarar cómo se evitó cada una

| Trampa | Qué la causa | Cómo se evita |
|---|---|---|
| **Coordinated omission** | Medir solo lo que el sistema alcanzó a atender, ignorando el retraso acumulado | Closed-loop con 1 en vuelo, o registrar el tiempo previsto de envío |
| Promedio en vez de percentiles | Comodidad | Percentiles obligatorios |
| Sin warmup | Cachés fríos, JIT sin compilar, CPU en baja frecuencia | 100 k iteraciones descartadas |
| Asignación de memoria en el bucle caliente | GC o `malloc` en la ruta medida | Buffers y array de muestras preasignados |
| Nagle activo | El kernel agrupa paquetes pequeños → picos de ~40 ms | `TCP_NODELAY` en todas las variantes TCP |
| Reloj de pared | Salta con NTP y ajustes horarios | Reloj monótono |
| Escribir logs dentro del bucle | La E/S domina la medición | Volcar al final |
| Medir el arranque del proceso | Contamina las primeras muestras | Conexión establecida en el warmup |
| Una sola corrida | La varianza entre corridas se oculta | 3 rondas independientes |

## 6. Formato de salida — común a las 4 variantes

CSV de muestras crudas, una por línea, para que el análisis sea idéntico en todas:

```csv
iteracion,latencia_ns
1,23417
2,21980
...
```

Nombre de archivo: `resultados-<variante>-<ronda>.csv` (p. ej. `resultados-tcp-python-1.csv`).
El análisis (percentiles + histograma) lo hace **un solo script compartido** sobre estos CSV.
Así ninguna variante puede "calcular sus percentiles a su manera".

## 7. Lo que hay que acordar antes de codificar

- [ ] ¿Se acepta la frontera de medición de la sección 1?
- [ ] ¿Payload de 32 bytes o otro tamaño?
- [ ] ¿Quién implementa el script de análisis compartido?
- [ ] ¿En qué máquina se corre la ronda final?
- [ ] ¿Repositorio Git compartido? ¿Dónde?
- [ ] ¿Se fijan hilos a núcleos? (afecta mucho a la variante Memoria compartida C)
      → **Resuelto por la plataforma: NO SE PUEDE.** En macOS/arm64 `thread_policy_set`
      devuelve `KERN_NOT_SUPPORTED` (verificado 10/09). Solo queda la clase de QoS, que es
      una sugerencia al planificador. Si se consigue una máquina Linux para la ronda final,
      la respuesta cambia. Ver ADR-002.
- [ ] ¿Se acepta la **enmienda del reloj** (ADR-003) antes de congelar?
- [ ] ¿Se acepta la **frontera F1** tal como la fija ADR-001?
