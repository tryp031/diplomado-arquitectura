# Contenidos obligatorios M2 — P4: video «Módulo 2 - Seguridad Security» (transcripción)

> **Tipo:** `material-oficial` (Brightspace → Módulo 2 → «Contenidos obligatorios», presentación P4).
> **Fuente:** video de YouTube `MbUXkPdKaGw` (https://youtu.be/MbUXkPdKaGw), canal «Proyectos SB», 5 min 13 s,
> publicado el 9 jun 2026. Insertado en Brightspace como `youtube.com/embed/MbUXkPdKaGw`.
> **Captura:** 2026-10-04, panel «Mostrar transcripción» de YouTube abierto desde un navegador automatizado
> (41 segmentos). Es la **transcripción automática** de YouTube: puede tener errores de reconocimiento de voz.
> Se conservan las marcas de tiempo; el texto va tal cual, sin corregir.
> **Este archivo no se edita.** Las observaciones van al final, separadas y marcadas como anotación.

---

## Transcripción

**0:05** Hola, bienvenido y bienvenida a este nuevo video del diplomado en arquitectura de software. En este video
vamos a explorar un atributo de calidad crítico en cualquier sistema, la seguridad, y lo haremos paso a paso con
ejemplos y una metáfora que seguramente te ayudará a recordarlo con claridad.

**0:27** ¿Qué es la seguridad en sistemas? La seguridad es la capacidad que tiene un sistema para proteger los datos y la
información contra accesos no autorizados al mismo tiempo que permite el acceso a quienes sí están autorizados.

**0:42** Pero, ¿qué pasa cuando alguien intenta vulnerar esa protección? A eso lo llamamos un ataque. Puede tener
distintas formas, desde un intento de leer información sin permiso hasta querer modificarla o incluso bloquear el
acceso a usuarios legítimos, como sucede en los ataques de denegación de servicio. Para entender mejor cómo
proteger un sistema, es útil conocer los tres pilares fundamentales de la seguridad.

**1:05** Confidencialidad es la capacidad del sistema para mantener la información fuera del alcance de personas no
autorizadas. Por ejemplo, un hacker o pirata informático no debería poder acceder a tu declaración de impuestos
guardada en un sistema gubernamental.

**1:29** Integridad. Asegura que la información no sea alterada por personas no autorizadas. Imagina que la nota que te
asignó tu profesor se mantiene igual hasta que tú la ves. Eso es integridad.

**1:42** Disponibilidad significa que el sistema estará activo y disponible para los usuarios legítimos cuando lo
necesiten, como cuando compras un libro en línea y el sitio no se cae por un ataque.

**1:51** ¿Y qué hay de la privacidad? Muy relacionada con la seguridad está la privacidad que ha cobrado enorme
importancia en los últimos años. Las leyes como el Reglamento General de Protección de Datos, GDPR en Europa y otras
normativas similares en el mundo buscan proteger la información de identificación personal, también conocida como PI.

**2:21** Lograr la privacidad se trata de limitar el acceso a la información, lo que a su vez se trata de qué
información se debe limitar el acceso y a quién se debe permitir el acceso. La información que debe mantenerse
privada es la información de identificación personal PI.

**2:39** Pero, ¿qué es la PI exactamente? Según el Instituto Nacional de Estándares y Tecnología, se trata de cualquier
información que pueda identificar a una persona como nombre, número de seguro social, fecha de nacimiento,
información médica, educativa o financiera.

**3:01** Para ilustrarlo, veamos este escenario. Un empleado descontento, desde una ubicación remota, intenta modificar
la tabla de tasas de pago del sistema durante operaciones normales. El intento es detectado a tiempo, el sistema
registra la actividad y los datos correctos se restauran en un día. Este tipo de comportamiento muestra por qué la
seguridad no es solo una opción, sino una necesidad.

**3:29** Una manera útil de visualizar la seguridad en sistemas es compararla con la seguridad física de un edificio.
Las instalaciones seguras solo permiten un acceso limitado a ellas. Por ejemplo, mediante el uso de vallas y puntos
de control de seguridad. tienen medios para detectar intrusos, exigiendo que los visitantes legítimos lleven
insignias. Tienen mecanismos de disuasión como guardias armados, capacidad de reacción con cierre automático de
puertas y mecanismos de recuperación como copia de seguridad fuera del sitio. Lo mismo debe aplicarse al software.

**4:09** Cuatro tácticas para lograr seguridad. A partir de esta analogía se desprenden cuatro grandes categorías de
tácticas que puedes aplicar en tu arquitectura de software: Identificar comportamientos sospechosos o accesos
indebidos. Resistir, proteger el sistema para que no pueda ser vulnerado fácilmente. Reaccionar, tomar medidas cuando
ocurre una intrusión. recuperarse, restaurar el sistema a su estado seguro después de un ataque.

**4:41** ¿Quieres profundizar más? Para conocer en detalle cómo se aplica cada táctica de seguridad y explorar otras
tácticas asociadas a atributos como portabilidad o usabilidad, te invitamos a consultar la siguiente referencia
esencial. Además, puedes ampliar cada táctica desde cómo se aplica y su significado en la sección de recursos
complementarios.

**5:03** La presentación Tácticas Seguridad.

---

## Anotación (Danny + IA, 2026-10-04; no es del curso)

1. **«PI» es PII** (*Personally Identifiable Information*): el reconocimiento de voz se comió una letra. El deck
   y el resto del material usan PII. *(Seguro.)*
2. **La primera familia de tácticas se llama distinto.** El video dice «**Identificar** comportamientos
   sospechosos»; el deck `Tacticas-Seguridad.md` la llama «**Detectar** ataques». Es la misma familia. Usar
   «detectar» en los entregables, que es el término del deck y de Bass. *(Probable.)*
3. **La analogía del edificio trae una quinta idea:** «mecanismos de disuasión como guardias armados». No
   corresponde a ninguna de las cuatro familias que nombra el video a continuación; leerla como parte de
   *resistir*. *(Suposición.)*
4. **El escenario del empleado descontento** (3:01) es el único escenario de calidad de seguridad completo del
   material de M2. Sus 6 partes están desglosadas en el cuaderno de estudio, §7.
5. La «referencia esencial» que menciona (4:48) no se nombra en el audio; por el contexto, es el libro de Bass,
   Clements y Kazman que citan los decks. *(Suposición.)*
