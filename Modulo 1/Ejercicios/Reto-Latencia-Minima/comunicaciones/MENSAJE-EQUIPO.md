> ⚠️ **OBSOLETO (14/09/2026).** Cifras del eco puro y reparto de 4 personas.
> Usar [`MENSAJE-EQUIPO-14-09.md`](MENSAJE-EQUIPO-14-09.md).

# Mensaje al equipo (Group 2) — propuesta de enfoque y reparto

> **Para:** Freddy Aparicio · Bryan Brack · Camilo Céspedes
> **Estado:** borrador listo para enviar · redactado 10/09/2026
> **Objetivo del mensaje:** que el 11/09 estén asignadas las cuatro variantes y decidido el repo.
> Nada más. Las discusiones de diseño van después, no en el chat.
>
> ⚠️ **Para WhatsApp usa [`GRUPO-WHATSAPP.md`](GRUPO-WHATSAPP.md)**, que está escrito en formato
> de chat y lleva los resultados nuevos (control Bc, 3 M de muestras). Este archivo conserva
> la **versión larga para correo**, útil si el equipo prefiere ese canal; sus cifras son las
> de la corrida de 100 k del 08/09 y quedaron por debajo de la cola real.

---

## Versión corta — para WhatsApp / Teams (enviar esta)

```text
Hola equipo 👋 Avancé con el reto de latencia del M1 y les traigo una propuesta concreta para que la evaluemos.

EL PUNTO DE PARTIDA: probé un servidor de eco en TCP crudo sobre loopback, en Python. Resultado: p50 = 13 µs, o sea 75 veces por debajo del ms que pide el reto. Conclusión: bajar de 1 ms es trivial. Si los cuatro trabajamos en una sola implementación nos vamos a estorbar para conseguir un número que ya está conseguido.

LA PROPUESTA: en vez de una implementación, un estudio comparativo. Cada uno toma un transporte distinto, todos miden exactamente igual, y la entrega es la comparación:

  A · HTTP/REST sobre TCP     ~50–200 µs   (la línea base "así se hace normalmente")
  B · TCP crudo + NODELAY     ~20–50 µs    (ya está hecho, sirve de referencia)
  C · Unix socket o UDP       ~10–30 µs    (cuánto cuesta la pila de red)
  D · Memoria compartida      ~50 ns–1 µs  (el límite físico)

Por qué así: se divide en cuatro de verdad, y el informe deja de ser "logramos X µs" para ser "medimos cuatro arquitecturas bajo las mismas condiciones y estos son los trade-offs". Que es literalmente el tema del módulo.

YA ESTÁ LISTO Y PROBADO: el harness común (script de medición + análisis de percentiles + histogramas). Nadie arranca de cero: se copia el cliente de referencia y se cambia el transporte. Son unas 40 líneas por variante.

UN HALLAZGO QUE VALE LA PENA: en 100.000 mediciones, el máximo fue 2,2 ms. O sea que una muestra SÍ se pasó del objetivo, al doble. Eso es lo interesante del ejercicio y creo que ahí está la nota, no en el número bajo.

LO QUE NECESITO DE USTEDES (hoy o mañana 11/09, para no perder el fin de semana):
1. ¿Les suena el enfoque comparativo o prefieren implementación única? Es debatible, díganme.
2. ¿Quién toma A, C y D? Yo me quedo con la D, que es la más exótica. La B ya está.
3. ¿Montamos repo en GitHub? Si alguien ya tiene uno, mejor.

Dos cosas más, cortas:
- Escribí a la facilitadora para confirmar si la entrega es grupal o individual (el enunciado está escrito en singular pero la plataforma nos agrupó). Aviso apenas responda. El plan funciona igual en los dos casos.
- El encuentro del 15/09 a las 6 pm: si vamos con resultados preliminares podemos preguntarle al profe directamente cómo espera que midamos. ¿Quiénes pueden asistir?

Les paso el plan completo y el harness cuando me digan si vamos por ahí. Fecha de entrega objetivo: 27/09, para no quedar contra el cierre del 29.
```

---

## Si prefieren correo — versión con más contexto

**Asunto:** Reto de Latencia M1 — propuesta de enfoque y reparto de variantes (necesito respuesta el 11/09)

Hola Freddy, Bryan y Camilo:

Adelanté trabajo sobre la actividad del Módulo 1 y quiero someter a discusión el enfoque antes de
que nos repartamos nada, porque la decisión cambia bastante cómo trabajamos.

**El hallazgo que dispara la propuesta.** Implementé y medí un servidor de eco en TCP crudo sobre
loopback (Python, el candidato más lento que se me ocurrió): la mediana fue de **13,4 µs**, unas
**75 veces por debajo** del milisegundo que pide el reto. El objetivo del enunciado se cumple con
40 líneas de código. Eso significa que si los cuatro nos concentramos en «bajar de 1 ms», vamos a
invertir tres semanas en un problema que ya está resuelto — y un servidor de eco no se reparte
entre cuatro personas sin que se estorben.

**La propuesta: un estudio comparativo en vez de una implementación.** Cada uno toma un transporte
distinto del mismo sistema (mismo estímulo, misma respuesta, misma metodología de medición):

| Variante | Transporte | Latencia esperada | Qué demuestra |
|---|---|---|---|
| A | HTTP/1.1 (REST) sobre TCP loopback | 50–200 µs | La línea base «así se hace normalmente» |
| B | TCP crudo, `TCP_NODELAY`, conexión persistente | 20–50 µs | Cuánto cuesta el protocolo de aplicación |
| C | Unix domain socket o UDP loopback | 10–30 µs | Cuánto cuesta la pila de red del sistema operativo |
| D | Memoria compartida + ring buffer + busy-spin | 50 ns – 1 µs | El límite físico, y lo que cuesta llegar ahí |

La entrega deja de ser «logramos X µs» y pasa a ser: *medimos cuatro arquitecturas de comunicación
bajo condiciones idénticas, el rango fue de cuatro órdenes de magnitud, y estas son las razones
para elegir una u otra según lo que priorice el negocio*. El temario del módulo es exactamente eso:
atributos de calidad, restricciones, decisiones y trade-offs.

**No arrancamos de cero.** Ya está hecho y probado el harness común: el script de análisis
(percentiles p50/p99/p99.9/máximo, histogramas), el orquestador de corridas y la variante B como
implementación de referencia. Para las otras variantes se copia el cliente y se cambia el
transporte. El contrato entre variantes es un CSV con las muestras crudas — así ninguna calcula
sus propios percentiles y los cuatro resultados son comparables por construcción.

**El dato que creo que vale la nota.** En 100 000 mediciones el máximo fue **2 202 µs**: una
muestra se pasó del objetivo por más del doble, mientras la mediana estaba en 13 µs. Explicar por
qué pasa eso (planificador del sistema operativo, recolector de basura, migración entre núcleos,
interrupciones) vale más que cualquier optimización, y es justo lo que un promedio esconde.

**Lo que necesito decidir con ustedes — idealmente el 11/09:**

1. ¿Vamos por el estudio comparativo o prefieren implementación única? Está a discusión.
2. Reparto de A, C y D. Yo tomo la **D**; la B ya está lista y hace de referencia.
3. Repositorio Git compartido: ¿lo monto yo en GitHub o alguien ya tiene uno?
4. La ronda final de medición **tiene que correr en una sola máquina**, o los números no son
   comparables entre nosotros. ¿En cuál?
5. ¿Quiénes pueden asistir al encuentro del **15/09 a las 6 pm**? Conviene llegar con resultados
   preliminares y preguntarle al docente cómo espera que definamos la frontera de medición.

**Pendiente aparte:** escribí a la facilitadora para confirmar si la entrega es grupal o individual
— el enunciado está redactado en singular («cada estudiante elegirá herramientas…») pero la
plataforma nos asignó grupo. Les aviso apenas responda. El plan funciona en ambos escenarios: si
resulta individual, cada uno entrega el estudio completo citando su variante como aporte propio.

**Fechas:** entrega objetivo **27/09**, para no quedar contra el cierre del **29/09** — que además
cae el mismo día del segundo encuentro. Después del cierre no se califica.

Un saludo,
Daniel

---

## Notas de decisión (no enviar)

- **El riesgo real de este mensaje no es técnico, es de equipo.** Llegas con el enfoque definido,
  el harness construido y una variante ya medida. Eso puede leerse como «aquí está todo decidido,
  ejecuten». Por eso el mensaje pregunta el enfoque en primer lugar y dice explícitamente que es
  debatible. Si alguien propone implementación única, hay que escucharlo de verdad: el argumento
  a favor es que se parece más a lo que pidió el enunciado, y eso no es despreciable.
- **Se pide una sola cosa: el reparto.** Un mensaje que pide cinco decisiones a la vez no recibe
  ninguna. Las preguntas 3, 4 y 5 son secundarias y se pueden cerrar después.
- **No se manda el `PLAN-EQUIPO.md` completo de entrada.** Ocho secciones de documento asustan en
  un chat. Se manda cuando digan que sí al enfoque.
- **No se comparte la espec de medición todavía.** Sigue en borrador y congelarla es la decisión
  arquitectónica central; merece una conversación propia, no un archivo adjunto que nadie lee.
- Si al **12/09** no hay respuesta del equipo: seguir con la variante D en solitario. Dos variantes
  medidas (B y D) ya sostienen el estudio, y el resto se suma si aparece.
