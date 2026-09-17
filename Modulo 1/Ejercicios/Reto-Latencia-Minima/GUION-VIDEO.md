# Guion del video — entregable 5 (máximo 5 minutos)

> El enunciado da a elegir: **video MP4 ≤ 5 min** para quien no asista al encuentro, o
> **demostración en vivo** para quien sí. §A es el guion del video; §B, el de la demo.
> Estado: borrador del 10/09/2026, con los datos de B, Bc y D. Actualizar al tener A y C.

---

> ⚠️ **Pendiente de revisar tras el ADR-007 (16/09).** El guion cita el control `Bc` y la
> variante `E`, que ya no están en el árbol. Sus mediciones siguen siendo válidas
> (`reto-latencia-group2/docs/archivo/`) pero no se reproducen en vivo. Ver también el draft
> de presentación en `Modulo 1/Aportes/danny/m1-presentacion-reto-latencia-danny.html`.

## Principio rector

**Cinco minutos no alcanzan para explicar el sistema. Alcanzan para defender una tesis.**

El error típico es narrar el recorrido: «primero probamos esto, luego aquello…». Eso consume
los cinco minutos sin llegar a ninguna afirmación. El video tiene **una** tesis:

> *El reto no estaba en bajar de 1 ms. Estaba en darse cuenta de en qué capa está el coste —y
> de que la métrica que se elige decide el veredicto.*

Todo lo que no sostenga esa frase, se corta. Incluido el código: **no se muestra código**.
Cinco minutos de un revisor no se gastan en leer C.

---

## A. Guion del video (4:40 de contenido, 20 s de margen)

### 0:00 – 0:30 · El planteamiento y el anticlímax

> **En pantalla:** el enunciado del reto, y debajo un único número: `13,2 µs`.

«El reto pedía un sistema que respondiera a un estímulo en menos de un milisegundo.

Lo primero que hicimos fue medirlo con la peor implementación que se nos ocurrió: un servidor
de eco en Python, sobre TCP. Mediana: **13 microsegundos**. Setenta y seis veces por debajo del
objetivo, con cuarenta líneas de código.

Así que el reto no era alcanzar el número. El número estaba alcanzado desde el principio. La
pregunta interesante era otra: **¿dónde está realmente el coste, y qué pasa si miramos bien?**»

### 0:30 – 1:10 · El diseño del experimento

> **En pantalla:** el diagrama de las cuatro capas de pila (A/B/C/D), apareciendo una a una.

«Montamos el mismo servicio sobre transportes distintos, midiendo todos exactamente igual.

La diferencia entre ellos es **cuánta pila de sistema atraviesa cada mensaje**: HTTP añade un
protocolo de aplicación; TCP crudo lo quita; un socket de dominio Unix quita la pila de red; y
memoria compartida con espera activa quita hasta las llamadas al sistema operativo.

Y añadimos algo que no es una variante sino un **control**: el mismo TCP, reescrito en C. Sin
él no podríamos separar el efecto del lenguaje del efecto del transporte, porque cambian los
dos a la vez.»

### 1:10 – 1:50 · Cómo se mide — la decisión central

> **En pantalla:** el diagrama de la frontera F1, con t0 y t1 marcados. Después, la tabla de
> las cinco fronteras posibles con sus valores (5 µs / 13 µs / 100 µs / 50 ms).

«Antes de medir hay que decidir **dónde se ponen las sondas**, y esa es la decisión
arquitectónica de verdad del ejercicio.

El mismo sistema, sin cambiar una línea, reporta entre 5 microsegundos y 50 milisegundos según
dónde empiece y termine el cronómetro.

Elegimos la frontera más desfavorable de las defendibles: desde justo antes de escribir hasta
tener la respuesta completa leída en el cliente. Es lo que percibe un consumidor real. Podríamos
haber reportado 5 microsegundos midiendo solo la llamada al sistema, y habría sido igualmente
cierto. No lo hicimos, y eso está documentado en un ADR antes de conocer los resultados.»

### 1:50 – 2:40 · Primer resultado: se optimizó la capa equivocada

> **En pantalla:** la tabla de descomposición. Los dos números grandes: **1,1×** y **144,6×**.

«Aquí está el primer resultado, y contradice el reflejo habitual.

Pasar de Python a C, con el mismo transporte, mejoró la mediana un **nueve por ciento**.
Cambiar el transporte, con el mismo lenguaje, la mejoró **ciento cuarenta y cuatro veces**.

El intérprete de Python cuesta 1,2 microsegundos por intercambio. Es real. Pero está sepultado
bajo los doce microsegundos que cuestan las dos llamadas al sistema, las copias del kernel y la
pila TCP — que C paga exactamente igual.

Ante un requisito de latencia, lo primero que se propone casi siempre es cambiar de lenguaje.
Los datos dicen que el noventa y uno por ciento del coste estaba en una **decisión de
arquitectura**, no en un detalle de implementación.

Con un matiz que hay que decir: este servicio no hace nada. Recibe treinta y dos bytes y
devuelve treinta y dos. Con lógica de negocio de por medio, la proporción cambia.»

### 2:40 – 3:40 · Segundo resultado: la métrica decide el veredicto

> **En pantalla:** la gráfica de percentiles, con la línea roja del milisegundo. Dejarla
> respirar: es la imagen del trabajo.

«Segundo resultado, y es el que responde a la pregunta del enunciado.

Por mediana, las tres configuraciones cumplen de sobra. Setenta y seis veces, ochenta y tres
veces, doce mil veces por debajo del milisegundo.

Pero miren la cola. De tres millones de mediciones, la versión en Python **se pasó del
milisegundo en trescientas sesenta y tres**. La de C, en ciento cuarenta y una. La de memoria
compartida, en ninguna.

Entonces, ¿el sistema cumple el objetivo? **Depende de qué signifique cumplir.** Si significa
que la respuesta típica tarda menos de un milisegundo, cumplen las tres. Si significa que nunca
tarda más, solo cumple una.

Un informe basado en promedios habría dado las tres por buenas. **No es el sistema el que
determina el veredicto: es la métrica que uno elige.**»

### 3:40 – 4:20 · Tercer resultado: lo que no se puede quitar

> **En pantalla:** `p50 = 83 ns` y debajo `máx = 34 833 ns`, con el factor `420×`.

«Y el tercero, que es el que más nos enseñó.

La versión de memoria compartida no hace **ni una sola llamada al sistema operativo**. Su
mediana son ochenta y tres nanosegundos. Y su máximo son treinta y cinco microsegundos:
cuatrocientas veinte veces la mediana.

Esa cola no la pone el software, porque ya no queda software que quitar. La ponen el
planificador del sistema operativo y el hardware. Intentamos fijar el hilo a un núcleo, que es
la técnica estándar para acotarla, y descubrimos que **en esta plataforma no existe**: la
llamada devuelve "no soportado".

O sea que el sistema operativo y el hardware no son un detalle de despliegue. Son una
**restricción arquitectónica de primer orden**, y aquí la pudimos medir en vez de solo
enunciarla.»

### 4:20 – 4:40 · Cierre

> **En pantalla:** la tabla de atributos sacrificados por la variante D.

«Para cerrar: la versión más rápida es también la peor arquitectura posible para casi cualquier
sistema real. No funciona entre máquinas, quema dos núcleos al cien por ciento sin hacer nada,
no es portable y no se puede depurar.

El umbral de un milisegundo lo cumple la opción más simple y más interoperable. Pasar de esa a
la extrema compra tres órdenes de magnitud que casi nadie necesita, al precio de todos los demás
atributos.

Concluir "usen memoria compartida" habría sido aprender a optimizar. La conclusión que nos
llevamos es otra: **todo es un trade-off, y la pregunta nunca es cuál es más rápida sino qué
atributo prioriza el negocio.**»

---

### Notas de producción

| | |
|---|---|
| Duración | 4:40 + margen. **Cronometrar el ensayo**: 5:01 no se acepta |
| Ritmo | ~140 palabras/minuto. El guion está calibrado para eso; si te sales, corta contenido, no aceleres |
| Qué NO mostrar | **Código.** Ni un archivo. También fuera: la estructura de carpetas y el proceso de trabajo |
| Qué SÍ mostrar | Los cuatro diagramas/tablas indicados y la gráfica de percentiles. Seis imágenes en total |
| Grabación | Pantalla + voz. No hace falta cámara |
| Herramienta | QuickTime (Cmd+Shift+5 en macOS) basta. No inviertas tiempo en edición |
| Ensayos | Dos. El primero sale largo siempre |

### Los cinco números que hay que decir bien

Si el revisor solo retiene cinco cosas, que sean estas:

1. **13 µs** — el objetivo estaba cumplido desde la primera implementación ingenua
2. **1,1× contra 144,6×** — lenguaje frente a arquitectura
3. **363 contra 0** — muestras por encima de 1 ms, de 3 millones
4. **420×** — la cola que queda cuando ya no hay software que quitar
5. **F1** — la frontera de medición se eligió y se documentó **antes** de ver los resultados

---

## B. Guion de la demo en vivo (encuentro del 15/09 o 29/09)

Si asistes, la demo sustituye al video. Cambia el formato, no la tesis.

### Preparación — antes de conectarte

- [ ] Binarios compilados: `cd harness && make -C variante-D-shm && make -C control-Bc-tcp-c`
- [ ] Una corrida de prueba completa, para que nada falle en vivo
- [ ] Dos terminales abiertas, fuente grande (≥ 18 pt)
- [ ] `INFORME.md` §6 y §7 abiertos en otra ventana, por si preguntan
- [ ] Las dos gráficas SVG abiertas en el navegador
- [ ] **Corridas cortas**: `--iters 100000`, no un millón. Un millón tarda y el público se pierde

### Secuencia (7–8 minutos con preguntas)

1. **Arranca el servidor D** y muestra que queda escuchando permanentemente. Menciona de paso
   que está consumiendo un núcleo entero sin hacer nada — engancha, y es honesto.
2. **Corre el cliente con 100 000 iteraciones.** Sale en segundos. Señala tres cosas de la
   salida: la verificación del reloj, la integridad 100 %, y el p50.
3. **Corre B** (la de Python) con los mismos parámetros. Contrasta las medianas en vivo.
4. **Cambia a la gráfica de percentiles.** Aquí está el discurso: por mediana todas cumplen,
   por cola no. Es el momento de la presentación.
5. **Cierra con la descomposición** 9 % contra 144×.

### Preguntas que van a salir — y la respuesta corta

| Pregunta | Respuesta |
|---|---|
| ¿Por qué en loopback y no en red? | Está declarado como supuesto S3. Con red la latencia la domina la red y no se vería la diferencia entre transportes, que es lo que el estudio quiere medir. Es una limitación reconocida, no un descuido. |
| ¿El máximo de 44 ms no invalida el resultado? | Al contrario: **es** el resultado. Y depende de cuánto se mida: con 100 000 muestras era 2,2 ms. Por eso se especifica en percentiles. |
| ¿Por qué C y no Rust o Go? | No están instalados en el equipo, y con el tiempo disponible añadir un toolchain era riesgo sin beneficio: el resultado no depende del lenguaje —lo demostramos con el control. |
| ¿Esto sirve en producción? | No, y esa es la conclusión. Ver la tabla de atributos sacrificados. |
| ¿Por qué no usaron un framework? | Cada capa añade latencia. El enunciado no pide concurrencia, persistencia ni seguridad; añadirlas sería sobreingeniería medible. |
| ¿Midieron bajo carga? | No. Es latencia en vacío, closed-loop con una petición en vuelo, y está declarado. Medir bajo carga es trabajo futuro. |

### Lo que NO hay que hacer en la demo

- **No corras un millón de iteraciones en vivo.** Tarda y pierdes a la audiencia.
- **No enseñes código.** Si alguien pregunta por las barreras de memoria, respóndelo hablando.
- **No presumas del 83 ns.** El número impresiona treinta segundos; el trade-off es lo que se
  califica. Presumir del número es exactamente el error que el trabajo denuncia.
