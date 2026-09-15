# Qué sistema construir — menú de opciones para el equipo

> Para discutir en el grupo y elegir. 10/09/2026.
> **[DIP]** contenido del diplomado · **[COMP]** conocimiento complementario · **[REC]** mi
> recomendación como arquitecto, discutible.
>
> El enunciado deja libre casi todo: *«cada estudiante elige herramientas, lenguajes o
> metodologías»*. Eso significa que **la elección es parte de lo que se califica** — el
> entregable 2 pide explícitamente justificarla.

---

## Parte 1 — El mecanismo de comunicación

Es el eje real del reto. Todas las opciones cumplen los tres requisitos del enunciado
(escuchar permanentemente · responder algo específico · medir el tiempo). La diferencia es
**cuánta pila de sistema atraviesa cada mensaje**, y eso es lo que fija la latencia.

```text
  más capas = más latencia, más interoperabilidad
  ┌──────────────────────────────────────────────────────────────────┐
  │  HTTP/REST → gRPC → WebSocket → TCP crudo → Unix socket → UDP    │
  │      → tubería con nombre → memoria compartida → misma función   │
  └──────────────────────────────────────────────────────────────────┘
  menos capas = menos latencia, nada de interoperabilidad
```

### Opciones, de la más convencional a la más extrema

| # | Mecanismo | RTT esperado | Dificultad | Qué demuestra |
|---|---|---|---|---|
| **1** | **HTTP/1.1 (REST)** | 50–200 µs | baja | La línea base «así se hace normalmente». Cuánto cuesta un protocolo de aplicación de texto + framework |
| 2 | **gRPC / HTTP/2** | 30–90 µs | media | Protocolo **binario** con multiplexación. El punto medio realista de la industria |
| 3 | **WebSocket** | 20–70 µs | baja | Conexión persistente sobre HTTP. Es lo que usan los sistemas web que necesitan latencia |
| **4** | **TCP crudo + `TCP_NODELAY`** ✅ *hecho* | 12–13 µs | baja | Cuánto cuesta el protocolo de aplicación: se quita HTTP y queda solo el transporte |
| **5** | **Unix domain socket** | 8–20 µs | baja | Cuánto cuesta la **pila de red**: mismo modelo de sockets, sin IP ni TCP |
| 6 | **UDP en loopback** | 10–25 µs | baja | Cuánto cuesta la **fiabilidad**: sin conexión, sin orden, sin reintentos |
| 7 | **Tubería con nombre (FIFO) o cola POSIX** | 10–30 µs | baja | Otro mecanismo del sistema operativo, sin sockets |
| **8** | **Memoria compartida + espera activa** ✅ *hecho* | 60–90 ns | **alta** | El límite físico entre procesos: cero llamadas al sistema |
| 9 | **Llamada a función en el mismo proceso** | 1–5 ns | trivial | **El piso teórico.** Ver nota abajo: es la opción más provocadora del menú |

✅ = ya implementado y medido por Daniel (`harness/variante-B-tcp/`, `harness/variante-D-shm/`,
más el control `control-Bc-tcp-c/` que separa el efecto del lenguaje del efecto del transporte).

### Las tres que faltan por repartir

**[REC]** Con B y D hechas, las que más aportan al estudio son:

| Variante | Mecanismo | Puerto | Por qué esta |
|---|---|---|---|
| **A** | HTTP/1.1 REST | 9100 | Es el extremo superior y **el más importante del informe**: es lo que construiría cualquiera por defecto. Sin A no se puede decir «la opción simple ya cumple el umbral» |
| **C** | Unix domain socket **o** UDP | 9102 | Aísla la pila de red. Con A, B y D ya medidas, es la que cierra el rango |
| **E** *(opcional)* | Función en el mismo proceso | — | 20 líneas. Da el piso teórico y hace la pregunta interesante del informe |

### Nota sobre la opción 9 — la más provocadora

Medir una llamada a función en el mismo proceso da **1–5 nanosegundos**, y obliga a una
pregunta que el informe se ahorraría de otro modo:

> *Si el objetivo es latencia mínima, ¿por qué hay dos procesos? Un solo proceso es
> 20 000 veces más rápido que el mejor mecanismo entre procesos.*

La respuesta es que el requisito real nunca es «latencia mínima» a secas: es latencia mínima
**con aislamiento entre componentes**, o **con posibilidad de desplegar por separado**, o **con
tolerancia a que uno falle**. Todo eso son atributos de calidad que el enunciado no menciona y
que en un sistema real sí existen.

**[REC]** Cuesta veinte líneas, se mide con el mismo harness, y convierte el informe de «medimos
transportes» en «entendimos qué se está comprando al separar procesos». Es la aplicación más
pura de la primera ley del módulo: *todo es un trade-off*.

### Lenguajes — cada uno elige, y hay que justificarlo

**[DIP]** El enunciado exige justificar el lenguaje. **[REC]** Y hay un dato propio que hace
esa justificación fácil: **medimos el mismo TCP en Python y en C, y la diferencia fue del 9 %**,
mientras cambiar de mecanismo dio 144×.

> **Conclusión para el equipo: elijan el lenguaje que dominen.** Está medido que no es la
> variable que importa. Lo único donde sí importa es la variante 8 (memoria compartida), porque
> ahí el sobrecoste del intérprete es mayor que la latencia a medir.

| Lenguaje | Sirve para | Aviso |
|---|---|---|
| **Python** | 1, 2, 3, 4, 5, 6, 7, 9 | El más cómodo. Ya hay plantilla de medición lista |
| **Java** | 1, 2, 3, 4, 5, 6 | `System.nanoTime()` sirve. El recolector de basura mete ruido en los percentiles altos — **eso es material para el informe, no un problema** |
| **Node.js** | 1, 2, 3, 4, 6 | Natural para WebSocket |
| **Go** | 1, 2, 3, 4, 5, 6 | Buen equilibrio; hay que instalarlo |
| **C / C++** | todas, imprescindible en la 8 | Ya está `clang` en la máquina de Daniel |

---

## Parte 2 — Qué representa el sistema

El enunciado dice *«ante un estímulo (por ejemplo, un mensaje cualquiera), el sistema responda
con otro mensaje (por ejemplo, "respuesta")»*. **El dominio está abierto.** Esto no cambia la
latencia, pero sí cambia el informe y el video.

### Opción 2.A — Eco puro *(lo que hay hoy)*

32 bytes entran, 32 bytes salen. Literal al enunciado, cero riesgo, cero narrativa.

- ✅ Es exactamente lo que se pide. Nadie puede objetar nada.
- ✅ No introduce ninguna variable que contamine la medición.
- ❌ El informe no puede responder a *«¿y para qué sirve bajar de 1 ms?»*.

### Opción 2.B — Ruta crítica de una decisión de trading **[REC]**

El estímulo es un **tick de mercado** (símbolo + precio, 32 bytes binarios). La respuesta es una
**decisión**: `COMPRAR` / `VENDER` / `NADA`, según un umbral precargado en memoria. 32 bytes.

```text
   32 B entrada                                    32 B salida
   ┌──────────────────────┐                    ┌──────────────────┐
   │ símbolo │ precio     │ ──▶ una comparación │ decisión │ ref   │
   └──────────────────────┘      contra umbral  └──────────────────┘
                                  (~1 ns)
```

- ✅ **Responde a por qué el requisito existe.** Sub-milisegundo no es un capricho: en trading
  de baja latencia es la diferencia entre ejecutar y no ejecutar.
- ✅ **Encaja con el perfil del docente** — arquitecto del sector financiero, event-driven.
  *(Esto es lectura del contexto, no del material: el temario no menciona trading.)*
- ✅ Cuesta **una comparación de números**: ~1 ns, cuatro órdenes de magnitud por debajo de lo
  que medimos. No distorsiona nada, y se puede demostrar que no distorsiona.
- ✅ Mismos 32 bytes en ambos sentidos → **las mediciones ya hechas siguen siendo válidas en
  forma**; solo hay que rehacerlas, y una ronda tarda segundos.
- ⚠️ **La lógica tiene que ser idéntica en las cuatro variantes**, sin asignación de memoria y
  sin ramas costosas. Si una variante hace algo distinto, la comparación se rompe.
- ❌ Añade una variable que hay que declarar y controlar. Más honesto, pero más trabajo.

### Opción 2.C — Sensor → actuador (control industrial)

El estímulo es una lectura de sensor; la respuesta, un comando de actuador con umbral de
seguridad. Mismo coste que 2.B.

- ✅ Igual de realista, y el argumento de latencia es aún más intuitivo: un freno, una parada
  de emergencia.
- ❌ Más lejos del sesgo del curso (banca, AWS, event-driven).

### Opción 2.D — Autorización contra una tabla en memoria

El estímulo es un token; la respuesta, permitido/denegado, buscando en un arreglo precargado.

- ✅ Muy común en la vida real (validación de sesión en la ruta crítica).
- ⚠️ **Una búsqueda no es O(1) constante:** los fallos de caché meten varianza en los
  percentiles altos, y eso **sí** contamina la comparación de transportes. Como estudio de
  caché sería interesante; como dominio para este reto, estorba.

### **[REC]** Mi recomendación sobre el dominio

**2.B, con una condición:** que se mantenga como **una sola comparación numérica**, sin
asignación de memoria, idéntica en las cuatro variantes, y que el informe **demuestre** que su
coste es despreciable (medir el bucle con y sin la comparación, y reportar la diferencia).

Si el equipo prefiere no asumir esa variable, **2.A es perfectamente defendible** — es literal
al enunciado — y el «para qué sirve» se puede resolver con un párrafo de contexto en el informe
en lugar de con código.

> **Lo que NO recomiendo en ningún caso:** añadir lógica de negocio real, serialización JSON,
> validación de esquemas o acceso a datos. Cualquiera de esas cosas pasa a dominar la medición
> y el estudio deja de medir transportes.

---

## Parte 3 — Lo que hay que evitar

**[DIP]** El módulo penaliza conceptualmente la sobreingeniería. Aquí está medible:

| Tentación | Por qué no |
|---|---|
| Docker / contenedores | Añaden red virtualizada: **suben** la latencia. Y el enunciado no pide portabilidad de despliegue |
| Kafka, RabbitMQ, un broker | Un salto de red más persistencia: tres órdenes de magnitud en contra |
| Framework web pesado en las variantes rápidas | Capas de indirección en la ruta crítica |
| Base de datos | No hay nada que persistir |
| TLS / autenticación | El enunciado no declara superficie de amenaza. Añade handshake y cifrado por mensaje |
| Kubernetes, balanceador, service mesh | No hay concurrencia ni múltiples instancias |
| JSON como formato del mensaje | Serializar y parsear cuesta más que el transporte en las variantes rápidas. Binario de tamaño fijo |
| Perseguir el número más bajo posible | **Es el error del ejercicio.** La nota está en la metodología y en el análisis del trade-off |

---

## Parte 4 — Qué necesita quien tome una variante

Nada que no esté listo. El harness común ya está probado:

```bash
git clone <repo>            # cuando exista (T04)
cd harness
cat README.md               # el contrato: 4 requisitos, nada más
cp variante-B-tcp/client.py variante-A-http/client.py   # plantilla de medición
# cambiar SOLO el transporte
./run.sh A 1 --iters 100000
```

**Las cuatro reglas del contrato** (están en `harness/README.md`):

1. Interfaz de línea de comandos fija: `--host --port --payload --warmup --iters --out`
2. Salida exacta: CSV `iteracion,latencia_ns`
3. El bucle de medición **se copia**, no se reinventa: `t0` antes de escribir, `t1` después de
   leer la respuesta completa, reloj monótono, array preasignado, volcado al final
4. Lenguaje libre — pero hay que justificarlo (media página, entregable 2)

Lo que **no** hay que hacer: calcular tus propios percentiles. `analyze.py` es único, y por eso
los cuatro resultados son comparables.

---

## Para pegar en el grupo

```text
Equipo, les paso el menú de opciones para que elijan. Dos decisiones separadas:

1) EL MECANISMO (de aquí sale la latencia)

   HTTP/REST         50-200 µs   fácil     ← la línea base "así se hace normalmente"
   gRPC / HTTP2      30-90 µs    media     ← protocolo binario, el punto medio de la industria
   WebSocket         20-70 µs    fácil     ← conexión persistente sobre HTTP
   TCP crudo         12-13 µs    fácil     ← YA HECHO
   Unix socket       8-20 µs     fácil     ← quita la pila de red
   UDP               10-25 µs    fácil     ← quita la fiabilidad
   Memoria compartida  60-90 ns  difícil   ← YA HECHO
   Función local     1-5 ns      trivial   ← el piso teórico, 20 líneas

   Faltan por tomar: HTTP/REST (la más importante del informe) y Unix socket o UDP.

   Sobre el LENGUAJE: elijan el que dominen. Medimos el mismo TCP en Python y en C y la
   diferencia fue del 9%, mientras cambiar de mecanismo dio 144x. Está medido que el
   lenguaje no es la variable que importa.

2) QUÉ REPRESENTA EL SISTEMA (el enunciado lo deja abierto)

   a) Eco puro: 32 bytes entran, 32 bytes salen. Literal al enunciado, cero riesgo.
   b) Tick de mercado -> decisión COMPRAR/VENDER/NADA con un umbral en memoria.
      Cuesta UNA comparación (~1 ns), no distorsiona la medición, y responde a la
      pregunta que el informe si no se ahorra: ¿para qué sirve bajar de 1 ms?
      Además encaja con el perfil del profe (arquitecto del sector financiero).

   Yo me inclino por (b) pero es debatible, y (a) es perfectamente defendible.

Lo que NO deberíamos hacer, por si a alguien se le ocurre: Docker, Kafka, base de datos,
JSON, TLS. Todo eso SUBE la latencia y el módulo penaliza la sobreingeniería. El sistema
es un eco: no necesita nada de eso.

¿Qué toman? Con que me digan el mecanismo me basta, el lenguaje lo eligen ustedes.
```
