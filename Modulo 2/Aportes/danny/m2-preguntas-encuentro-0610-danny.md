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
