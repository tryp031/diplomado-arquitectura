# Guion del video — entregable 5 (máximo 5 minutos)

> El enunciado da a elegir: **video MP4 ≤ 5 min** para quien no asista al encuentro, o
> **demostración en vivo** para quien sí. §A es el guion del video; §B, el de la demo.
>
> **Cifras de la corrida oficial del 24/09/2026**, alcance B y D (ADR-007). Todos los números
> de este guion salen de `INFORME.md` §6 y §7; si el informe cambia, este guion cambia con él.

---

## Principio rector

**Cinco minutos no alcanzan para explicar el sistema. Alcanzan para defender una tesis.**

El error típico es narrar el recorrido: «primero probamos esto, luego aquello…». Eso consume
los cinco minutos sin llegar a ninguna afirmación. El video tiene **una** tesis:

> *El reto no estaba en bajar de 1 ms. Estaba en darse cuenta de que la métrica que se elige
> decide el veredicto —y de que hay una cola que ninguna arquitectura elimina.*

Todo lo que no sostenga esa frase, se corta. Incluido el código: **no se muestra código**.
Cinco minutos de un revisor no se gastan en leer C.

---

## A. Guion del video (4:40 de contenido, 20 s de margen)

### 0:00 – 0:30 · El planteamiento y el anticlímax

> **En pantalla:** el enunciado del reto, y debajo un único número: `14,9 µs`.

«El reto pedía un sistema que respondiera a un estímulo en menos de un milisegundo.

Lo primero que hicimos fue medirlo con la peor implementación que se nos ocurrió: un servidor
en Python, sobre TCP. Mediana: **casi quince microsegundos**. Sesenta y siete veces por debajo
del objetivo, con cuarenta líneas de código.

Así que el reto no era alcanzar el número. El número estaba alcanzado desde el principio. La
pregunta interesante era otra: **¿qué pasa si lo miramos bien?**»

### 0:30 – 1:10 · El diseño del experimento

> **En pantalla:** el diagrama de las dos pilas, B encima de D, apareciendo una a una.

«Montamos el mismo servicio sobre dos transportes muy distintos, midiendo los dos exactamente
igual.

La diferencia entre ellos es **cuánta pila de sistema atraviesa cada mensaje**. El primero usa
TCP: pila de red completa, dos llamadas al sistema operativo, copias por el kernel. El segundo
usa memoria física compartida y espera activa: **cero llamadas al sistema** en la ruta crítica.

Son los dos extremos del espectro razonable: la opción más portable y convencional, frente a la
más rápida posible dentro de una sola máquina.

Y una advertencia que preferimos decir nosotros antes de que la diga un revisor: entre esas dos
configuraciones cambian **dos cosas a la vez**, el transporte y el lenguaje. Así que la
diferencia que van a ver es el efecto conjunto de las dos. No afirmamos cuánto aporta cada una,
porque este experimento no lo puede separar.»

### 1:10 – 1:50 · Cómo se mide — la decisión central

> **En pantalla:** el diagrama de la frontera F1, con t0 y t1 marcados. Después, la tabla de
> las cinco fronteras posibles con sus valores (5 µs / 15 µs / 100 µs / 50 ms).

«Antes de medir hay que decidir **dónde se ponen las sondas**, y esa es la decisión
arquitectónica de verdad del ejercicio.

El mismo sistema, sin cambiar una línea, reporta entre 5 microsegundos y 50 milisegundos según
dónde empiece y termine el cronómetro.

Elegimos la frontera más desfavorable de las defendibles: desde justo antes de escribir hasta
tener la respuesta completa leída en el cliente. Es lo que percibe un consumidor real. Podríamos
haber reportado 5 microsegundos midiendo solo la llamada al sistema, y habría sido igualmente
cierto. No lo hicimos, y eso está documentado en un ADR **antes** de conocer los resultados.»

### 1:50 – 2:40 · Primer resultado: la métrica decide el veredicto

> **En pantalla:** la gráfica de percentiles, con la línea roja del milisegundo. Dejarla
> respirar: es la imagen del trabajo.

«Primer resultado, y es el que responde directamente a la pregunta del enunciado.

Por mediana, las dos configuraciones cumplen de sobra: sesenta y siete veces y doce mil veces
por debajo del milisegundo.

Pero miren la cola. De tres millones de mediciones, la versión en Python **se pasó del
milisegundo en ciento sesenta y cuatro**. La de memoria compartida, en ninguna.

Y ahora lo que de verdad aprendimos. Diez días antes habíamos corrido exactamente lo mismo:
mismo código, misma máquina, tres millones de muestras otra vez. Aquella vez la versión en
Python se pasó del milisegundo en **cero**. Tres días después, en ciento treinta y seis.

Una vez cumplió y dos veces no. Sin tocar una línea. La de memoria compartida: cero las tres.

Así que la pregunta «¿este sistema cumple el objetivo?» no tiene respuesta si uno mide una sola
vez. **Afirmar que una arquitectura incumple a partir de una corrida es afirmar algo sobre la
máquina, no sobre la arquitectura.**

Un informe basado en promedios habría dado las dos por buenas. **No es el sistema el que
determina el veredicto: es la métrica que uno elige, y cuántas veces se moleste en medir.**»

### 2:40 – 3:30 · Segundo resultado: el máximo depende de cuánto se mire

> **En pantalla:** la tabla de cuatro filas —10 mil, 100 mil, 1 millón, 3 millones— con el
> máximo creciendo. Que se vea que es **la misma corrida**.

«Segundo resultado, y es el más incómodo de los tres.

Esta tabla no compara sistemas. Es **una sola corrida**, leída con ventanas de observación cada
vez más grandes.

Con diez mil mediciones, el peor caso fueron ciento noventa y un microsegundos. Con cien mil,
novecientos noventa y uno: rozando el milisegundo. Con un millón, ya incumple. Con tres
millones, casi dieciséis milisegundos. **Ochenta y dos veces peor, y no cambió nada del
sistema.** Solo cambió cuánto miramos.

Dos consecuencias prácticas. La primera: un máximo sin decir sobre cuántas muestras se tomó no
significa nada. La segunda, y es la que duele: **una demostración de diez mil mensajes no habría
visto ni uno solo de los ciento sesenta y cuatro incumplimientos.** Habríamos presentado un sistema
que cumple, y habría sido falso sin que nadie mintiera.»

### 3:30 – 4:20 · Tercer resultado: lo que no se puede quitar

> **En pantalla:** `p50 = 83 ns` y debajo `máx = 41 792 ns`, con el factor `504×`.

«Y el tercero, que es el que más nos enseñó.

La versión de memoria compartida no hace **ni una sola llamada al sistema operativo**. Su
mediana son ochenta y tres nanosegundos. Y su máximo son cuarenta y dos microsegundos:
quinientas cuatro veces la mediana.

Esa cola no la pone el software, porque ya no queda software que quitar. La ponen el
planificador del sistema operativo y el hardware. Intentamos fijar el hilo a un núcleo, que es
la técnica estándar para acotarla, y descubrimos que **en esta plataforma no existe**: la
llamada devuelve "no soportado".

O sea que el sistema operativo y el hardware no son un detalle de despliegue. Son una
**restricción arquitectónica de primer orden**, y aquí la pudimos medir en vez de solo
enunciarla.»

### 4:20 – 4:40 · Cierre

> **En pantalla:** la tabla de atributos sacrificados por la variante Memoria compartida C.

«Para cerrar: la versión más rápida es también la peor arquitectura posible para casi cualquier
sistema real. No funciona entre máquinas, quema dos núcleos al cien por ciento sin hacer nada,
no es portable y no se puede depurar.

El umbral de un milisegundo lo cumple la opción más simple y más interoperable. Pasar de esa a
la extrema compra dos órdenes de magnitud que casi nadie necesita, al precio de todos los demás
atributos. Solo hay un caso en que se justifica: cuando el requisito es absoluto, cuando el
contrato dice *ninguna respuesta por encima de un milisegundo*. Y entonces la razón para
elegirla no es que sea rápida, sino que **saca de la ruta crítica las fuentes de
variabilidad**: sin llamadas al sistema operativo, no hay planificador que pueda robarle quince
milisegundos. Aunque cuidado: eliminar no es acotar. Su peor caso medido fue cuarenta y dos
microsegundos, quinientas cuatro veces su propia mediana, sin ejecutar una sola
llamada al sistema. Lo que podemos afirmar es que no observamos ninguna respuesta por encima
del milisegundo. No que no puedan ocurrir.

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

1. **14,9 µs** — el objetivo estaba cumplido desde la primera implementación ingenua
2. **0, 136 y 164** — el mismo código, la misma máquina, tres corridas en diez días
3. **82×** — cuánto crece el peor caso solo por mirar más, en la misma corrida
4. **504×** — la cola que queda cuando ya no hay software que quitar
5. **F1** — la frontera de medición se eligió y se documentó **antes** de ver los resultados

---

## B. Guion de la demo en vivo (encuentro del 29/09)

Si asistes, la demo sustituye al video. Cambia el formato, no la tesis.

### Preparación — antes de conectarte

- [ ] Binarios compilados: `cd reto-latencia-group2/sistema && make -C memoria-compartida-c`
- [ ] `python3 verificar.py` en verde: confirma que el experimento sigue siendo válido
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
4. **Cambia a la gráfica de percentiles.** Aquí está el discurso: por mediana las dos cumplen,
   por cola no. Es el momento de la presentación.
5. **Cierra con la tabla de la ventana de observación** (§7.3): el mismo dato, mirado más
   tiempo, da un peor caso 82 veces mayor. Y decí en voz alta que la corrida que acaban de ver
   —cien mil iteraciones— es justamente la que no habría detectado el problema.

### Preguntas que van a salir — y la respuesta corta

| Pregunta | Respuesta |
|---|---|
| ¿Por qué en loopback y no en red? | Está declarado como supuesto S3. Con red la latencia la domina la red y no se vería la diferencia entre transportes, que es lo que el estudio quiere medir. Es una limitación reconocida, no un descuido. |
| ¿El máximo de 15,8 ms no invalida el resultado? | Al contrario: **es** el resultado. Y depende de cuánto se mida: en esa misma corrida, con 10 000 muestras el máximo era 191 µs. Por eso se especifica en percentiles. |
| ¿Cuánto del 179× es el lenguaje y cuánto el transporte? | **No lo sabemos, y lo decimos en el informe.** Las dos configuraciones cambian ambas cosas a la vez. Separarlo exige un control que cambie una sola variable; está en trabajo futuro (§9, limitación 3). |
| ¿Por qué C y no Rust o Go? | No están instalados en el equipo, y con el tiempo disponible añadir un toolchain era riesgo sin beneficio para lo que el estudio quiere mostrar. |
| ¿La búsqueda en la tabla no contamina la medición? | Se midió aislada: **1,9 ns**, el 0,013 % del RTT de B (§6.3). Y se midió con el método correcto: restar dos corridas no servía, porque la varianza entre rondas era mayor que el efecto. |
| ¿Esto sirve en producción? | No, y esa es la conclusión. Ver la tabla de atributos sacrificados. |
| ¿Por qué no usaron un framework? | Cada capa añade latencia. El enunciado no pide concurrencia, persistencia ni seguridad; añadirlas sería sobreingeniería medible. |
| ¿Midieron bajo carga? | No. Es latencia en vacío, closed-loop con una petición en vuelo, y está declarado. Medir bajo carga es trabajo futuro. |

### Lo que NO hay que hacer en la demo

- **No corras un millón de iteraciones en vivo.** Tarda y pierdes a la audiencia.
- **No enseñes código.** Si alguien pregunta por las barreras de memoria, respóndelo hablando.
- **No presumas del 83 ns.** El número impresiona treinta segundos; el trade-off es lo que se
  califica. Presumir del número es exactamente el error que el trabajo denuncia.
