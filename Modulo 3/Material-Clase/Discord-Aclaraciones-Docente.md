# Aclaraciones del docente sobre el Reto 3 (Discord #modulo-3)

> **Tipo:** `aclaracion-docente`: palabras del docente (Diego Alejandro Rozo Vanegas) en el canal de Discord del
> curso, **#modulo-3**. No es el enunciado, pero lo interpreta el propio autor del reto.
> **Fuente:** captura del canal que aportó Danny el 2026-10-18. Abarca de agosto de 2025 a septiembre de 2026 y
> trae preguntas de estudiantes de **cohortes anteriores**. A la consulta del 17/09/2026 venía adjunto el
> documento `Consulta_interpretacion_diagrama_resiliencia.docx`, que Danny descargó del mismo canal.
> **Transcripción:** las respuestas del docente van **tal cual**, entre comillas. Las preguntas de los estudiantes
> van **resumidas** y sin datos personales.
> **Autoridad (CLAUDE.md):** está por debajo del enunciado y por encima de las imágenes de «Resultados esperados».
> Cuando la aclaración contradice esas imágenes, manda la aclaración.
> **Este archivo no se edita.** Las anotaciones van en el bloque final, marcado como tal.

---

## 1. El script del Reto 3 no cambió

- **17/09/2026.** Un estudiante pregunta si el script del Reto 3 se mantiene. Docente: «Si, se mantiene».
- El docente reenvió el mismo `reto3.js` en el canal el 21/08/2025, el 08/10/2025, el 09/12/2025 y el 03/02/2026.
  Es el que tenemos en `k6-script-profesor-reto3.js`.

## 2. El comentario del minuto 5

- **25/05/2026.** Un estudiante advierte que el comentario del minuto 5 del k6 dice «las primeras 10» mientras que
  el código usa `< 15`. Según el diagrama mostrado en la sesión, debería haber 5 errores para que el sistema se
  recupere. Docente: «Pudo ser un error de comentario pero funciona de esa manera».
  → **Valen los 15 errores del código.**

## 3. Cómo se cuentan los errores: el minuto anterior decide el actual

- **17/09/2026.** Un estudiante consulta cómo interpretar el diagrama de la sesión, con el documento adjunto que se
  transcribe en el §5. Docente:
  > «Se usa y se cuenta la cantidad de errores en el minuto 2-3 ( minuto que ya pasó )para responder o determinar
  > que respuesta doy en el minuto 3-4 ( minuto actual)
  > Entonces si durante el minuto 2-3 hubo 10 errores, durante el minuto 3-4 que es el actual, respondes nivel 3»

## 4. Saltos de nivel

- **18/09/2026.** Un estudiante pregunta si con 12 errores en el minuto anterior el sistema debe pasar directo a
  Nivel 3 o pasar primero por el Nivel 2. Docente:
  > «Se pasa de inmediato. El script está hecho para hacer 5 y 10 errores, entonces no va a pasar que sean 12 o un
  > valor aleatorio»
  >
  > «Por ende siempre vas a ver nivel 1-2-3-3-2-1»
- El estudiante dice que a ellos el sistema les salta de 1 a 3. Docente:
  > «Es el mismo script que está en el chat. No ha cambiado. Si te salta es problema del sistema , no del script»

## 5. El diagrama de la sesión (según el documento adjunto del 17/09/2026)

El estudiante reproduce así el diagrama de estados que el docente presentó en una sesión sincrónica (columnas:
ventana de tiempo, errores del cliente, nivel del servidor):

| Ventana de tiempo | Errores del cliente | Nivel del servidor |
|---|---|---|
| 0-1 | 0 errores | Nivel 1 |
| 1-2 | 5 errores | Nivel 1 |
| 2-3 | 10 errores | Nivel 2 |
| 3-4 | 5 errores | Nivel 3 |
| 4-5 | 0 errores | Nivel 2 |
| 5-6 | 0 errores | Nivel 1 |

Secuencia que el estudiante pide confirmar: «Nivel 1 → Nivel 1 → Nivel 2 → Nivel 3 → Nivel 2 → Nivel 1». La
respuesta del docente es la del §3.

---

## Anotaciones (Danny/IA, 2026-10-18; no son del curso)

1. **El diagrama no está en el material de Brightspace.** Lo buscamos en el enunciado, en el k6 y en los 6 decks
   capturados y no aparece. Según el mensaje del 25/05/2026 se mostró «en la sesión pasada», es decir, en un
   encuentro sincrónico.
2. **El diagrama y el §3 cuentan la misma regla:** el nivel de la ventana *m* depende de los errores de la ventana
   *m − 1* (≥ 10 → N3; ≥ 5 → N2; si no, N1). Las seis filas del §5 se cumplen sin excepción con esa regla. **Los
   umbrales 5 y 10 se aplican sobre el conteo del minuto anterior.** Las dos interpretaciones que plantea el
   estudiante son en realidad la misma.
3. **El diagrama no usa el patrón de errores del script.** El diagrama tiene 0 / 5 / 10 / 5 / 0 errores por minuto.
   El script tiene 5 / 0 / 15 / 0 / 15 / 0 / 0. Con el script, la regla pura del §3 da **1-2-1-3-1-3-1**: hay un
   salto de **3 a 1**. Eso **no** coincide con el «siempre vas a ver 1-2-3-3-2-1» del §4 ni con el texto del
   enunciado («desde Nivel 3 … transiciona a Nivel 2»).
4. **Contradicción del docente que queda abierta:** en el §4 acepta el salto inmediato al **degradar**, y después
   dice que «si te salta es problema del sistema». La lectura que concilia todo, y que adoptamos como supuesto en el
   diseño: **se degrada de golpe y se recupera de a un nivel por minuto**. Hay que confirmarlo el 27/10.
5. **«Minuto» quiere decir minuto de reloj.** El k6 espera al segundo 00 para arrancar justamente para alinear sus
   minutos con los del servidor.
