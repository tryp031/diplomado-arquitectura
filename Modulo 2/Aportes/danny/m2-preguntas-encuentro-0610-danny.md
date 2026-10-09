# Preguntas para el encuentro del martes 06/10 — Reto 2

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny), con asistencia de IA |
| **Fecha** | 2026-10-04 |
| **Para** | Encuentro sincrónico M2, martes 06/10/2026, 6:00 pm |
| **Tipo** | `apunte` — preguntas propias; **no es material oficial** |
| **Fuente de las dudas** | `Material-Clase/Actividad-Reto2.md` (enunciado y dos rúbricas) · cuaderno de estudio §11 (gráfica del token bucket) |

> **Cómo abrir:** «Estamos en el diseño del Reto 2 y tenemos unas dudas del enunciado para no asumir.»
> **Si hay poco tiempo:** las preguntas **1, 2 y 3** desbloquean el diseño; la **8** toma 10 segundos.
> **Después:** anotar la respuesta tal cual, sin interpretarla, y pegarla en Claude empezando con
> «Respuestas del encuentro 06/10».

---

## 1. ¿Podemos hacer el reto en local, sin AWS? (la más importante)

**Pregunta:** «¿Es válido implementar el reto en nuestra máquina con Docker, respetando las restricciones con equivalentes locales (un límite de 15 peticiones por segundo en un proxy y máximo 10 contenedores)? ¿O es obligatorio desplegar en AWS?»

- **Por qué la hacemos:** el enunciado es condicional («**si se usa** API Gateway… **si se usan** procesadores como Docker, Lambda, EC2…»), pero la imagen de configuración es la consola de AWS y el diplomado es de *Cloud Computing*.
- **Qué cambia:** si dice que sí, seguimos en local. Si dice que no, hace falta una cuenta AWS personal esta misma semana.

**Respuesta:**

---

## 2. El script k6

**Pregunta:** «¿Cuándo y dónde publicarán el script k6? ¿Lo ejecutamos nosotros desde nuestra máquina durante la demo, o usted lo corre contra nuestro endpoint? ¿Cuántos eventos `Emergency` trae y en qué momento de la prueba?»

- **Por qué la hacemos:** el enunciado dice que «**se proporcionará**» y aún no está. El tiempo del correo vale la mitad de la nota (2.5 de 5) y sin el script no podemos medirlo.
- **Qué cambia:** si lo corre él, el sistema local necesita una URL pública (un túnel). La cantidad de `Emergency` define cuántos correos salen y si cumplimos el tiempo.

**Respuesta:**

---

## 3. ¿Un correo por cada `Emergency` o uno solo?

**Pregunta:** «Si en la prueba llegan varios eventos `Emergency`, ¿espera un correo por cada uno o basta con uno?»

- **Por qué la hacemos:** el enunciado dice «enviar un correo **en el momento en que se reciba** un evento `Emergency`». Con muchos eventos, Gmail puede frenar los envíos y el tiempo crece.
- **Qué cambia:** el diseño del envío. Uno por evento exige una cola que procese en paralelo; uno solo es mucho más simple.

**Respuesta:**

---

## 4. ¿Cómo se mide el tiempo del correo?

**Pregunta:** «El tiempo se mide desde el último envío de k6 hasta el correo. ¿Toma la hora en que llega a Gmail o la de nuestros logs? Y el objetivo dice menos de 30 segundos, pero la rúbrica corta en 15 y 45: ¿cuál es la meta?»

- **Por qué la hacemos:** el enunciado dice «entre el último envío realizado en k6 y la hora de envío del correo **y recepción** del mismo». Eso incluye la entrega de Gmail, que no controlamos. La rúbrica puntúa: < 15 s = 2.5 · 15–45 s = 1.5 · > 45 s = 0.5.
- **Qué cambia:** qué evidencia mostramos en la demo (log, bandeja de Gmail o ambos). Apuntamos a < 15 s.

**Respuesta:**

---

## 5. ¿Qué rúbrica califica?

**Pregunta:** «Hay dos rúbricas: la del PDF (2.5 de documentación + 2.5 de tiempo del correo) y la de Brightspace, con 5 criterios, entre ellos “Pruebas y análisis de resultados”. ¿Cuál se usa? ¿Qué espera en pruebas y análisis?»

- **Por qué la hacemos:** las dos son oficiales y no coinciden; los descriptores de la de Brightspace vienen vacíos.
- **Qué cambia:** poco, porque cubriremos las dos. Nos dice cuánto profundizar en las mediciones.

**Respuesta:**

---

## 6. El valor del *burst*

**Pregunta:** «Con 1000 peticiones en 30 segundos llegan unas 35 por segundo, más del doble del límite de 15. El enunciado dice que el burst queda “por defecto”, pero la imagen muestra 2000. ¿Qué valor debemos usar?»

- **Por qué la hacemos:** con un burst menor a ≈ 580 aparecen respuestas 429 y se incumple el «100 % de solicitudes procesadas» (gráfica del token bucket, cuaderno §11). En local nosotros elegimos ese número.
- **Qué cambia:** la configuración del proxy. Además, muestra que entendimos la restricción.

**Respuesta:**

---

## 7. Entrega individual o grupal

**Pregunta:** «En Brightspace la entrega aparece como individual. ¿Cada integrante sube la misma solución del grupo, o cada uno necesita su propia implementación? ¿La demo en vivo sería en el encuentro del 13/10?»

- **Por qué la hacemos:** la asignación está configurada individual (`grpid=0`). El enunciado pide demo en vivo a quienes asisten y video a quienes no.
- **Qué cambia:** cómo repartimos el trabajo con Camilo y Freddy, y si hay que preparar video.

**Respuesta:**

---

## 8. Fecha y hora de cierre

**Pregunta:** «¿Cuál es la fecha y hora exacta de cierre de la actividad M2? En la página no aparece.»

- **Por qué la hacemos:** después del cierre no se califica, sin excepciones.
- **Qué cambia:** el calendario. Hoy asumimos el 20/10, con margen hasta el 19/10.

**Respuesta:**

---

## 9. Evidencia del límite de 10 instancias (opcional)

**Pregunta:** «Para demostrar que no pasamos de 10 instancias simultáneas, ¿basta con mostrar la configuración, o quiere ver una métrica durante la prueba?»

- **Por qué la hacemos:** es una restricción dura del enunciado; en local hay que probarla, no solo afirmarla.
- **Qué cambia:** si agregamos un registro de instancias activas durante la corrida.

**Respuesta:**

---

## 10. Indicaciones del docente durante el encuentro del 06/10/2026

Estas notas recogen las indicaciones del docente compartidas por Freddy. Complementan las preguntas anteriores y precisan los criterios que debemos considerar en el diseño, las pruebas y la documentación del Reto 2.

| Campo | Valor |
|---|---|
| **Aporte añadido** | Freddy Aparicio, con asistencia de IA |
| **Fecha de incorporación** | 2026-10-09 |
| **Fuente** | Notas y aclaraciones de Freddy sobre el encuentro del 06/10/2026; no constituyen una transcripción literal ni sustituyen el material oficial |
| **Tipo** | `apunte` para las indicaciones reportadas; `investigacion` para la preparación complementaria con IA |
| **Estado** | Propuesta para revisión del equipo |

### 10.1. Despliegue y ubicación de los componentes

La documentación debe justificar **por qué se escoge una implementación en nube o en local**.

También debe describir:

- La ubicación geográfica de los componentes.
- La cercanía física entre los componentes que se comunican.
- La latencia observada entre ellos y su efecto sobre el tiempo de respuesta de la solución.

La ubicación y cercanía de los componentes deben considerarse como parte de las decisiones de arquitectura.

### 10.2. Carga de prueba y límite del backend

- La prueba debe enviar **1.000 peticiones**.
- No debe modificarse el script k6 en lo relacionado con las solicitudes.
- El **backend debe tener un límite máximo de 15 solicitudes por segundo**; puede configurarse un valor menor.
- Debe medirse cuánto tarda la carga completa de las 1.000 peticiones.
- Debe devolverse un **`200 OK` por cada petición**.

Ante una sobrecarga, la solución debe recibir las peticiones y permitir que su procesamiento ocurra posteriormente, por ejemplo mediante colas.

Debe prestarse atención a las respuestas **`429 Too Many Requests`** al superar el límite configurado. El diseño debe explicar cómo gestiona la carga sin perder mensajes.

### 10.3. Evidencia de procesamiento

La solución debe demostrar que:

1. Recibió los **1.000 mensajes**.
2. Procesó los **1.000 mensajes**.
3. Identificó y procesó el mensaje de tipo **`Emergency`**.

El docente solicitó que **cada mensaje quede registrado en un log cuando se procese**. Registrar únicamente su recepción no demuestra que haya terminado su procesamiento.

La respuesta HTTP y el log cumplen funciones distintas: debe responderse cada petición con `200 OK`, y los registros deben permitir verificar el procesamiento de los 1.000 mensajes.

### 10.4. Tiempo del evento de emergencia y del correo

Según las aclaraciones del encuentro reportadas por Freddy, el tiempo debe ser **menor de 16 segundos**, medido desde que **k6 envía el evento `Emergency` hasta que el correo llega al destinatario**.

Para demostrarlo, deben identificarse los siguientes momentos:

- Envío del evento de emergencia desde k6.
- Recepción del evento en la solución.
- Envío del correo.
- Recepción del correo en el destinatario.

La medición corresponde al evento de emergencia; no comienza con la última petición de toda la carga.

**Diferencia con el registro previo:** la pregunta 4 cita una rúbrica con máxima puntuación para menos de 15 segundos y una referencia al último envío de k6. Se conserva ese contenido como antecedente. Estas notas reportan menos de 16 segundos desde el envío del evento de emergencia; no modifican la rúbrica oficial. El equipo debe contrastar ambas referencias antes de cerrar el criterio de evaluación.

### 10.5. Máximo de instancias

La solución puede utilizar un máximo de **10 instancias**, por ejemplo contenedores Docker.

Este límite corresponde a instancias; no se interpreta como un límite de 10 hilos.

El diseño y las evidencias de ejecución deben permitir comprobar que no se supera el máximo establecido.

### 10.6. HTTPS obligatorio

La comunicación HTTP utilizada en la prueba debe realizarse mediante **HTTPS**.

La solución debe contemplar este requisito desde su diseño y demostrarlo durante la ejecución.

### 10.7. Documentación técnica de arquitectura

La documentación debe incluir:

- **Atributos de calidad priorizados:** identificar el más importante y explicar qué se priorizó, por ejemplo desempeño o escalabilidad.
- **Decisiones de arquitectura:** describir las decisiones adoptadas y su justificación.
- **Diagrama de arquitectura:** mostrar los componentes, sus relaciones y el flujo de las peticiones y del evento de emergencia.
- **Tácticas de arquitectura:** explicar los conceptos utilizados y cómo se aplican en la solución.

Para cada táctica debe señalarse **en qué componente o parte del diseño se aplica**, qué atributo de calidad favorece y cómo contribuye al cumplimiento del reto.

---

## 11. Decisión pendiente del equipo: momento de respuesta del `200 OK`

El docente exige un `200 OK` por cada petición y evidencia en logs de los 1.000 mensajes procesados. El momento de emitir la respuesta queda a criterio del equipo.

Debemos evaluar sobre la arquitectura propuesta:

> ¿Devolveremos `200 OK` después de recibir y almacenar de forma segura el mensaje en la cola, o después de completar su procesamiento?

La decisión debe explicar qué garantiza la respuesta y cómo se verificará el procesamiento posterior si se utiliza una cola.

### Propuesta de trazabilidad del equipo

Como propuesta del equipo, cada registro de procesamiento debería incluir:

- Identificador único del mensaje.
- Tipo de evento.
- Fecha y hora de recepción.
- Fecha y hora de finalización del procesamiento.
- Resultado del procesamiento.

Esto permitiría contar **1.000 mensajes únicos procesados**, detectar duplicados e identificar el evento de emergencia. Estos campos son una propuesta de implementación; la exigencia confirmada por Freddy es registrar cada mensaje al procesarlo.

---

## 12. Preparación para la exposición: conceptos y posibles preguntas

Esta sección es una guía de estudio del equipo, no una lista de preguntas confirmadas por el docente. Debemos poder explicar cómo funciona la solución, justificar sus decisiones y relacionar la teoría con los componentes implementados.

### 12.1. Teoría y temas técnicos que debemos reforzar

| Tema | Qué debemos comprender y explicar |
|---|---|
| **Atributos de calidad** | Diferencias entre desempeño, disponibilidad, escalabilidad, confiabilidad y seguridad. Cuáles priorizamos y qué compromisos asumimos. |
| **Tácticas de arquitectura** | Qué es una táctica, cómo se diferencia de un patrón y dónde se aplica en nuestra solución. |
| **Procesamiento síncrono y asíncrono** | Cuándo termina una petición HTTP y cuándo termina el procesamiento del mensaje. Qué garantiza nuestro `200 OK`. |
| **Colas y sobrecarga** | Productores, consumidores, acumulación de mensajes, capacidad de procesamiento y comportamiento cuando llegan más mensajes de los que podemos procesar. |
| **Limitación de solicitudes** | Diferencias entre tasa de solicitudes, concurrencia y capacidad de procesamiento. Dónde aplicamos el límite de 15 solicitudes por segundo. |
| **Rate y burst** | Qué representa cada parámetro y cómo influye en la aceptación o rechazo de peticiones. |
| **Escalabilidad y paralelismo** | Diferencias entre escalar horizontalmente, escalar verticalmente y ejecutar tareas en paralelo. Cómo respetamos el máximo de 10 instancias. |
| **HTTP y HTTPS** | Significado de `200`, `202`, `429` y errores `5xx`. Qué garantiza HTTPS y cómo se configura en la solución. |
| **Entrega y procesamiento de mensajes** | Riesgos de pérdida, duplicación y reintentos. Persistencia e idempotencia: cómo evitar que un mensaje repetido produzca efectos duplicados. |
| **Medición y trazabilidad** | Diferencias entre latencia y rendimiento. Cómo relacionamos los registros de k6, backend, procesamiento y correo mediante identificadores y tiempos. |
| **Ubicación de componentes** | Cómo afectan la distancia geográfica, la red y las dependencias externas a la latencia. |
| **Pruebas con k6** | Qué carga genera el script, qué métricas reporta y cómo interpretamos solicitudes exitosas, errores y duración de la prueba. |
| **Envío de correo** | Diferencia entre entregar el correo al servidor de envío y que llegue al destinatario. Qué evidencia utilizamos para cada momento. |

### 12.2. Posibles preguntas durante la exposición

1. ¿Por qué escogieron nube o local? ¿Qué cambiaría al desplegar la solución en otro entorno?
2. ¿Cuál es el atributo de calidad más importante y dónde se refleja en la arquitectura?
3. ¿Qué tácticas aplicaron y qué componente implementa cada una?
4. ¿Dónde se limita el backend a 15 solicitudes por segundo y cómo verificaron ese límite?
5. ¿Qué sucede si llegan más solicitudes de las que el backend puede procesar?
6. ¿Qué garantiza exactamente el `200 OK` en su implementación?
7. ¿Cómo demuestran que se procesaron 1.000 mensajes únicos y no solamente que se recibieron 1.000 peticiones?
8. ¿Qué ocurre si una instancia falla después de responder `200 OK` y antes de procesar el mensaje?
9. ¿Cómo manejan los mensajes duplicados, los reintentos y los fallos de procesamiento?
10. ¿Cómo evitan superar las 10 instancias y qué efecto tiene aumentar su número?
11. ¿Qué diferencia hay entre el tiempo de toda la carga y el tiempo del evento de emergencia?
12. ¿Cómo demuestran los menos de 16 segundos desde el envío del `Emergency` en k6 hasta la llegada del correo?
13. ¿Cómo comparan marcas de tiempo de componentes ubicados en máquinas diferentes?
14. ¿Qué ocurre si el envío o la entrega del correo se demora?
15. ¿Dónde termina la conexión HTTPS y cómo se protegen las comunicaciones posteriores?
16. ¿Cuál es el principal cuello de botella y qué evidencia respalda esa conclusión?

### 12.3. Evidencias que debemos poder mostrar

Las respuestas deben apoyarse en la implementación y en resultados observables:

- Diagrama de arquitectura y recorrido de una petición.
- Configuración del límite del backend y del máximo de instancias.
- Resultados de la ejecución del script k6.
- Logs que acrediten el procesamiento de los 1.000 mensajes únicos.
- Trazabilidad del evento `Emergency` y evidencia de recepción del correo.
- Justificación del momento en que se devuelve `200 OK`.
- Configuración y evidencia de uso de HTTPS.

Cada integrante debe poder conectar **requisito → decisión → componente → evidencia**, evitando limitar la explicación a definiciones teóricas.
