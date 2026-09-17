# Control del dominio — ¿cuánto cuesta clasificar?

**Pregunta:** el dominio (ADR-004) mete una búsqueda en tabla dentro de la ruta caliente.
¿La contamina?

Afirmar «es despreciable» sin medirlo es exactamente lo que el enunciado señala como
entregable 2: *«explicación de cómo se mide la latencia»*. Así que se mide.

## Primer intento — y por qué falló

Medirlo a través del RTT: correr la variante D con y sin clasificador y restar.

| | mediana por lotes |
|---|---|
| D con clasificador | 64 · 67 · 64 ns |
| D sin clasificador | 63 · 63 · 76 ns |

**No sirve.** La varianza entre rondas (±13 ns) es mayor que el efecto que se busca
(~2 ns). Una primera pareja de corridas dio una diferencia de 7 ns que al repetir se
disolvió: era ruido, no señal.

> **[REC] Esto va al informe tal cual.** Un método que no puede resolver el efecto que
> mide produce números, no resultados. Reportar aquellos 7 ns como «el coste del
> clasificador» habría sido un error de método que nadie habría detectado desde fuera.

## Segundo intento — aislar

`micro.c` saca el clasificador del RTT y lo mide solo: sin sockets, sin memoria
compartida, sin planificador. Técnica de lotes (ADR-003): un par de llamadas al reloj
cada 100 000 iteraciones, porque a 2 ns por llamada el reloj (41,67 ns de granularidad)
no puede cronometrar una llamada individual.

Se mide contra un bucle de referencia idéntico **sin** la llamada, y se resta. El
acumulador es `volatile` para que el optimizador no borre el bucle — sin eso se mediría
un bucle vacío.

```bash
make && ./micro ../tabla-hosts.csv
```

## Resultado — Apple M4, macOS 26.6, arm64, clang -O2

| | ns por llamada |
|---|---|
| Bucle de referencia | 0,27 |
| Bucle con `clasificar()` | 2,14 |
| **Coste del clasificador** | **≈ 1,9** (1,55 · 1,87 · 1,87 en tres rondas) |

## Qué significa

| Frente a | Peso del clasificador |
|---|---|
| Variante D (p50 83 ns) | **2,3 %** |
| Variante B (p50 13 458 ns) | **0,014 %** |
| Granularidad del reloj (41,67 ns) | **por debajo de un solo tic** |

**Conclusión:** el dominio no cambia ninguna conclusión del estudio. El salto de B a D
(162×) es dos órdenes de magnitud mayor que este efecto.

**Y el matiz honesto:** en D es el 3 %, no cero. A 64 ns ya nada es gratis. Decir
«despreciable» sin el número sería la misma clase de afirmación sin respaldo que el
informe critica en otros sitios.

---

# Tercera pregunta — ¿cuesta lo mismo decir LOCAL que decir EXTERNO?

`veredicto.c`, añadido el 15/09.

**De dónde salió la pregunta.** Al probar la lista negra desde la interfaz, un host
bloqueado respondía tan rápido como uno permitido. La reacción natural es sospechar
que la lista negra no está haciendo nada. Es al revés: es la propiedad buscada,
funcionando.

`clasificador.h` **afirma** ser de tiempo constante — recorre siempre las 16 ranuras,
sin salida anticipada. Este programa lo **mide**. Afirmar no es medir: esa distinción
es la que obligó a escribir `micro.c`, y vale igual aquí.

## Resultado

```text
    veredicto        p50 (ns)   p99 (ns)
    LOCAL               2.208      2.321
    EXTERNO             2.201      2.318
    DESCONOCIDO         2.201      2.396

    diferencia máxima entre veredictos:                0.007 ns
    dispersión dentro de un mismo veredicto (p99-p50): 0.195 ns
```

**Indistinguibles.** Los tres veredictos se separan entre sí **28 veces menos** que lo
que varía uno solo al repetirse. La diferencia atribuible al veredicto es más pequeña
que el ruido del propio veredicto: no se puede afirmar que exista.

## El criterio, y por qué no es un umbral inventado

No se compara contra un número elegido a dedo —eso sería decidir el resultado antes de
medirlo—. Se comparan **dos dispersiones**: cuánto se separan los veredictos entre sí,
contra cuánto se mueve uno solo entre rondas. Si lo primero es menor que lo segundo,
no hay señal. Es exactamente el razonamiento que invalidó el primer intento de
`micro.c`, donde 7 ns de «coste del clasificador» resultaron ser varianza.

## Qué aporta al informe

Dos conclusiones independientes que apuntan a la misma propiedad:

1. **Metodológica.** La latencia no depende del dato. Dos corridas con distinta mezcla
   de IPs dan el mismo número, así que la comparación entre transportes no está
   contaminada por qué se preguntó.
2. **De seguridad.** No hay **canal lateral temporal**: midiendo el tiempo de respuesta
   no se puede deducir si un host está en la lista negra. En un control de acceso real
   —el escenario que declara `tabla-hosts.csv`— eso sería una fuga de información.

Esto es lo que hace que la lista negra valga como parte del dominio y no como adorno:
sin ella no habría dos veredictos que contrastar, y la propiedad no sería demostrable.

## Por qué aislado y no por RTT

El efecto buscado es de ~2 ns. El RTT de la variante más rápida es 83 ns; el de B,
13 400 ns. Medirlo por RTT repetiría el error ya documentado arriba: la varianza entre
rondas se traga la señal y se reporta ruido como resultado.
