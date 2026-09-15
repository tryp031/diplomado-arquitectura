# ADR-004 — El dominio del sistema: clasificación de hosts contra listas

- **Estado:** Propuesta · pendiente de aceptación del equipo
- **Fecha:** 2026-09-14
- **Decide:** Group 2 (Freddy Aparicio · Camilo Céspedes · Daniel Mazo)
- **Sustituye a:** la opción «eco puro» (2.A de `OPCIONES-SISTEMA.md`), vigente hasta el 11/09
- **Depende de:** [ADR-001](ADR-001-frontera-de-medicion.md) (frontera F1) ·
  [ADR-003](ADR-003-resolucion-del-reloj.md) (granularidad del reloj)

---

## Contexto

El enunciado deja el dominio abierto: *«ante un estímulo (por ejemplo, un mensaje
cualquiera), el sistema responda con otro mensaje (por ejemplo, "respuesta")»*. Hasta el
11/09 el sistema era un **eco puro**: 32 bytes entran, los mismos 32 bytes salen.

En la reunión del equipo del 13/09 surgió otra propuesta: **listas blancas y negras de
hosts** — dado un host, decir si es local o externo, y mostrar tiempos de respuesta. La
propuesta venía acompañada de un mecanismo concreto: usar `ping`.

### Lo que no se podía aceptar de la propuesta original

| Problema | Consecuencia |
|---|---|
| `ping` usa ICMP: **quien escucha y responde es el kernel**, no un proceso nuestro | El enunciado exige un sistema propio que *«escuche permanentemente»* y *«retorne una respuesta específica»*. No habría arquitectura que diseñar ni herramientas que justificar (entregable 2) |
| Invocar el binario `ping` por iteración paga `fork`+`exec`: **1–5 ms** | Es la frontera **F4** que ADR-001 descarta: mediría el lanzador de procesos, no el sistema |
| Los tiempos de la propuesta (38–107 µs en local, ~40 ms a internet) | Entre **3× y 480 000× peores** que lo ya medido. Y 40 ms es **40× por encima** del objetivo de 1 ms |

### Lo que sí valía

La intuición **local vs. externo** apunta justo al supuesto **S3** del diseño —medir en
loopback elimina la red, que en un sistema real domina la latencia—, que es la
declaración más honesta de todo el trabajo. Y una clasificación contra una tabla es un
dominio legítimo, **si** se implementa de forma que no contamine la medición.

## Decisión

**Se adopta la clasificación de hosts como dominio del sistema.** El estímulo deja de ser
un mensaje arbitrario y pasa a ser un identificador de host; la respuesta deja de ser un
eco y pasa a ser un veredicto.

```text
ESTÍMULO — 32 B                            RESPUESTA — 32 B
┌────────┬────────┬──────────────┐         ┌──────────┬────────┬────────────┐
│host_id │  seq   │   relleno    │   ──▶   │veredicto │host_id │  relleno   │
│ 4 B    │  4 B   │    24 B      │         │   1 B    │  4 B   │   27 B     │
└────────┴────────┴──────────────┘         └──────────┴────────┴────────────┘
 IPv4, orden de red                         LOCAL(1) / EXTERNO(0) / DESCONOCIDO(2)
```

**Mismo tamaño en ambos sentidos que el eco puro.** No cambia el transporte, no cambia la
frontera F1, no cambia el harness. Solo cambia qué significan los bytes.

Se rechaza `ping` como mecanismo. Se conserva ICMP **como línea base medida con socket
propio** (variante E), precisamente para demostrar por qué no servía.

### Las cinco condiciones que hacen defendible la decisión

Sin ellas el dominio contaminaría la medición y el estudio comparativo se rompería.

1. **Una sola fuente de verdad.** La tabla vive en `harness/tabla-hosts.csv` y todas las
   variantes la cargan. Nunca se duplica en código. Mismo argumento que `analyze.py`
   (atributo AC-3): si cada variante define su tabla, la comparación B vs Bc deja de
   aislar el lenguaje y pasa a mezclar «lenguaje» con «dos tablas que divergieron».
2. **Límite duro de 16 entradas.** 16 × 4 B = **64 B = una línea de caché**. La tabla vive
   en L1 permanentemente y no falla nunca. Este límite es la decisión, no un detalle:
   subirlo invalida este ADR.
3. **Tiempo constante.** El barrido recorre siempre las 16 ranuras, sin salida anticipada
   y sin ramas dependientes del dato. Verificado en el ensamblador generado: **16 `csel`,
   cero saltos condicionales** (`cc -O2 -S`, arm64).
4. **Ciclo de estímulos preconstruido.** Los 16 estímulos se arman antes del bucle y se
   recorren con `i & 15` — un AND, no un módulo. Mezcla en el bucle medido:
   **10 LOCAL · 6 EXTERNO · 0 DESCONOCIDO**, declarada aquí. Que falte DESCONOCIDO no
   sesga nada *porque* la condición 3 se cumple; se ejercita en la autoprueba de arranque.
5. **La tabla se carga de un archivo, nunca de constantes en el código.** Ver §6.

## Consecuencias

### Lo que mejora

- **La respuesta ahora es «específica» en el sentido literal del enunciado.** Con el eco
  puro la respuesta era constante e independiente del estímulo. Ahora depende de él.
- **El informe puede responder «¿para qué sirve bajar de 1 ms?»** sin un párrafo de
  relleno: hay un caso de uso — autorización en la ruta crítica — con código.
- **Hay algo que demostrar en vivo** (entregable 5): `demo.py` es la CLI que el equipo
  dibujó en sus notas, funcionando contra el sistema real.
- **La decisión es del equipo**, no impuesta. Con tres personas y quince días, eso importa.

### Lo que cuesta

- **Hubo que reejecutar las 9 M de muestras** de B, Bc y D. Coste real: ~15 min de máquina.
- **Dos corridas de control adicionales** que antes no hacían falta (§5).
- **Una asimetría entre lenguajes que hay que declarar:** en C el clasificador es un
  barrido de tiempo constante (~1,9 ns); en Python es un `dict` (~40 ns). No son el mismo
  algoritmo. Se acepta porque replicar el barrido en Python costaría ~2 µs —el 15 % del
  p50 de B— y *eso* sí contaminaría. Consecuencia honesta: **Python no puede ofrecer la
  garantía de tiempo constante que sí ofrece C.** Es un trade-off del lenguaje, y es
  material del informe.

### Lo que se sacrificó, y por qué

| Alternativa | Por qué no |
|---|---|
| **Eco puro** (statu quo) | Cero riesgo y literal al enunciado, pero el informe no puede responder para qué sirve el requisito. Sigue siendo una opción defendible: si el equipo prefiere no asumir la variable, se vuelve a él sin perder nada del estudio |
| **Regla RFC 1918** (rangos privados con máscaras, sin tabla) | Más barata (3 comparaciones, sin memoria). Se descarta porque una *regla* no admite excepciones: no puede expresar «este host público es de confianza». Una *lista* es política auditable y modificable sin tocar la lógica. **Es un trade-off real, no una preferencia: la regla gana en coste, la lista gana en expresividad** |
| **`ping` / ICMP como sistema** | Ver §Contexto. Conservado como línea base (variante E) |
| **Tabla grande con hash** | Fallos de caché → varianza en los percentiles altos → contamina la comparación de transportes, que es el objeto del estudio |

## 5. Verificación — el coste medido, no supuesto

El enunciado pide como entregable *«explicación de cómo se mide la latencia»*. Afirmar
«clasificar es despreciable» sin medirlo sería exactamente lo que este trabajo critica.

### Primer método, y por qué se descartó

Medir a través del RTT: variante D con y sin clasificador, y restar.

| | mediana por lotes, 3 rondas |
|---|---|
| D con clasificador | 64 · 67 · 64 ns |
| D sin clasificador | 63 · 63 · 76 ns |

**El método no puede resolver el efecto.** La varianza entre rondas (±13 ns) es mayor que
lo que se busca (~2 ns). Una primera pareja de corridas dio 7 ns de diferencia que al
repetir se disolvió: era ruido presentado como señal.

> Este fallo va al informe. Un método incapaz de resolver el efecto que mide produce
> números, no resultados — y desde fuera nadie lo habría detectado.

### Segundo método — aislar (`harness/control-dominio/`)

Microbenchmark del clasificador solo: sin sockets, sin memoria compartida, sin
planificador. Técnica de lotes (ADR-003), contra un bucle de referencia idéntico sin la
llamada, con acumulador `volatile` para que el optimizador no borre el bucle.

| | ns por llamada |
|---|---|
| Bucle de referencia | 0,27 |
| Bucle con `clasificar()` | 2,14 |
| **Coste del clasificador** | **≈ 1,9** (1,55 · 1,87 · 1,87) |

| Frente a | Peso |
|---|---|
| Variante D (64 ns) | **3 %** |
| Control Bc (12 000 ns) | 0,016 % |
| Granularidad del reloj (41,67 ns) | por debajo de un tic |

**Conclusión:** el dominio no altera ninguna conclusión del estudio; el factor transporte
(~144×) es dos órdenes de magnitud mayor. **Matiz obligatorio:** en D es el 3 %, no cero.
A 64 ns nada es gratis.

## 6. Trampa verificada — no convertir la tabla en constantes

Comprobado con `cc -O2 -S` en Apple Silicon:

| Cómo se conoce la tabla | Qué emite el compilador |
|---|---|
| Cargada de `tabla-hosts.csv` en ejecución | **16 `csel`, 0 saltos.** El barrido existe. Correcto |
| Conocida en tiempo de compilación | `cmp w0,#0 ; csel` — **el clasificador desaparece del binario** |

Si alguien «simplifica» esto poniendo las IPs como literales, la corrida de control
mediría **cero** y la conclusión «clasificar es despreciable» sería un artefacto del
optimizador. El experimento se invalidaría en silencio.

> **Es un ejemplo medible de que la frontera del sistema medido no la fija el código
> fuente, sino el código después del compilador.** Mismo tipo de hallazgo que ADR-003
> (el reloj que no alcanzaba al fenómeno) y que la descomposición lenguaje/transporte.

## Trazabilidad

| Requisito | Cómo lo satisface esta decisión |
|---|---|
| D3 — «retornar una respuesta específica» | El veredicto depende del estímulo; el eco puro no dependía |
| D5 — justificar herramientas y metodología | §Decisión, §5 y §6 son esa justificación |
| AC-1 — latencia p99.9 < 1 ms | +1,9 ns sobre 64 ns: no compromete el objetivo |
| AC-2 — determinismo | Tiempo constante verificado: el veredicto no cambia la latencia |
| AC-3 — comparabilidad | Una sola tabla para todas las variantes |
| AC-4 — trazabilidad | `control-dominio/` es reproducible y está versionado |

## Referencias

- `Modulo 1/Ejercicios/Reto-Latencia-Minima/harness/clasificador.h` · `clasificador.py`
- `harness/tabla-hosts.csv` — la tabla
- `harness/control-dominio/` — el microbenchmark y su README
- `harness/demo.py` — la demostración en vivo
- `harness/variante-E-icmp/` — ICMP como línea base
