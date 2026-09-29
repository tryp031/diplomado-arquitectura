# Guion de sustentación y preguntas probables — Reto de Latencia Mínima

- **Autor:** Daniel Mazo · **Fecha:** 29/09/2026 · **Tipo:** `investigacion` (preparado con IA)
- **Para:** Freddy, Camilo y Danny. El profesor elige a cualquiera para exponer: los tres
  tenemos que poder contarlo solos.
- **Presentación que se usa:** `Aportes/danny/m1-presentacion-reto-latencia-v2-danny.html` (9 láminas).
- **Fuentes de las cifras:** la lámina de resultados y el PDF `informe_arquitectura_reto_latencia_minima_grupo2.pdf`
  (§10). Los dos usan la **misma corrida, la del 28/09** (1 × 1 M por variante).

---

## ⚠ Tres cosas que hay que saber antes de exponer

1. **La presentación y el informe usan la misma corrida (28/09), pero redondean distinto.**
   Para memoria compartida C, la presentación dice p50 **83 ns**, **184×** y **12 048×**; el
   informe PDF dice **80 ns**, **191×** y **12 500×**. En voz alta digan **83 ns**: el propio
   informe (§10.2) explica que el reloj solo puede dar 42, 83, 125 ns…, así que 80 ns es un
   redondeo, no un valor que se haya medido. Ver la pregunta 6.
2. **Hoy (29/09) se quitó el warmup del código** (ADR-012, todavía *Propuesta*: falta que
   Freddy y Camilo lo ratifiquen). Las cifras de la presentación y del informe **sí** se
   tomaron con warmup de 100 000. La nota «Reproducir» de la lámina de resultados trae
   `--warmup 100000`, y **ese comando ahora falla**. No lo lean en voz alta ni lo ejecuten
   en vivo. Ver la pregunta 12.
3. **Frases que NO se dicen:**
   - «Memoria compartida tiene el peor caso acotado» → **falso**: su máximo fue 17,6 µs (28/09)
     y 42 µs (24/09).
   - «Memoria compartida es mejor» → depende del atributo de calidad que se priorice.
   - «Memoria compartida nunca pasa de 1 ms» → lo correcto es «**no lo observamos**».

---

## Parte 1 — Guion (≈5 min, una idea por lámina)

| # | Lámina | Tiempo | Qué decir (la idea que no puede faltar) |
|---|---|---|---|
| 1 | Portada | 0:10 | «Somos el Group 2 y este es nuestro reto de latencia mínima.» Y pasar. |
| 2 | La solución que entregamos | 0:40 | Hicimos **dos soluciones** que responden exactamente lo mismo, más una **web** para operarlas. El servicio no es un eco: **clasifica una IP** como LOCAL, EXTERNO o DESCONOCIDO. Las dos soluciones comparten esa lógica, y el proyecto comprueba que clasifiquen igual. Por eso la comparación es justa. |
| 3 | Dos caminos para el mismo mensaje | 0:40 | Lo que cambia es **cuántas capas del sistema operativo atraviesa el mensaje**. TCP Python pasa por llamadas al sistema, la pila de red y el planificador, a la ida y a la vuelta. En memoria compartida C, un proceso escribe y el otro lee, sin el sistema operativo en medio. **Salvedad que decimos antes de que la pregunten:** cambian a la vez el camino y el lenguaje, así que la diferencia no se puede atribuir a una sola de las dos causas. |
| 4 | Un plano que controla, dos que se miden | 0:30 | La web **enciende y muestra, pero no cronometra**. Un navegador vive en milisegundos: si midiéramos desde ahí, estaríamos midiendo el navegador. |
| 5 | Dónde empieza y dónde para el cronómetro | 0:30 | El cronómetro arranca **justo antes de enviar** y para cuando **la respuesta llegó completa** (ida y vuelta). La conexión se abre una sola vez y queda fuera. Mismo reloj y mismo mensaje de 32 bytes en las dos soluciones. |
| 6 | Demostración | 1:00 | Llegar con la web **ya abierta** en `127.0.0.1:8080`: se encienden las dos, se manda un host de la lista y una IP a mano (usar `192.0.2.50`, nunca una IP real) y se lanza una medición corta. **Plan B:** si la demo falla, pasar a la siguiente lámina; ningún número sale de la demo. |
| 7 | Resultados | 0:40 | TCP Python: **15,3 µs** de mediana. Memoria compartida C: **83 ns**, es decir, **184×** más rápida por mediana. Hoy ninguna pasó de 1 ms, pero el 24/09, **con el mismo código**, TCP pasó de 1 ms **164 veces**. Y el máximo depende de cuántas muestras se miren: **por eso reportamos percentiles**. |
| 8 | Atributos de calidad comparados | 0:40 | **Esta es la lámina que demuestra que entendimos el módulo.** TCP gana en flexibilidad, concurrencia e interoperabilidad, y pierde en previsibilidad del peor caso. Memoria compartida gana en previsibilidad, y pierde en recursos (ocupa un núcleo entero), escalabilidad (un cliente a la vez) y flexibilidad (misma máquina, no corre en Windows nativo). |
| 9 | ¿Bajamos del milisegundo? | 0:30 | Por mediana, **las dos, y de sobra** (66× y 12 048× por debajo). Por la cola, TCP depende del día. Cerrar despacio: **«El milisegundo ya lo cumple la solución simple. La pregunta de arquitectura es qué estamos dispuestos a sacrificar para ir más rápido.»** Y parar ahí. |

**Si solo recuerdas tres cosas:** (1) las dos cumplen por mediana; (2) la cola de TCP depende
del estado del sistema operativo, no del código; (3) elegir entre las dos es un trade-off
de atributos de calidad, no un ganador.

---

## Parte 2 — Preguntas probables del profesor

### Sobre percentiles

**1. ¿Qué significa cada percentil?**
Se ordenan de menor a mayor el millón de tiempos medidos:

| Métrica | Qué dice | TCP Python | Memoria compartida C |
|---|---|---|---|
| **p50 (mediana)** | La mitad de los intercambios tardó esto o menos. Es el caso típico | 15,3 µs | 0,083 µs |
| **p99** | 99 de cada 100 tardaron esto o menos; **1 de cada 100** tardó más | 21,6 µs | 0,125 µs |
| **p99.9** | 999 de cada 1 000 tardaron esto o menos; **1 de cada 1 000** tardó más (en 1 M, unos 1 000 intercambios) | 31,2 µs | 0,167 µs |
| **máximo** | El peor intercambio de todos, **uno solo** | 622,5 µs | 17,6 µs |

Por ejemplo: «un p99.9 de 31 µs quiere decir que solo 1 de cada 1 000 intercambios tardó más de 31 µs».

**2. ¿Por qué percentiles y no el promedio?**
Porque el promedio **esconde la cola**, que es justo lo que importa en baja latencia.
Unos pocos intercambios de 15 ms mueven el promedio, pero no dicen cuántos fueron ni qué tan
malos. Con los percentiles se ve la forma de la distribución. Nuestra especificación
(`ESPEC-MEDICION.md` §3) **prohíbe usar el promedio como titular**.
*Complementario, si quiere ir más allá:* un usuario real hace muchas peticiones. Si una
página dispara 100 llamadas, la probabilidad de que al menos una caiga por encima del p99
es 1 − 0,99¹⁰⁰ ≈ **63 %**. La cola la sufre casi todo el mundo, no «el 1 %».

**3. ¿Por qué esos percentiles y no otros?**
- **p50**: para decir cuánto tarda un intercambio normal.
- **p99 y p99.9**: para ver la cola, es decir, qué tan malo es el caso raro pero frecuente.
- **máximo**: porque el enunciado habla de «menos de 1 ms», y lo que decide si alguna muestra
  se pasó es el peor caso.
- El análisis calcula además p90 y p99.99 (`ESPEC-MEDICION.md` §3). La lámina muestra los
  cuatro que cuentan la historia.

**4. ¿Por qué un millón de intercambios?**
Para que los percentiles altos tengan sentido estadístico. Con 1 M, el p99.99 todavía deja
100 muestras por encima. Con 10 000, el p99.9 dependería de 10 muestras. La lámina 7 lo
muestra: el máximo de TCP fue **46,5 µs** mirando 10 000 intercambios, **105 µs** mirando
100 000 y **622,5 µs** mirando el millón. **Un máximo no significa nada si no se dice sobre
cuántas muestras se tomó.**

**5. ¿Cómo calcularon los percentiles?**
Con **un solo script** (`analyze.py`) para las dos soluciones, así ninguna calcula sus
percentiles a su manera. El método es rango más cercano (*nearest-rank*), sin interpolar:
posición `ceil(p·n) − 1` en la lista ordenada.

### Sobre los resultados

**6. ¿Por qué la presentación dice 83 ns y el informe 80 ns?**
Es la misma corrida, la del 28/09. El reloj avanza en pasos de 41,67 ns, así que cada
medición de memoria compartida solo puede valer 42, 83, 125 ns…; el 71,1 % cayó en 83 ns. La
presentación da el valor exacto y el informe lo redondeó a dos cifras (80, 120, 170 ns). De
ahí salen también 184× frente a 191×.
- **Si citan 71 ns:** es la segunda forma de medir del informe, que cronometra lotes de 1 000
  intercambios y divide. Se reportan las dos cifras y ninguna es «la verdadera».
- **La corrida del 24/09** aparece en el informe (§10.4) solo para comparar: con el mismo
  código, TCP pasó de 1 ms 164 veces.

**7. ¿Por qué TCP pasó de 1 ms 164 veces un día y ninguna otro, con el mismo código?**
Porque la cola de TCP **depende del estado del sistema operativo**: planificador,
interrupciones y otros procesos. No depende del diseño del programa. El 24/09 la máquina
tenía carga 5,76 sobre 10 núcleos; el 28/09, 3,8. *Probable, no demostrado:* la correlación
con la carga encaja, pero no aislamos la causa.

**8. ¿Cumplen el objetivo de 1 ms?**
Por mediana, sí: TCP está 66× por debajo y memoria compartida 12 048×. Por la cola, TCP
depende del día (164 de 3 M sobre 1 ms el 24/09, ninguna el 28/09), y memoria compartida no
pasó en ninguna corrida. **Que no lo observáramos no quiere decir que no pueda pasar.**

**9. Entonces, ¿memoria compartida tiene el peor caso garantizado?**
**No.** Su máximo fue 17,6 µs, más de 200 veces su mediana, y eso sin ninguna llamada al
sistema. Esos picos los ponen las interrupciones, el hardware y la migración del hilo entre
núcleos (en macOS/arm64 no se puede fijar un hilo a un núcleo). Lo defendible es que
**sacó varias fuentes de variabilidad del camino, no todas**.
*Ojo con el informe §10.3:* dice que «importa que el peor caso esté acotado por diseño». Es
el **criterio** que se usa para evaluar, no una afirmación de que memoria compartida lo
cumpla. Si lo citan, esa es la respuesta.

### Sobre la metodología

**10. ¿Qué miden exactamente? ¿Por qué no solo la ida?**
El tiempo de ida y vuelta completo, desde antes de enviar hasta tener la respuesta entera
(frontera F1, ADR-001). No medimos solo la ida porque exigiría dos relojes sincronizados con
más precisión que la propia latencia, y eso entre procesos no se consigue. Además, **F1 es
la frontera más desfavorable de las defendibles**: si solo hubiéramos medido la llamada al
sistema, habríamos reportado unos 5 µs. Elegir la medida que nos perjudica le da
credibilidad al resultado.

**11. ¿Qué reloj usan y por qué importa?**
Un reloj monotónico con resolución real de **41,67 ns**. En el M4, `CLOCK_MONOTONIC` avanza a
saltos de 1 000 ns: con ese reloj, el 97,6 % de las muestras de memoria compartida (~83 ns)
habrían salido en **cero** (ADR-003). Regla: la granularidad del reloj debe ser al menos
10 veces menor que lo que se mide.

**12. ¿Hicieron warmup? El código no lo tiene.**
Las cifras del informe y de la presentación **sí** se tomaron con 100 000 intercambios de
calentamiento descartados, que sirven para calentar cachés y dejar que la CPU suba de
frecuencia. El 29/09 se quitó del código (ADR-012). Por eso una corrida nueva **no se compara**
con las del informe: sin warmup, la cola sube.

**13. ¿La web no afecta la medición?**
No. La web solo enciende las soluciones y muestra los resultados; el cronómetro vive en el
cliente de cada plano de datos. Además verificamos que medir desde la web no escribe en los
resultados oficiales.

**14. ¿Clasificar la IP no contamina la medición?**
Lo medimos por separado: **1,945 ns por llamada**. Primero intentamos restar dos corridas,
pero la variación entre rondas (±13 ns) era mayor que el efecto (~2 ns). Era ruido que parecía
señal, así que descartamos ese método (INFORME §6.3).

### Sobre las decisiones de diseño

**15. ¿Por qué Python y C?**
Python, porque es el candidato más lento que se nos ocurre: **si Python cumple, el umbral no
es el reto**. C, porque en Java el recolector de basura y el JIT meten pausas en la cola, y en
Python el intérprete cuesta más que la latencia que queremos medir. **Limitación declarada:**
como cambian a la vez el lenguaje y el camino, no podemos decir cuánto de los 184× se debe a
cada uno.

**16. ¿Por qué espera activa y no semáforos?**
Porque un semáforo o un *futex* vuelve a meter al planificador, que es justo lo que queremos
sacar del camino. El precio: **cada proceso ocupa un núcleo al 100 %** aunque no haya trabajo.

**17. ¿Qué es `TCP_NODELAY`?**
Desactiva el algoritmo de Nagle, que agrupa los mensajes pequeños antes de enviarlos. Si se
deja activo, aparecen picos de unos 40 ms. Es el error clásico de este ejercicio.

**18. En la lámina dicen «contenedores», pero el informe descarta contenedores.**
En la lámina, «contenedor» se usa en el sentido del **modelo C4**: una unidad que se ejecuta
por separado. No es Docker. Docker sí se descartó porque añade una red virtualizada, y eso
**sube** la latencia.

**19. ¿Por qué no usaron un broker como Kafka o un framework web?**
Porque no están en el alcance y van en contra del objetivo. Un broker añade un salto de red
y persistencia, varios órdenes de magnitud más de latencia. Un framework mete capas en la
ruta crítica. No hay nada que guardar, ni un requisito de disponibilidad que justifique
reintentos. **Justificar lo que no se construyó también es arquitectura.**

**20. ¿Cuál usarían en producción?**
**Depende del atributo de calidad que priorice el negocio.** Para casi cualquier servicio:
TCP, porque ya cumple el milisegundo y además da red, varios clientes y portabilidad. Para
memoria compartida hace falta un caso que exija **determinismo extremo en una sola máquina**
y que pueda pagar núcleos dedicados y código atado a la plataforma. *Complementario:* es el
caso de la comunicación entre procesos en sistemas de trading de baja latencia.
